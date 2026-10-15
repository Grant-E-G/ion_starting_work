"""Published METL backbone adaptation on new grouped function partitions.

Source-only checkpoints; linear head/dropout0.5, AdamW/weight decay0.1,
head LR1e-3, phase2 ratio0.1, backbone freeze250 of500 epochs from released
finetune_avgfp_local arguments. Grouped validation/early stopping are new.
"""

from __future__ import annotations

import argparse
import copy
import json
import math
import sys
import time

import numpy as np
import pandas as pd
import torch
from data import OUT, RAW, SEEDS, load_vep, vep_split
from metrics import evaluate
from torch import nn

sys.path.insert(0, str(RAW / "metl"))
import metl

CHECKPOINTS = {
    "gfp": "METL-L-2M-3D-GFP-Hr4GNHws.pt",
    "binding": "METL-BIND-2M-3D-GB1-BINDING-Bo5wn2SG.pt",
    "binding_control": "METL-BIND-2M-3D-GB1-STANDARD-K6mw24Rg.pt",
}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", choices=["avgfp", "gb1"], required=True)
    parser.add_argument("--checkpoints", nargs="+", required=True)
    parser.add_argument("--seeds", nargs="+", type=int, default=SEEDS)
    parser.add_argument("--protocols", nargs="+", default=["site", "mutation"])
    parser.add_argument("--train-limit", type=int, default=1000)
    parser.add_argument("--validation-limit", type=int, default=0)
    parser.add_argument("--epochs", type=int, default=500)
    parser.add_argument("--unfreeze-epoch", type=int, default=250)
    parser.add_argument("--batch-size", type=int, default=128)
    parser.add_argument("--validation-stride", type=int, default=1)
    args = parser.parse_args()
    assert torch.cuda.is_available()
    torch.set_num_threads(3)
    folder = OUT / "metl_finetune"
    folder.mkdir(exist_ok=True)
    frame, sequence, offset = load_vep(args.dataset)
    pdb_name = "1gfl_cm.pdb" if args.dataset == "avgfp" else "2qmt_p.pdb"
    pdb = RAW / "metl/pdbs" / pdb_name
    y = frame.target.to_numpy(dtype=np.float32)
    sequences = []
    for parsed in frame.parsed:
        chars = list(sequence)
        for wt, position, alt in parsed:
            assert chars[position - offset] == wt
            chars[position - offset] = alt
        sequences.append("".join(chars))
    (folder / f"{args.dataset}_settings_n{args.train_limit}.json").write_text(
        json.dumps(
            {
                "args": vars(args),
                "training": "Published adaptation mechanism; source-only physical pretraining, new strict grouped partitions and train-only target normalization; not exact released split reproduction",
                "utility": "GFP WT-normalized log10 gain>0.1; GB1 verified WT enrichment gain>ln1.2",
                "published_arguments": "sources/sprint/raw/metl/finetune_avgfp_local.txt",
                "stopping": "Validation MSE; patience25 after at least25 unfrozen epochs; best checkpoint can be a frozen-head state",
            },
            indent=2,
        )
        + "\n"
    )
    for protocol in args.protocols:
        for seed in args.seeds:
            split = vep_split(frame, args.dataset, protocol, seed, offset)
            index = {
                key: np.flatnonzero(split == key)
                for key in ["train", "validation", "test"]
            }
            index["train"] = np.random.RandomState(seed).permutation(index["train"])[
                : args.train_limit
            ]
            if args.validation_limit:
                index["validation"] = np.random.RandomState(seed + 314).permutation(
                    index["validation"]
                )[: args.validation_limit]
            selected = np.concatenate(list(index.values()))
            # Encode only the experimental rows needed for this comparison.
            local = {int(row): i for i, row in enumerate(selected)}
            local_index = {
                key: np.array([local[int(row)] for row in rows])
                for key, rows in index.items()
            }
            center, spread = y[index["train"]].mean(), y[index["train"]].std()
            response = torch.tensor((y[selected] - center) / spread, device="cuda")
            for checkpoint_key in args.checkpoints:
                case = f"{args.dataset}_{protocol}_{seed}_{checkpoint_key}_n{args.train_limit}_e{args.epochs}_u{args.unfreeze_epoch}"
                if args.validation_stride != 1:
                    case += f"_v{args.validation_stride}"
                if args.validation_limit:
                    case += f"_val{args.validation_limit}"
                destination = folder / f"{case}.json"
                if destination.exists():
                    continue
                random_control = checkpoint_key.startswith("random_")
                key = checkpoint_key.removeprefix("random_")
                torch.manual_seed(seed)
                model, encoder = metl.get_from_checkpoint(
                    str(RAW / "metl/weights" / CHECKPOINTS[key])
                )
                if random_control:
                    # Recreate the source architecture with its own initialization.
                    # Resetting every child would incorrectly replace METL's
                    # uniform(-0.1,0.1) sequence embedding with N(0,1).
                    source = torch.load(
                        RAW / "metl/weights" / CHECKPOINTS[key],
                        map_location="cpu",
                        weights_only=True,
                    )
                    hyperparameters = source["hyper_parameters"]
                    torch.manual_seed(seed)
                    model = metl.models.Model[hyperparameters["model_name"]].cls(
                        **hyperparameters
                    )
                    del source
                model.requires_grad_(False)
                width = model.model.prediction.in_features
                # The published cutoff -1 removes the original attribute head.
                torch.manual_seed(seed)
                model.model.prediction = nn.Sequential(
                    nn.Dropout(0.5), nn.Linear(width, 1)
                )
                model.to("cuda")
                encoded = torch.tensor(
                    encoder.encode_sequences([sequences[i] for i in selected]),
                    device="cuda",
                )
                optimizer = torch.optim.AdamW(
                    [
                        {"params": model.model.prediction.parameters(), "lr": 0.001},
                        {
                            "params": [
                                p
                                for name, p in model.named_parameters()
                                if not name.startswith("model.prediction")
                            ],
                            "lr": 0.001,
                        },
                    ],
                    weight_decay=0.1,
                )
                best, best_epoch, state = float("inf"), -1, None
                history = []
                rng = np.random.RandomState(seed)
                torch.cuda.synchronize()
                torch.cuda.reset_peak_memory_stats()
                start = time.perf_counter()
                # The frozen body's validation representation is deterministic
                # in eval mode. Cache it without changing stochastic training
                # dropout; invalidate the cache when backbone updates begin.
                model.eval()
                head = model.model.prediction
                model.model.prediction = nn.Identity()
                # METL lazily caches RPE bucket indices on its first forward.
                # no_grad (not inference_mode) keeps those persistent tensors
                # valid for later backbone autograd after unfreezing.
                with torch.no_grad():
                    validation_hidden = torch.cat(
                        [
                            model(
                                encoded[
                                    local_index["validation"][i : i + args.batch_size]
                                ],
                                pdb_fn=str(pdb),
                            )
                            for i in range(
                                0, len(local_index["validation"]), args.batch_size
                            )
                        ]
                    )
                model.model.prediction = head
                with torch.inference_mode():
                    check_rows = local_index["validation"][
                        : min(8, len(local_index["validation"]))
                    ]
                    cache_error = float(
                        (
                            head(validation_hidden[: len(check_rows)])
                            - model(encoded[check_rows], pdb_fn=str(pdb))
                        )
                        .abs()
                        .max()
                    )
                assert cache_error < 1e-4
                model.requires_grad_(True)
                model(
                    encoded[local_index["train"][:2]], pdb_fn=str(pdb)
                ).sum().backward()
                model.zero_grad(set_to_none=True)
                model.requires_grad_(False)
                head.requires_grad_(True)

                def predict(
                    rows: np.ndarray,
                    model: nn.Module = model,
                    encoded: torch.Tensor = encoded,
                    spread: float = float(spread),
                    center: float = float(center),
                ) -> np.ndarray:
                    model.eval()
                    with torch.inference_mode():
                        output = [
                            model(
                                encoded[rows[i : i + args.batch_size]], pdb_fn=str(pdb)
                            )
                            .ravel()
                            .cpu()
                            .numpy()
                            for i in range(0, len(rows), args.batch_size)
                        ]
                    return np.concatenate(output) * spread + center

                for epoch in range(args.epochs):
                    if epoch == args.unfreeze_epoch:
                        model.requires_grad_(True)
                    phase2 = epoch >= args.unfreeze_epoch
                    fraction = (epoch - args.unfreeze_epoch) / max(
                        1, args.epochs - args.unfreeze_epoch
                    )
                    learning_rate = (
                        (0.0001 * 0.5 * (1 + math.cos(math.pi * fraction)))
                        if phase2
                        else 0.001
                        * min(1, (epoch + 1) / max(1, 0.01 * args.unfreeze_epoch))
                    )
                    for group in optimizer.param_groups:
                        group["lr"] = learning_rate
                    model.train()
                    order = rng.permutation(local_index["train"])
                    losses = []
                    for i in range(0, len(order), args.batch_size):
                        batch = order[i : i + args.batch_size]
                        optimizer.zero_grad(set_to_none=True)
                        prediction = model(encoded[batch], pdb_fn=str(pdb)).ravel()
                        loss = ((prediction - response[batch]) ** 2).mean()
                        loss.backward()
                        nn.utils.clip_grad_norm_(model.parameters(), 0.5)
                        optimizer.step()
                        losses.append(float(loss.detach()))
                    if (
                        phase2
                        and epoch % args.validation_stride
                        and epoch != args.epochs - 1
                    ):
                        continue
                    if not phase2:
                        model.eval()
                        with torch.inference_mode():
                            pv = (
                                head(validation_hidden).ravel().cpu().numpy() * spread
                                + center
                            )
                    else:
                        pv = predict(local_index["validation"])
                    value = float(np.mean((pv - y[index["validation"]]) ** 2))
                    history.append(
                        {
                            "epoch": epoch,
                            "train_normalized_MSE": float(np.mean(losses)),
                            "validation_MSE": value,
                            "learning_rate": learning_rate,
                        }
                    )
                    if value < best:
                        best, best_epoch, state = (
                            value,
                            epoch,
                            copy.deepcopy(model.state_dict()),
                        )
                    if epoch % 50 == 0:
                        print(case, epoch, round(value, 4), flush=True)
                    if epoch >= args.unfreeze_epoch + 25 and epoch - best_epoch >= 25:
                        break
                assert state is not None
                model.load_state_dict(state)
                prediction = predict(local_index["test"])
                torch.cuda.synchronize()
                threshold = 0.1 if args.dataset == "avgfp" else float(np.log(1.2))
                test = index["test"]
                singles = frame.num_mutations.to_numpy()[test] == 1
                result = {
                    "case": case,
                    "dataset": args.dataset,
                    "protocol": protocol,
                    "seed": seed,
                    "checkpoint": checkpoint_key,
                    "train_n": len(index["train"]),
                    "validation_n": len(index["validation"]),
                    "development_labels_total": len(index["train"])
                    + len(index["validation"]),
                    "best_epoch": best_epoch,
                    "epochs_executed": epoch + 1,
                    "seconds": time.perf_counter() - start,
                    "peak_allocated_MiB": torch.cuda.max_memory_allocated() / 2**20,
                    "parameters": sum(p.numel() for p in model.parameters()),
                    "all": evaluate(y[test], prediction, threshold),
                    "singles": evaluate(
                        y[test][singles], prediction[singles], threshold
                    ),
                    "history": history,
                    "train_positive_examples": int(
                        (y[index["train"]] >= threshold).sum()
                    ),
                    "frozen_validation_cache_max_error": cache_error,
                    "checkpoint_scope": (
                        "Random initialization control"
                        if random_control
                        else "Physical source pretraining only; no experimental target weights"
                    ),
                }
                destination.write_text(json.dumps(result, indent=2) + "\n")
                pd.DataFrame(
                    {
                        "id": frame.id.to_numpy()[test],
                        "actual": y[test],
                        "predicted": prediction,
                        "mutations": frame.num_mutations.to_numpy()[test],
                    }
                ).to_csv(folder / f"{case}_predictions.csv", index=False)
                print("COMPLETED", case, result["all"], flush=True)
                del model, optimizer, encoded, state, predict
                torch.cuda.empty_cache()


if __name__ == "__main__":
    main()
