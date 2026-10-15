"""Small pretrained ESM-2 LoRA test versus physical augmentation.

Concrete question: does the physical increment survive a trainable pretrained
sequence baseline? Fixed protocol and grouped validation; no foundation training.
"""

from __future__ import annotations

import argparse
import copy
import json
import time

import numpy as np
import pandas as pd
import torch
from Bio import SeqIO
from data import AA, DATA, FEATURES, OUT, RAW, SEEDS, load_bk, load_vep, vep_split
from metrics import evaluate
from peft import LoraConfig, get_peft_model
from sklearn.preprocessing import StandardScaler
from torch import nn
from transformers import AutoModel, AutoTokenizer
from vep import lookups


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", choices=["bk", "avgfp", "pab1"], required=True)
    parser.add_argument("--modes", nargs="+", default=["lora"])
    parser.add_argument("--features", nargs="+", default=["none", "rosetta"])
    parser.add_argument("--seeds", type=int, nargs="+")
    parser.add_argument("--protocols", nargs="+", default=["site"])
    parser.add_argument("--train-limit", type=int, default=1000)
    parser.add_argument("--validation-limit", type=int, default=0)
    parser.add_argument("--epochs", type=int, default=40)
    args = parser.parse_args()
    assert torch.cuda.is_available()
    torch.set_num_threads(3)
    meta = json.loads((DATA / "esm2_35m_model.json").read_text())
    tokenizer = AutoTokenizer.from_pretrained(
        meta["name"], revision=meta["revision"], local_files_only=True
    )
    if args.dataset == "bk":
        frame = load_bk()
        sequence = str(next(SeqIO.parse(RAW / "6V3G.fasta", "fasta")).seq)
        offset = 1
        energy = 50 * np.tanh(frame.loc[:, "score":"rama_prepro"].to_numpy() / 50)
        local_path = FEATURES / "bk_evoef_r20.csv"
        energies = {"none": np.zeros((len(frame), 0)), "rosetta": energy}
        if local_path.exists():
            local = pd.read_csv(local_path).set_index("mutation").loc[frame.id]
            energies["local"] = 50 * np.tanh(
                local[
                    [c for c in local if c.startswith("state_difference_")]
                ].to_numpy()
                / 50
            )
        seeds = args.seeds if args.seeds is not None else list(range(5))
    else:
        frame, sequence, offset = load_vep(args.dataset)
        lookup, _, _ = lookups(args.dataset)
        energies = {"none": np.zeros((len(frame), 0))}
        for key in ["rosetta", "evoef_matched"]:
            if key not in lookup:
                continue
            values = []
            for parsed in frame.parsed:
                atomic = np.stack(
                    [
                        lookup[key][position - offset, AA.index(alt)]
                        for _, position, alt in parsed
                    ]
                )
                values.append(
                    np.concatenate([atomic.sum(0), atomic.min(0), atomic.max(0)])
                )
            energies[key] = np.stack(values)
        seeds = args.seeds if args.seeds is not None else SEEDS
    sequences, positions = [], []
    for parsed in frame.parsed:
        chars = list(sequence)
        sites = []
        for wt, position, alt in parsed:
            assert chars[position - offset] == wt
            chars[position - offset] = alt
            sites.append(position - offset)
        left = max(0, min(sites[0] - 511, len(chars) - 1022))
        sequences.append("".join(chars[left : left + 1022]))
        positions.append([site - left + 1 for site in sites])
    encoded = tokenizer(sequences, padding=True, return_tensors="pt")
    y = frame.target.to_numpy(dtype=np.float32)
    folder = OUT / "finetune"
    folder.mkdir(exist_ok=True)
    (folder / f"{args.dataset}_settings.json").write_text(
        json.dumps(
            {
                "args": vars(args),
                "model": meta,
                "LoRA": "query/value, r8, alpha16, dropout0.05",
                "learning_rates": {"adapter": 0.0001, "head": 0.001},
                "precision": "CUDA float16 autocast with gradient scaling",
                "validation": "MSE/patience8; train-only feature/target normalization; test after checkpoint selection",
            },
            indent=2,
        )
        + "\n"
    )
    for protocol in args.protocols:
        for seed in seeds:
            if args.dataset == "bk":
                parts = pd.read_csv(DATA / "bk_partitions.csv")
                selected = parts[(parts.protocol == protocol) & (parts.seed == seed)]
                split = frame.id.map(selected.set_index("id").split).to_numpy()
                split[frame.censored.to_numpy()] = "excluded"
            else:
                split = vep_split(frame, args.dataset, protocol, seed, offset)
            index = {
                label: np.flatnonzero(split == label)
                for label in ["train", "validation", "test"]
            }
            rng = np.random.RandomState(seed)
            index["train"] = rng.permutation(index["train"])[: args.train_limit]
            if args.validation_limit:
                index["validation"] = np.random.RandomState(seed + 314).permutation(
                    index["validation"]
                )[: args.validation_limit]
            center, scale = float(y[index["train"]].mean()), float(
                y[index["train"]].std()
            )
            targets = torch.tensor((y - center) / scale, device="cuda")
            for mode in args.modes:
                for physical in args.features:
                    case = f"{args.dataset}_{protocol}_{seed}_{mode}_{physical}_n{args.train_limit}_e{args.epochs}"
                    if args.validation_limit:
                        case += f"_val{args.validation_limit}"
                    destination = folder / f"{case}.json"
                    if destination.exists():
                        continue
                    torch.manual_seed(seed)
                    rng = np.random.RandomState(seed)
                    base = AutoModel.from_pretrained(
                        meta["name"],
                        revision=meta["revision"],
                        local_files_only=True,
                        add_pooling_layer=False,
                    )
                    if mode == "lora":
                        base = get_peft_model(
                            base,
                            LoraConfig(
                                r=8,
                                lora_alpha=16,
                                lora_dropout=0.05,
                                target_modules=["query", "value"],
                                bias="none",
                            ),
                        )
                    elif mode == "frozen":
                        base.requires_grad_(False)
                    else:
                        raise ValueError(mode)
                    base.to("cuda")
                    raw_energy = energies[physical]
                    if raw_energy.shape[1]:
                        standardized = (
                            StandardScaler()
                            .fit(raw_energy[index["train"]])
                            .transform(raw_energy)
                        )
                    else:
                        standardized = raw_energy
                    energy_tensor = torch.tensor(
                        standardized, dtype=torch.float32, device="cuda"
                    )
                    head = nn.Sequential(
                        nn.Linear(
                            2 * base.config.hidden_size + raw_energy.shape[1], 128
                        ),
                        nn.LeakyReLU(0.2),
                        nn.Dropout(0.2),
                        nn.Linear(128, 1),
                    ).to("cuda")
                    optimizer = torch.optim.AdamW(
                        [
                            {
                                "params": [
                                    p for p in base.parameters() if p.requires_grad
                                ],
                                "lr": 0.0001,
                            },
                            {"params": head.parameters(), "lr": 0.001},
                        ],
                        weight_decay=0.01,
                    )
                    scaler = torch.amp.GradScaler("cuda")
                    batch_size = 2 if args.dataset == "bk" else 16
                    accumulation = 8 if args.dataset == "bk" else 1

                    def predict_batch(
                        batch: np.ndarray,
                        base: nn.Module = base,
                        head: nn.Module = head,
                        energy_tensor: torch.Tensor = energy_tensor,
                    ) -> torch.Tensor:
                        inputs = {
                            key: value[batch].to("cuda")
                            for key, value in encoded.items()
                        }
                        with torch.autocast("cuda", dtype=torch.float16):
                            hidden = base(**inputs).last_hidden_state
                            mask = inputs["attention_mask"].clone()
                            mask[:, 0] = 0
                            for j, record in enumerate(batch):
                                mask[j, len(sequences[record]) + 1] = 0
                            pooled = (hidden * mask[:, :, None]).sum(1) / mask.sum(
                                1, keepdim=True
                            )
                            mutated = torch.stack(
                                [
                                    hidden[j, positions[record]].mean(0)
                                    for j, record in enumerate(batch)
                                ]
                            )
                            return (
                                head(
                                    torch.cat(
                                        [pooled, mutated, energy_tensor[batch]], dim=1
                                    )
                                )
                                .ravel()
                                .float()
                            )

                    def predict(
                        batch_indices: np.ndarray,
                        base: nn.Module = base,
                        head: nn.Module = head,
                        batch_size: int = batch_size,
                        scale: float = scale,
                        center: float = center,
                        predict_batch=predict_batch,
                    ) -> np.ndarray:
                        base.eval()
                        head.eval()
                        with torch.inference_mode():
                            output = [
                                predict_batch(batch_indices[i : i + batch_size])
                                .cpu()
                                .numpy()
                                for i in range(0, len(batch_indices), batch_size)
                            ]
                        return np.concatenate(output) * scale + center

                    best, best_epoch, saved = float("inf"), -1, None
                    history = []
                    torch.cuda.synchronize()
                    torch.cuda.reset_peak_memory_stats()
                    start = time.perf_counter()
                    for epoch in range(args.epochs):
                        base.train(mode == "lora")
                        head.train()
                        order = rng.permutation(index["train"])
                        optimizer.zero_grad(set_to_none=True)
                        losses = []
                        for step, i in enumerate(range(0, len(order), batch_size)):
                            batch = order[i : i + batch_size]
                            loss = torch.mean(
                                (predict_batch(batch) - targets[batch]) ** 2
                            )
                            scaler.scale(loss / accumulation).backward()
                            if (step + 1) % accumulation == 0 or i + batch_size >= len(
                                order
                            ):
                                scaler.unscale_(optimizer)
                                torch.nn.utils.clip_grad_norm_(
                                    [p for p in base.parameters() if p.requires_grad]
                                    + list(head.parameters()),
                                    1.0,
                                )
                                scaler.step(optimizer)
                                scaler.update()
                                optimizer.zero_grad(set_to_none=True)
                            losses.append(float(loss.detach()))
                        pval = predict(index["validation"])
                        loss_val = float(np.mean((pval - y[index["validation"]]) ** 2))
                        history.append(
                            {
                                "epoch": epoch,
                                "train_mse_normalized": float(np.mean(losses)),
                                "validation_mse": loss_val,
                            }
                        )
                        if np.isfinite(loss_val) and loss_val < best:
                            best, best_epoch = loss_val, epoch
                            # Save only trainable adapter weights plus regression head.
                            saved = (
                                {
                                    key: value.detach().cpu().clone()
                                    for key, value in base.state_dict().items()
                                    if "lora_" in key
                                },
                                copy.deepcopy(head.state_dict()),
                            )
                        print(case, epoch, round(loss_val, 4), flush=True)
                        if epoch - best_epoch >= 8:
                            break
                    assert saved is not None
                    base.load_state_dict(saved[0], strict=False)
                    head.load_state_dict(saved[1])
                    prediction = predict(index["test"])
                    torch.cuda.synchronize()
                    threshold = (
                        50.0
                        if args.dataset == "bk"
                        else (
                            0.1
                            if args.dataset == "avgfp"
                            else float(np.quantile(y[index["train"]], 0.9))
                        )
                    )
                    result = {
                        "case": case,
                        "dataset": args.dataset,
                        "protocol": protocol,
                        "seed": seed,
                        "mode": mode,
                        "physical": physical,
                        "train_n": len(index["train"]),
                        "validation_n": len(index["validation"]),
                        "development_labels_total": len(index["train"])
                        + len(index["validation"]),
                        "train_positive_examples": int(
                            (y[index["train"]] >= threshold).sum()
                        ),
                        "validation_positive_examples": int(
                            (y[index["validation"]] >= threshold).sum()
                        ),
                        "best_epoch": best_epoch,
                        "seconds": time.perf_counter() - start,
                        "peak_allocated_MiB": torch.cuda.max_memory_allocated() / 2**20,
                        "trainable_base_parameters": sum(
                            p.numel() for p in base.parameters() if p.requires_grad
                        ),
                        "head_parameters": sum(p.numel() for p in head.parameters()),
                        "positive": evaluate(y[index["test"]], prediction, threshold),
                        "history": history,
                    }
                    if args.dataset == "bk":
                        result["negative"] = evaluate(
                            y[index["test"]], prediction, -50, -1
                        )
                    destination.write_text(json.dumps(result, indent=2) + "\n")
                    pd.DataFrame(
                        {
                            "id": frame.id.to_numpy()[index["test"]],
                            "actual": y[index["test"]],
                            "predicted": prediction,
                        }
                    ).to_csv(folder / f"{case}_predictions.csv", index=False)
                    print("COMPLETED", case, result["positive"], flush=True)
                    del base, head, optimizer, saved, predict, predict_batch
                    torch.cuda.empty_cache()


if __name__ == "__main__":
    main()
