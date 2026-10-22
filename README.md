# Little sQrt v2.0.1

Production-oriented Python loudness measurement, normalization, and true-peak verification utility.

[![Python Version](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Version](https://img.shields.io/badge/version-2.0.1-orange.svg)](CHANGELOG.md)

---

## What it does

- **BS.1770-4 K-weighting**: Precise filter stages adhering to ITU-R BS.1770 specifications.
- **Loudness Gating**: Energy-domain absolute ($-70\text{ LUFS}$) and relative ($-10\text{ LU}$) gating.
- **Integrated LUFS**: Accurate broadcast-grade integrated loudness calculation.
- **Momentary & Short-Term**: $400\text{ ms}$ momentary and $3\text{ s}$ short-term loudness measurement.
- **EBU LRA**: EBU Tech 3342 loudness range distribution measurement.
- **True-Peak Detection**: $4\times$ interpolated true-peak measurement.
- **Multichannel Support**: Explicit channel-weight support for up to 8 channels.
- **Normalization & Limiting**: Loudness normalization to target LUFS with configurable true-peak ceiling.
- **High-Rate PCM**: Optional $8\times$ high-rate PCM output rendering.
- **Post-Render Verification**: Automated forensic verification report.
- **Batch Processing**: Multi-process batch execution with per-job error isolation.
- **Deterministic JSON Reports**: Detailed forensic reporting separating measurement, render actions, and verification.
- **Numba Acceleration**: Optional high-performance JIT execution.

---

## Installation

Clone the repository and install the required dependencies:

```bash
git clone [https://github.com/ljrseals-dev/Little-sQrt.git](https://github.com/ljrseals-dev/Little-sQrt.git)
cd Little-sQrt
python -m pip install -r requirements.txt
```
---
# Little sQrt v2.0.1

Production-oriented Python loudness normalization and verification utility.

## What it does

- BS.1770-style K-weighted loudness measurement
- 400 ms / 100 ms momentary block structure
- energy-domain absolute and relative loudness gating
- integrated LUFS
- short-term loudness
- EBU-style LRA distribution calculation
- 4x interpolated true-peak measurement
- explicit common multichannel weighting
- loudness normalization
- configurable true-peak ceiling
- optional 8x high-rate PCM rendering
- post-render verification
- JSON forensic report
- batch processing with per-job error isolation
- optional Numba acceleration

## Important terminology

`--no-8x` disables the output sample-rate conversion.

Without it, a 48 kHz source becomes 384 kHz and a 44.1 kHz source becomes 352.8 kHz. The project therefore calls this **8x high-rate PCM output** rather than claiming that every source/output is technically DXD.

The true-peak detector is separate from the 8x output SRC.

## Install

```bash
python -m pip install -r requirements.txt
```

Numba is optional:

```bash
python -m pip uninstall numba
```

The program falls back to NumPy/SciPy when Numba is unavailable.

## Examples

```bash
python littlesqrt.py in.wav out.wav --target -23 --bits 24
```

Podcast-style target:

```bash
python littlesqrt.py in.wav out.wav --target -16 --no-8x
```

No input high-pass:

```bash
python littlesqrt.py in.wav out.wav --hp 0 --target -23
```

Batch:

```bash
python littlesqrt.py --batch list.txt --target -23 --workers 8 --report report.json
```

`list.txt`:

```text
in/a.wav out/a.wav
in/b.wav out/b.wav
```

## Report semantics

The JSON report deliberately separates:

1. **measurement** — properties of the input after the optional high-pass, before normalization;
2. **render** — requested gain and true-peak ceiling actions;
3. **verification** — properties actually measured on the final rendered file.

If the requested loudness gain would violate the true-peak ceiling, the processor applies a final gain trim. The resulting `loudness_error_lu` therefore reports the actual deviation from target rather than hiding it.

## Validation status

This release is a production-oriented implementation, not a claim of independent standards certification.

Before broadcast certification, validate against the organization's reference BS.1770/EBU test vectors and the exact delivery-channel layout. In particular, verify:

- K-weighting reference vectors
- gated integrated loudness reference files
- LRA reference files
- true-peak intersample test signals
- mono, stereo and delivery-specific multichannel layouts
- 44.1/48/88.2/96/192 kHz
- PCM16/PCM24/float32 output
- long-form and short-form material

## Design rule

Measurement and rendering are separate concepts. The utility never uses an arbitrary pre-gain merely to make the meter look convenient.

The Python and Web implementations were cross-checked against a −20 dBFS
997 Hz stereo reference after v2.0.1 and agree within 0.05 LU.
