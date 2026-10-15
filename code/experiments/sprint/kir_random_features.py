"""Architecture-matched random controls for physical source pretraining.

Official constructor initialization, three label-independent seeds. No training.
Only pooled latent features are compared; random energy heads have no units.
"""

from __future__ import annotations

import json
import sys
import time

import numpy as np
import torch
from data import DATA, FEATURES, OUT, RAW, write_immutable
from kir_transfer import prepare


def main() -> None:
    sys.path.insert(0, str(RAW / "metl"))
    import metl
    from metl_check import CHECKPOINTS

    frame, sequence = prepare()
    sequences = [sequence] + [
        sequence[: r.position - 1] + r.alt + sequence[r.position :]
        for r in frame.itertuples()
    ]
    policy = {
        "hypothesis": "Does physical pretraining improve joint-gain selection beyond the same architecture with random weights?",
        "initialization": "Fresh officialMETLconstructor from exact sourcecheckpoint hyperparameters; never genericrecursive reset_parameters",
        "seeds": [1729, 2718, 3141],
        "architectures": ["global1d", "global3d"],
        "readout": "Same frozen native-site/region partitions, label budgets and validation-selected Ridge/logistic; report all random seeds rather than best testseed",
        "scope": "Matched architecture control, no new foundation training or experimental labels; inspected benchmark, exploratory attribution test",
    }
    write_immutable(
        DATA / "kir_random_control_policy.json", json.dumps(policy, indent=2) + "\n"
    )
    for family in ["global1d", "global3d"]:
        checkpoint = RAW / "metl/weights" / CHECKPOINTS[family]
        source = torch.load(checkpoint, map_location="cpu", weights_only=True)
        hyperparameters = source["hyper_parameters"]
        del source
        _, encoder = metl.get_from_checkpoint(str(checkpoint))
        encoded = encoder.encode_sequences(sequences)
        for seed in [1729, 2718, 3141]:
            key = family.replace("global", "random") + f"_s{seed}"
            path = FEATURES / f"kir_transfer_{key}.npz"
            if path.exists():
                continue
            torch.manual_seed(seed)
            start = time.perf_counter()
            torch.cuda.reset_peak_memory_stats()
            model = (
                metl.models.Model[hyperparameters["model_name"]]
                .cls(**hyperparameters)
                .eval()
                .to("cuda")
            )
            captured: list[torch.Tensor] = []

            def capture(_module, _inputs, output, captured=captured):
                captured.append(output.detach())

            hook = model.model.avg_pooling.register_forward_hook(capture)
            rows = []
            for i in range(0, len(encoded), 16):
                captured.clear()
                with torch.inference_mode():
                    batch = torch.tensor(encoded[i : i + 16], device="cuda")
                    (
                        model(batch, pdb_fn=str(RAW / "kir_af.pdb"))
                        if family == "global3d"
                        else model(batch)
                    )
                rows.append(captured[0].cpu().numpy())
            hook.remove()
            values = np.concatenate(rows)
            assert np.isfinite(values).all()
            np.savez_compressed(
                path, ids=frame.id.to_numpy(dtype=str), latent=values[1:] - values[:1]
            )
            torch.cuda.synchronize()
            result = {
                "method": key,
                "variants": len(frame),
                "seconds": time.perf_counter() - start,
                "peak_allocated_MiB": torch.cuda.max_memory_allocated() / 2**20,
                "seed": seed,
                "scope": "Random architecture control, no physical/function pretraining",
            }
            (OUT / f"kir_transfer_{key}_resources.json").write_text(
                json.dumps(result, indent=2) + "\n"
            )
            print(result, flush=True)
            del model
            torch.cuda.empty_cache()


if __name__ == "__main__":
    torch.set_num_threads(2)
    main()
