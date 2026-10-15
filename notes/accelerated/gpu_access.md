# Verified local GPU execution

On 2026-10-14, running `nvidia-smi` through an escalated `exec_command`
exposed the working RTX 3080 Laptop GPU, NVIDIA driver 560.35.05. The default
sandbox hides the device nodes. The previous failure was sandbox isolation.
Separately, `/tmp/c5r-predict` uses CPU-only PyTorch and cannot execute CUDA.
No drivers, system CUDA installation, or existing benchmark environment changed.

An isolated `/tmp/c5r-gpu` environment uses Python 3.10.9, PyTorch
2.6.0+cu124 and Transformers 4.49.0. PyTorch publishes this CUDA combination in
its [official installation matrix](https://pytorch.org/get-started/previous-versions/).
The complete installed package pins are in
[requirements-gpu.txt](../../code/experiments/accelerated/requirements-gpu.txt).
[AGENTS.md](../../AGENTS.md) records the execution workaround and rebuild commands.

The actual [executable check](../../code/experiments/accelerated/gpu_check.py)
loaded the cached, pinned ESM-1v 650M checkpoint and performed 13 separate masked
forward passes on the 347-residue deposited 5ZIH sequence. Each pass used batch
size one, float32, TF32 disabled. CPU used four threads. GPU timing synchronized
CUDA and excluded model loading, model transfer, downloads and initial warmup.

| Measurement | Observed |
|---|---:|
| Parameters | 652,356,534 |
| CPU inference, 13 positions | 16.626 s |
| GPU inference, same positions | 1.248 s |
| GPU repeat | 1.200 s |
| Peak allocated GPU memory | 2,598.8 MiB |
| Peak reserved GPU memory | 2,680.0 MiB |
| CPU/GPU maximum absolute logit difference | 0.00001717 |
| Repeated GPU maximum absolute logit difference | 0 |

All logits were finite. Assertions checked CPU/GPU agreement with absolute
tolerance 0.001 and relative tolerance 0.0001, and GPU repeat agreement at
0.00001. The unused contact-regression head is absent from this checkpoint;
its initialization warning does not affect the masked-language-model logits.
The generated JSON receipt is `notes/accelerated/gpu_verification.json`.

This is approximately 13.3× faster inference on this particular workload and
demonstrates substantial available VRAM for this model. It does not establish
training capacity, BioEmu compatibility, or functional prediction accuracy.
The sequence is a deposited structure sequence, not an assertion about the
experimental ChrimsonR fusion construct. Earlier functional comparisons and
all OmpF artifacts remain unchanged.
