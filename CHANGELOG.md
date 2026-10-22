# Changelog

## 2.0.1 — 2026-10-21

### Fixed
- K-weighting stage-1 `a1` sign: shipped coefficient was `+1.69065929` at
  48 kHz because the numerator was `-2*(K*K-1)`. The BS.1770-4 published value
  is `−1.69065929`. This inverted the high-shelf pole pair and produced ~38 dB
  of shape error below ~1 kHz — the meter applied the wrong spectral weighting,
  not merely a gain offset. Corrected to `+2*(K*K-1)`.
- Removed dead `analyze()` call (`after_core`) in `process_one()`. It ran a
  full three-window K-weight pass plus a 4× true-peak resample per file and
  was never read.

### Added
- `test_k_weighting_matches_bs1770_48k`
- `test_integrated_lufs_minus20_dbfs_997hz`

### Removed
- The superseded v1.x `littlesqrt.py` (arbitrary `-12 dBFS` pre-gain, flat
  `Report` schema, same K-weighting bug). Eliminated from the tree to prevent
  import shadowing.

## 2.0.0 — 2026-09-15

### Added
- energy-domain integrated loudness gating
- explicit input measurement stage
- structured measurement/render/verification report
- post-render verification
- explicit channel weighting table
- short-file handling as undefined/empty measurements
- batch per-file exception isolation
- NaN/Inf input rejection
- optional 8x high-rate PCM output
- safety-scaling state in reports
- versioned CLI and documentation

### Changed
- removed arbitrary -12 dBFS pre-gain
- renamed DXD behavior to 8x high-rate PCM in documentation
- separated true-peak measurement from output SRC
- loudness gain is now calculated directly from measured integrated LUFS

### Known limitations
- The true-peak detector uses scipy's polyphase interpolation and requires
  independent validation against normative Annex 2 vectors for certification.
- LRA implementation is an engineering implementation of the EBU distribution
  method and should be checked against EBU Tech 3342 reference material.
- Delivery-specific channel layouts beyond the common 1–8 channel assumptions
  should be explicitly configured and tested.
