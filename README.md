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
