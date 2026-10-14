"""Small published-method tests; no claim that compatibility or flexibility is function."""

from __future__ import annotations

import importlib.util
import json
import resource
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE.parent / "predictive"))
from data import AA, RAW, kir_reference, load_bedbrook, load_kir
from features import mapping, properties

CACHE = ROOT / "sources/accelerated/raw"
OUT = ROOT / "notes/accelerated"
# Wimley-White whole-residue water-to-octanol transfer, kcal/mol.
# NOT a translocon insertion scale or a Rosetta membrane potential.
WW = dict(
    zip(
        AA,
        [
            0.50,
            -0.02,
            3.64,
            3.63,
            -1.71,
            1.15,
            2.33,
            -1.12,
            2.80,
            -1.25,
            -0.67,
            0.85,
            0.14,
            0.77,
            1.81,
            0.46,
            0.25,
            -0.46,
            -2.09,
            -0.71,
        ],
    )
)


def template(name: str) -> tuple:
    from Bio.PDB import PDBParser, ShrakeRupley
    from Bio.SeqUtils import seq1

    model = PDBParser(QUIET=True).get_structure(name, RAW / f"{name}.pdb")[0]
    chain = next(
        c for c in model if len([r for r in c if r.id[0] == " " and "CA" in r]) > 100
    )
    residues = [
        r for r in chain if r.id[0] == " " and "CA" in r and seq1(r.resname) in AA
    ]
    # Remove other chains/ligands for an explicitly monomeric exposure approximation.
    ShrakeRupley(n_points=100).compute(chain, level="R")
    seq = "".join(seq1(r.resname) for r in residues)
    xyz = np.array([r["CA"].coord for r in residues])
    exposure = np.array([r.sasa for r in residues]) / 200.0
    return chain, residues, seq, xyz, exposure


def dynamics(xyz: np.ndarray) -> tuple[np.ndarray, dict]:
    from prody import GNM, calcSqFlucts

    start = time.perf_counter()
    model = GNM("template")
    model.buildKirchhoff(xyz, cutoff=10.0)
    model.calcModes(n_modes=None)
    matrix = model.getKirchhoff()
    eig = model.getEigvals()
    assert np.max(abs(matrix.sum(1))) < 1e-10
    assert np.all(eig > 0)
    fluctuations = calcSqFlucts(model)
    return fluctuations, {
        "seconds": time.perf_counter() - start,
        "modes": len(eig),
        "residues": len(xyz),
        "row_sum_max": float(np.max(abs(matrix.sum(1)))),
        "positive_min_eigenvalue": float(eig.min()),
        "scope": "uniform-spring monomer GNM; no mutation-dependent spring parameterization",
    }


def mpnn(
    name: str, chain_id: str, pdb_path: Path | None = None
) -> tuple[str, np.ndarray, dict]:
    import torch

    torch.set_num_threads(1)
    spec = importlib.util.spec_from_file_location(
        "official_mpnn", CACHE / "mpnn_utils.py"
    )
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    start = time.perf_counter()
    checkpoint = torch.load(CACHE / "mpnn.pt", map_location="cpu", weights_only=True)
    model = module.ProteinMPNN(
        num_letters=21,
        node_features=128,
        edge_features=128,
        hidden_dim=128,
        num_encoder_layers=3,
        num_decoder_layers=3,
        k_neighbors=checkpoint["num_edges"],
        augment_eps=0.0,
    )
    model.load_state_dict(checkpoint["model_state_dict"])
    model.eval()
    entry = module.parse_PDB(
        str(pdb_path or RAW / f"{name}.pdb"), input_chain_list=[chain_id]
    )[0]
    batch = module.tied_featurize([entry], torch.device("cpu"), None)
    x, _, mask, _, _, chain_encoding, *_rest = batch
    residue_idx = batch[12]
    with torch.inference_mode():
        scores = model.unconditional_probs(
            x, mask, residue_idx, chain_encoding
        ).numpy()[0]
        repeated = model.unconditional_probs(
            x, mask, residue_idx, chain_encoding
        ).numpy()[0]
    assert np.isfinite(scores).all()
    assert np.max(abs(np.exp(scores).sum(1) - 1)) < 1e-5
    assert np.max(abs(scores - repeated)) < 1e-4, {
        "max": float(np.max(abs(scores - repeated))),
        "positions": np.flatnonzero(abs(scores - repeated).max(1) > 1e-4).tolist(),
        "valid_max": float(abs(scores - repeated)[mask.numpy()[0] > 0].max()),
        "train": model.training,
    }
    return (
        entry["seq"],
        scores,
        {
            "seconds": time.perf_counter() - start,
            "positions": len(scores),
            "finite_backbone_positions": int(mask.sum()),
            "deterministic_repeat_maxdiff": float(np.max(abs(scores - repeated))),
            "parameters": sum(p.numel() for p in model.parameters()),
            "scope": "backbone-only unconditional log probabilities, no sequence-context epistasis, no lipids/cofactor",
        },
    )


def main() -> None:
    start = time.perf_counter()
    OUT.mkdir(exist_ok=True)
    resources: dict = {}
    bed, _ = load_bedbrook()
    kir, _ = load_kir()
    rows = []
    for name, ref in [
        ("3UG9", str(bed[bed.id == "C1C2"].iloc[0].sequence)),
        ("6M84", kir_reference()[1]),
    ]:
        t = time.perf_counter()
        chain, _residues, seq, xyz, exposure = template(name)
        fluct, dyn = dynamics(xyz)
        ms, logp, timing = mpnn(name, chain.id)
        match = mapping(ref, seq)
        mpmap = mapping(ref, ms)
        resources[name] = {
            "gnm": dyn,
            "proteinmpnn": timing,
            "all_components_seconds": time.perf_counter() - t,
            "identity": float(np.mean([ref[i] == seq[j] for i, j in match.items()])),
            "chain": chain.id,
        }
        if name == "6M84":
            for r in kir.drop_duplicates("id").itertuples():
                p = r.position - 1
                if p not in match or p not in mpmap:
                    values = [0.0] * 7
                else:
                    j = match[p]
                    k = mpmap[p]
                    delta = properties(r.alt) - properties(r.wt)
                    values = [
                        logp[k, (AA + "X").index(r.alt)]
                        - logp[k, (AA + "X").index(r.wt)],
                        exposure[j],
                        (WW[r.alt] - WW[r.wt]) * exposure[j],
                        fluct[j],
                        delta[0] * fluct[j],
                        delta[2] * fluct[j],
                        1.0,
                    ]
                rows.append(
                    dict(
                        dataset="kir",
                        id=r.id,
                        **dict(
                            zip(
                                [
                                    "mpnn",
                                    "exposure",
                                    "transfer",
                                    "gnm",
                                    "gnm_hydro",
                                    "gnm_volume",
                                    "mapped",
                                ],
                                values,
                            )
                        ),
                    )
                )
        else:
            aligned_ref = str(bed[bed.id == "C1C2"].iloc[0].seq)
            cols = [i for i, a in enumerate(aligned_ref) if a != "-"]
            for r in bed.itertuples():
                vals = []
                for i, j in match.items():
                    a = r.seq[cols[i]]
                    if a in AA and i in mpmap:
                        delta = properties(a) - properties(ref[i])
                        vals.append(
                            [
                                logp[mpmap[i], (AA + "X").index(a)]
                                - logp[mpmap[i], (AA + "X").index(ref[i])],
                                (WW[a] - WW[ref[i]]) * exposure[j],
                                delta[0] * fluct[j],
                                delta[2] * fluct[j],
                            ]
                        )
                v = np.mean(vals, axis=0)
                rows.append(
                    {
                        "dataset": "bedbrook",
                        "id": r.id,
                        "mpnn": v[0],
                        "transfer": v[1],
                        "gnm_hydro": v[2],
                        "gnm_volume": v[3],
                        "mapped": len(vals),
                    }
                )
    pd.DataFrame(rows).fillna(0).to_csv(OUT / "component_features.csv", index=False)
    resources["total_seconds"] = time.perf_counter() - start
    resources["peak_rss_MiB"] = (
        resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024
    )
    resources["device"] = "CPU"
    (OUT / "component_resources.json").write_text(
        json.dumps(resources, indent=2) + "\n"
    )
    print(json.dumps(resources, indent=2))


if __name__ == "__main__":
    main()
