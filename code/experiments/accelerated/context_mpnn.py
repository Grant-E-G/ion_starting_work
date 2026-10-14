"""Paired official MPNN variants: backbone, global membrane label, heteroatom context."""

from __future__ import annotations

import importlib.util
import json
import resource
import sys
import time

import numpy as np
import pandas as pd
import torch
from components import AA, CACHE, OUT, ROOT
from sklearn.metrics import roc_auc_score

sys.path.insert(0, str(ROOT / "code/experiments/predictive"))
from benchmark import precision_at_k


def load(name: str):
    spec = importlib.util.spec_from_file_location(name, CACHE / f"ligand_{name}.py")
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> None:
    torch.set_num_threads(4)
    data = load("data_utils")
    network = load("model_utils")
    policy = json.loads(
        (ROOT / "sources/accelerated/evaluation_policy.json").read_text()
    )["chrimson"]
    predictions = []
    resources = []
    for kind, filename in [
        ("protein_mpnn", "proteinmpnn_v_48_020.pt"),
        ("global_label_membrane_mpnn", "global_label_membrane_mpnn_v_48_020.pt"),
        ("ligand_mpnn", "ligandmpnn_v_32_010_25.pt"),
    ]:
        start = time.perf_counter()
        cp = torch.load(CACHE / filename, map_location="cpu", weights_only=True)
        context = cp.get("atom_context_num", 1)
        model = network.ProteinMPNN(
            node_features=128,
            edge_features=128,
            hidden_dim=128,
            num_encoder_layers=3,
            num_decoder_layers=3,
            k_neighbors=cp["num_edges"],
            device=torch.device("cpu"),
            atom_context_num=context,
            model_type=kind,
            ligand_mpnn_use_side_chain_context=False,
        )
        model.load_state_dict(cp["model_state_dict"])
        model.eval()
        protein, _, _, _icodes, _ = data.parse_PDB(
            str(CACHE / "5ZIH.pdb"),
            device=torch.device("cpu"),
            chains=["A"],
            parse_all_atoms=False,
            parse_atoms_with_zero_occupancy=False,
        )
        protein["chain_mask"] = torch.ones_like(protein["R_idx"])
        protein["membrane_per_residue_labels"] = torch.ones_like(
            protein["R_idx"], dtype=torch.long
        )
        features = data.featurize(
            protein,
            cutoff_for_score=8.0,
            use_atom_context=True,
            number_of_ligand_atoms=context,
            model_type=kind,
        )
        features["batch_size"] = 1
        features["symmetry_residues"] = [[]]
        probs = []
        t = time.perf_counter()
        for seed in range(1729, 1745):
            torch.manual_seed(seed)
            features["randn"] = torch.randn((1, features["mask"].shape[1]))
            with torch.inference_mode():
                p = model.score(features, use_sequence=False)["log_probs"].numpy()[0]
            probs.append(p)
        score = np.mean(probs, axis=0)
        numbering = protein["R_idx"].numpy().astype(int).tolist()
        for v in policy["panel"]:
            site = int(v[1:-1])
            if site not in numbering:
                continue
            j = numbering.index(site)
            prediction = (
                score[j, (AA + "X").index(v[-1])] - score[j, (AA + "X").index(v[0])]
            )
            predictions.append(
                {
                    "method": kind,
                    "id": v,
                    "prediction": prediction,
                    "prediction_sd": float(
                        np.std(
                            [
                                pp[j, (AA + "X").index(v[-1])]
                                - pp[j, (AA + "X").index(v[0])]
                                for pp in probs
                            ]
                        )
                    ),
                    "gain": v in policy["current_gains"],
                    "missing": v in policy["unpatchable_exclude"],
                }
            )
        resources.append(
            {
                "method": kind,
                "inference_seconds_16_seeds": time.perf_counter() - t,
                "total_seconds": time.perf_counter() - start,
                "parameters": sum(p.numel() for p in model.parameters()),
                "positions": len(numbering),
                "heteroatom_count": (
                    int(protein["Y_m"].sum()) if "Y_m" in protein else 0
                ),
                "seed_max_logprob_sd": float(np.std(probs, axis=0).max()),
                "peak_rss_MiB_cumulative": resource.getrusage(
                    resource.RUSAGE_SELF
                ).ru_maxrss
                / 1024,
                "scope": "monomer, backbone-only score (no sequence context); global label=1; ligand model sees parsed heteroatoms, does not simulate photochemistry",
            }
        )
        print(resources[-1], flush=True)
    f = pd.DataFrame(predictions)
    f.to_csv(OUT / "context_mpnn_predictions.csv", index=False)
    results = []
    for method, g in f.groupby("method"):
        g = g[~g.missing]
        results.append(
            {
                "method": method,
                "n": len(g),
                "positive": int(g.gain.sum()),
                "precision5": precision_at_k(
                    g.prediction.to_numpy(), g.gain.to_numpy(), 5
                ),
                "auc": roc_auc_score(g.gain, g.prediction),
            }
        )
    pd.DataFrame(results).to_csv(OUT / "context_mpnn_metrics.csv", index=False)
    (OUT / "context_mpnn_resources.json").write_text(
        json.dumps(resources, indent=2) + "\n"
    )
    print(pd.DataFrame(results).to_string(index=False))


if __name__ == "__main__":
    main()
