"""Modern executable Barethiya-style CNN/GCN physical-feature ablations.

PyTorch port of the published architecture, not bitwise TensorFlow-1 training
reproduction. Uses public energy/RMSF tables and strictly grouped partitions.
"""

from __future__ import annotations

import argparse
import copy
import json
import time
from typing import Any

import numpy as np
import pandas as pd
import torch
from Bio.PDB import PDBParser
from data import (
    AA,
    DATA,
    FEATURES,
    OUT,
    RAW,
    SEEDS,
    constants,
    load_vep,
    vep_split,
    write_immutable,
)
from metrics import evaluate
from torch import nn


def energy_components(table: pd.DataFrame) -> np.ndarray:
    """Predeclared eight groups; no labels or regression fits define energies."""
    columns = table.columns

    def summed(tokens: list[str]) -> np.ndarray:
        names = [c for c in columns if any(token in c for token in tokens)]
        return table[names].sum(axis=1).to_numpy()

    return np.column_stack(
        [
            summed(["vdwatt"]),
            summed(["vdwrep"]),
            summed(["electr"]),
            summed(["deslvP"]),
            summed(["deslvH"]),
            summed(["_hb"]),
            summed(["dunbrack", "aapropensity", "ramachandran"]),
            table.Total,
        ]
    )


def lookups(name: str) -> tuple[dict[str, np.ndarray], np.ndarray, np.ndarray]:
    info = constants()[name]
    sequence, offset = info["wt_aa"], info["wt_ofs"]
    base = RAW / f"VEP/data/{name}"
    physical = pd.read_csv(base / "ddG.tsv", sep="\t")
    dims = len(physical.columns) - 1
    assert dims == 8
    rosetta: np.ndarray = np.zeros((len(sequence), 20, dims), dtype=np.float32)
    present: np.ndarray = np.zeros((len(sequence), 20), dtype=bool)
    for row in physical.itertuples(index=False, name=None):
        token = row[-1]
        position, alt = int(token[1:-1]) - offset, AA.index(token[-1])
        rosetta[position, alt] = row[:-1]
        present[position, alt] = True
    rmsf = pd.read_csv(base / "rmsf.tsv", sep="\t").rmsf.to_numpy(dtype=np.float32)
    assert len(rmsf) == len(sequence)
    lookup = {
        "rosetta": rosetta,
        "mutation_indicator": np.ones((len(sequence), 20, 1), dtype=np.float32),
    }
    rng = np.random.RandomState(1729)
    lookup["rosetta_shuffled"] = np.stack([row[rng.permutation(20)] for row in rosetta])
    site_mean = np.zeros_like(rosetta)
    for site in range(len(sequence)):
        if present[site].any():
            site_mean[site] = rosetta[site, present[site]].mean(axis=0)
    lookup["rosetta_site_mean"] = site_mean
    aa_mean = np.zeros_like(rosetta)
    for amino in range(20):
        selected = present[:, amino]
        if selected.any():
            aa_mean[:, amino] = rosetta[selected, amino].mean(axis=0)
    lookup["rosetta_aa_mean"] = aa_mean
    lookup["rosetta_site_residual"] = rosetta - site_mean
    lookup["rosetta_aa_residual"] = rosetta - aa_mean
    path = FEATURES / f"{name}_evoef.csv"
    if path.exists():
        table = pd.read_csv(path)
        values = np.tanh(energy_components(table) / 50).astype(np.float32)
        evo = np.zeros((len(sequence), 20, values.shape[1]), dtype=np.float32)
        for token, value in zip(table.mutation, values, strict=True):
            evo[int(token[1:-1]) - offset, AA.index(token[-1])] = value
        lookup["evoef"] = evo
        control = FEATURES / f"{name}_evoef_self.csv"
        if control.exists():
            self_table = pd.read_csv(control)
            self_values = energy_components(self_table)
            self_map = {
                int(token[1:-1]) - offset: value
                for token, value in zip(self_table.mutation, self_values, strict=True)
            }
            matched = np.zeros_like(evo)
            raw_values = energy_components(table)
            for token, value in zip(table.mutation, raw_values, strict=True):
                site = int(token[1:-1]) - offset
                matched[site, AA.index(token[-1])] = np.tanh(
                    (value - self_map[site]) / 50
                )
            lookup["evoef_matched"] = matched
    for model in ["esm2_8m", "esm2_35m", "esm2_150m", "esm1v_650m"]:
        path = FEATURES / f"{name}_{model}.npz"
        if path.exists():
            with np.load(path) as file:
                logp = file["masked_logp"]
                wt_index = np.array([AA.index(a) for a in sequence])
                llr = logp - logp[np.arange(len(sequence)), wt_index, None]
                lookup[model] = llr[:, :, None].astype(np.float32)
    # Native residues always have zero mutation-effect energy/LLR/indicator.
    for values in lookup.values():
        values[np.arange(len(sequence)), [AA.index(a) for a in sequence]] = 0
    for token in physical.mutation:
        assert sequence[int(token[1:-1]) - offset] == token[0]
    return lookup, rmsf, present


def adjacency(name: str) -> np.ndarray:
    source = RAW / "VEP" / constants()[name]["pdb_fn"]
    chain = next(iter(PDBParser(QUIET=True).get_structure(name, source)[0]))
    residues = [r for r in chain if r.id[0] == " " and "CA" in r]
    coords = np.array(
        [r["CA"].coord if r.resname == "GLY" else r["CB"].coord for r in residues]
    )
    threshold = 6.0 if name == "bgl3" else 7.0
    adj = (
        np.linalg.norm(coords[:, None] - coords[None, :], axis=-1) < threshold
    ).astype(np.float32)
    np.fill_diagonal(adj, 0)
    adj /= np.maximum(adj.sum(axis=1, keepdims=True), 1)
    return adj


def integer_sequences(frame: pd.DataFrame, sequence: str, offset: int) -> np.ndarray:
    values = np.tile(
        np.array([AA.index(a) for a in sequence], dtype=np.int64), (len(frame), 1)
    )
    for i, parsed in enumerate(frame.parsed):
        for _, position, alt in parsed:
            values[i, position - offset] = AA.index(alt)
    return values


def build_model(
    architecture: str, length: int, dimensions: int, specification: dict | None = None
) -> nn.Module:
    width = 128 if specification is None else specification["filters"]
    number = (
        (3 if architecture == "cnn" else 5)
        if specification is None
        else specification["layers"]
    )
    kernel = 7 if specification is None else specification.get("kernel", 7)
    if architecture == "cnn":
        layers: list[nn.Module] = []
        for _ in range(number):
            layers.extend(
                [nn.Conv1d(dimensions, width, kernel_size=kernel), nn.LeakyReLU(0.2)]
            )
            dimensions = width
        model = nn.Sequential(
            *layers,
            nn.Flatten(),
            nn.Linear((length - number * (kernel - 1)) * width, 100),
            nn.LeakyReLU(0.2),
            nn.Dropout(0.2),
            nn.Linear(100, 1),
        )
    elif architecture == "gcn":
        graph_layers = nn.ModuleList()
        for _ in range(number):
            graph_layers.append(
                nn.ModuleList(
                    [
                        nn.Linear(dimensions, width),
                        nn.Linear(dimensions, width, bias=False),
                    ]
                )
            )
            dimensions = width
        model = nn.ModuleList(
            [
                graph_layers,
                nn.Sequential(
                    nn.Flatten(),
                    nn.Linear(length * width, 100),
                    nn.LeakyReLU(0.2),
                    nn.Dropout(0.2),
                    nn.Linear(100, 1),
                ),
            ]
        )
    else:
        raise ValueError(architecture)
    if specification is not None:
        for layer in model.modules():
            if isinstance(layer, (nn.Linear, nn.Conv1d)):
                nn.init.xavier_uniform_(layer.weight)
                if layer.bias is not None:
                    nn.init.zeros_(layer.bias)
        if architecture == "gcn":
            for center, neighbor in model[0]:
                for layer in [center, neighbor]:
                    bound = 1 / np.sqrt(layer.weight.numel())
                    nn.init.uniform_(layer.weight, -bound, bound)
    return model


def forward(
    model: nn.Module, architecture: str, x: torch.Tensor, adj: torch.Tensor
) -> torch.Tensor:
    if architecture == "cnn":
        return model(x.transpose(1, 2)).ravel()
    for center, neighbor in model[0]:
        x = torch.nn.functional.leaky_relu(
            center(x) + adj @ neighbor(x), negative_slope=0.2
        )
    return model[1](x).ravel()


def train_case(
    name: str,
    architecture: str,
    mode: str,
    protocol: str,
    seed: int,
    train_limit: int,
    epochs: int,
    batch_size: int,
    frame: pd.DataFrame,
    sequence: str,
    offset: int,
    ints: torch.Tensor,
    lookup: dict[str, np.ndarray],
    rmsf: np.ndarray,
    adj: torch.Tensor,
    published: bool = False,
    aaindex_mode: str = "full",
) -> dict[str, Any]:
    label = f"{name}_{architecture}_{mode}_{protocol}_{seed}_n{train_limit}_e{epochs}"
    if published:
        label += "_S2"
    if aaindex_mode == "mutation":
        label += "_maskedAA"
    if published and "esm" in mode:
        label += "_rawLLR"
    result_path = OUT / "vep" / f"{label}.json"
    if result_path.exists():
        return json.loads(result_path.read_text())
    split = vep_split(frame, name, protocol, seed, offset)
    rng = np.random.RandomState(seed)
    indices = {
        part: np.flatnonzero(split == part) for part in ["train", "validation", "test"]
    }
    if train_limit:
        indices["train"] = rng.permutation(indices["train"])[:train_limit]
    torch.manual_seed(seed)
    aaindex = np.load(RAW / "VEP/data/aaindex/pca-19_norm.npy")
    # Published table has 20 canonical-AA rows, without the stop-codon row.
    aaindex = torch.tensor(aaindex, dtype=torch.float32, device="cuda")
    assert aaindex.shape == (20, 19)
    identity = torch.eye(20, device="cuda")
    # Stop-codon channel is identically zero after missense-only filtering.
    zero_channel = torch.zeros((len(sequence), 1), device="cuda")
    physical = []
    if "rosetta" in mode:
        key = next(
            (
                candidate
                for candidate in [
                    "rosetta_shuffled",
                    "rosetta_site_residual",
                    "rosetta_aa_residual",
                    "rosetta_site_mean",
                    "rosetta_aa_mean",
                ]
                if candidate in mode
            ),
            "rosetta",
        )
        physical.append(lookup[key])
    if "evoef" in mode:
        physical.append(lookup["evoef_matched" if "matched" in mode else "evoef"])
    if "indicator" in mode:
        physical.append(lookup["mutation_indicator"])
    for model_name in ["esm2_8m", "esm2_35m", "esm2_150m", "esm1v_650m"]:
        if model_name in mode:
            # Fixed numerical rescaling; not fitted to function labels.
            physical.append(lookup[model_name] / (1 if published else 10))
    lookup_tensor = (
        torch.tensor(np.concatenate(physical, axis=2), device="cuda")
        if physical
        else None
    )
    rmsf_tensor = torch.tensor(rmsf[:, None], device="cuda") if "rmsf" in mode else None
    dimensions = (
        40
        + (lookup_tensor.shape[2] if lookup_tensor is not None else 0)
        + (1 if rmsf_tensor is not None else 0)
    )
    specification = (
        json.loads((DATA / "vep_s2_configs.json").read_text())["configurations"][
            f"{name}:{protocol}:{architecture}"
        ]
        if published
        else None
    )
    model = build_model(architecture, len(sequence), dimensions, specification).to(
        "cuda"
    )
    optimizer = torch.optim.Adam(
        model.parameters(),
        lr=0.001 if specification is None else specification["learning_rate"],
    )
    y = (frame.score if published else frame.target).to_numpy(dtype=np.float32)
    mean, std = float(y[indices["train"]].mean()), float(y[indices["train"]].std())
    if published:
        mean, std = 0.0, 1.0
    targets = torch.tensor((y - mean) / max(std, 1e-6), device="cuda")
    positions = torch.arange(len(sequence), device="cuda")
    native = torch.tensor([AA.index(a) for a in sequence], device="cuda")

    def predict_batch(index: np.ndarray) -> torch.Tensor:
        residues = ints[index]
        aa_features = aaindex[residues]
        if aaindex_mode == "mutation":
            # Released Barethiya encode.py passes wt_minus_mt_seqs to AAIndex,
            # with native positions set to the stop index. Repair its missing
            # zero stop row and canonical-AA indexing explicitly.
            aa_features = aa_features * (residues != native)[..., None]
        features = [
            identity[residues],
            zero_channel.expand(len(index), -1, -1),
            aa_features,
        ]
        if lookup_tensor is not None:
            features.append(lookup_tensor[positions, residues])
        if rmsf_tensor is not None:
            features.append(rmsf_tensor.expand(len(index), -1, -1))
        return forward(model, architecture, torch.cat(features, dim=2), adj)

    def predict(index: np.ndarray) -> np.ndarray:
        model.eval()
        with torch.inference_mode():
            parts = [
                predict_batch(index[i : i + batch_size]).cpu().numpy()
                for i in range(0, len(index), batch_size)
            ]
        return np.concatenate(parts) * std + mean

    best, state, best_epoch = float("inf"), None, 0
    history = []
    torch.cuda.synchronize()
    torch.cuda.reset_peak_memory_stats()
    start = time.perf_counter()
    for epoch in range(epochs):
        model.train()
        order = rng.permutation(indices["train"])
        train_losses = []
        effective_batch = (
            batch_size if specification is None else specification["batch_size"]
        )
        for i in range(0, len(order), effective_batch):
            effective = order[i : i + effective_batch]
            optimizer.zero_grad(set_to_none=True)
            for j in range(0, len(effective), batch_size):
                index = effective[j : j + batch_size]
                loss = torch.mean((predict_batch(index) - targets[index]) ** 2)
                (loss * (len(index) / len(effective))).backward()
                train_losses.append(float(loss.detach()))
            optimizer.step()
        pval = predict(indices["validation"])
        value = float(np.mean((pval - y[indices["validation"]]) ** 2))
        history.append(
            {
                "epoch": epoch,
                "train_normalized_mse": float(np.mean(train_losses)),
                "validation_mse": value,
            }
        )
        if value < best:
            best, best_epoch, state = value, epoch, copy.deepcopy(model.state_dict())
        if epoch - best_epoch >= (50 if published else 10):
            break
    assert state is not None
    model.load_state_dict(state)
    test = indices["test"]
    prediction = predict(test)
    torch.cuda.synchronize()
    threshold = 0.1 if name == "avgfp" else float(np.quantile(y[indices["train"]], 0.9))
    report_y = y[test].copy()
    if published and name == "avgfp":
        reference = float((frame.score - frame.target).median())
        report_y -= reference
        prediction -= reference
    values = evaluate(report_y, prediction, threshold)
    singles = frame.num_mutations.to_numpy()[test] == 1
    single_metrics = (
        evaluate(report_y[singles], prediction[singles], threshold)
        if singles.any()
        else {}
    )
    result = {
        "case": label,
        "dataset": name,
        "architecture": architecture,
        "features": mode,
        "protocol": protocol,
        "seed": seed,
        "train_limit": train_limit,
        "train_n": len(indices["train"]),
        "validation_n": len(indices["validation"]),
        "test_n": len(test),
        "best_epoch": best_epoch,
        "epochs_executed": len(history),
        "validation_mse": best,
        "gain_threshold": threshold,
        "gain_scope": (
            "WT-normalized log10 fluorescence >0.1"
            if name == "avgfp"
            else "Above training-set 90th percentile; NOT verified gain over WT"
        ),
        "seconds": time.perf_counter() - start,
        "peak_allocated_MiB": torch.cuda.max_memory_allocated() / 2**20,
        "parameters": sum(p.numel() for p in model.parameters()),
        "all": values,
        "singles": single_metrics,
        "history": history,
        "published_configuration": specification,
        "target_standardized": not published,
        "aaindex_mode": aaindex_mode,
        "llr_divisor": 1 if published else 10,
        "note": (
            "Published S2 architecture/batch/LR and released initializers; raw targets, patience50, new strict three-way grouped partitions; not an exact paper split reproduction"
            if published
            else "PyTorch architecture port, strict three-way grouped splits, normalized targets, Adam1e-3/patience10; not exact published training"
        ),
    }
    result_path.parent.mkdir(exist_ok=True)
    result_path.write_text(json.dumps(result, indent=2) + "\n")
    pd.DataFrame(
        {
            "id": frame.id.to_numpy()[test],
            "actual": report_y,
            "predicted": prediction,
            "mutations": frame.num_mutations.to_numpy()[test],
        }
    ).to_csv(OUT / "vep" / f"{label}_predictions.csv", index=False)
    print(
        label,
        "Pearson",
        round(values["pearson"], 3),
        "P20",
        round(values["P20"], 3),
        "s",
        round(result["seconds"], 1),
        flush=True,
    )
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--datasets", nargs="+", default=["pab1", "avgfp", "gb1"])
    parser.add_argument("--architectures", nargs="+", default=["cnn", "gcn"])
    parser.add_argument(
        "--features",
        nargs="+",
        default=["sequence", "rosetta_rmsf", "esm2_35m", "esm2_35m_rosetta_rmsf"],
    )
    parser.add_argument("--protocols", nargs="+", default=["site", "mutation"])
    parser.add_argument("--seeds", nargs="+", type=int, default=SEEDS)
    parser.add_argument("--train-limit", type=int, default=1000)
    parser.add_argument("--epochs", type=int, default=60)
    parser.add_argument("--batch-size", type=int, default=128)
    parser.add_argument("--published", action="store_true")
    parser.add_argument("--aaindex-mode", choices=["full", "mutation"], default="full")
    args = parser.parse_args()
    assert torch.cuda.is_available()
    torch.set_num_threads(3)
    torch.backends.cuda.matmul.allow_tf32 = False
    torch.backends.cudnn.allow_tf32 = False
    policy = vars(args)
    path = DATA / (
        "vep_run_"
        + __import__("hashlib")
        .sha256(json.dumps(policy, sort_keys=True).encode())
        .hexdigest()[:12]
        + ".json"
    )
    write_immutable(path, json.dumps(policy, indent=2) + "\n")
    for name in args.datasets:
        frame, sequence, offset = load_vep(name)
        ints = torch.tensor(integer_sequences(frame, sequence, offset), device="cuda")
        lookup, rmsf, _ = lookups(name)
        adj = torch.tensor(adjacency(name), device="cuda")
        for protocol in args.protocols:
            for seed in args.seeds:
                for architecture in args.architectures:
                    for mode in args.features:
                        train_case(
                            name,
                            architecture,
                            mode,
                            protocol,
                            seed,
                            args.train_limit,
                            args.epochs,
                            args.batch_size,
                            frame,
                            sequence,
                            offset,
                            ints,
                            lookup,
                            rmsf,
                            adj,
                            args.published,
                            args.aaindex_mode,
                        )
        del ints, adj
        torch.cuda.empty_cache()


if __name__ == "__main__":
    main()
