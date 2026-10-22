# Little sQrt v2.0.1 Forensic Validation Plan

## Truth labels

- IMPLEMENTED: present in source and covered by unit tests or direct inspection.
- UNVERIFIED: implemented but requires external reference vectors.
- REQUIRES-HOST-TESTING: not applicable to this CLI-only build.
- BLOCKED: no reference vector or required environment available.

## Current matrix

| Area | Status |
|---|---|
| NaN/Inf rejection | IMPLEMENTED |
| Energy-domain loudness gating | IMPLEMENTED |
| Integrated LUFS | IMPLEMENTED — 997 Hz −20 dBFS stereo reference passing |
| Momentary loudness | UNVERIFIED |
| Short-term loudness | UNVERIFIED |
| EBU LRA | UNVERIFIED |
| 4x true peak | UNVERIFIED |
| Common channel weighting | UNVERIFIED |
| K-weighting coefficient derivation | IMPLEMENTED — BS.1770-4 Table 1 assertion |
| 8x output SRC | IMPLEMENTED |
| Post-render verification | IMPLEMENTED |
| Batch error isolation | IMPLEMENTED |
| JSON report | IMPLEMENTED |
| Plugin/DAW host behavior | REQUIRES-HOST-TESTING |

## Required reference tests

1. BS.1770 reference material at 48 kHz stereo.
2. EBU Tech 3342 LRA examples.
3. Inter-sample true-peak test tones.
4. Multichannel layouts with explicit LFE behavior.
5. Sample-rate sweep: 44.1, 48, 88.2, 96, 192 kHz.
6. Short files below 400 ms and 3 seconds.
7. Silence and near-silence.
8. Full-scale impulse and near-full-scale sine.

## Release gate

Do not describe this implementation as independently certified until the
reference-vector measurements have been run and recorded.

## Known limitations

- v2.0.0 shipped a K-weighting stage-1 a1 sign error (a1 = +1.69065929 at
  48 kHz instead of −1.69065929). Corrected in v2.0.1. The response now
  matches BS.1770-4 to within 0.01 dB across the audio band.
- v2.0.1 CLI and the browser port (`index.html` `kWeightSos`) were
  cross-checked on a −20 dBFS 997 Hz stereo reference and agree within 0.05 LU.
