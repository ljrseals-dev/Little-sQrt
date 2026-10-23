## 2.0.2 (proposed)

### Fixed
- Multichannel: channel weights now follow the usual ITU/WAV order (`L R C LFE Ls Rs`, 7.1 `... Lb Rb`): LFE (index 3) excluded, surrounds weighted 1.41 (+1.5 dB). Before, the sixth channel was zeroed (an `Rs`), the LFE counted at full weight and surrounds were unweighted. `--layout lfe-last` keeps the old assumption (LFE is the final channel). The layout is recorded in the report.
- LRA: the relative gate is now 20 LU below the power mean of the absolute-gated short-term values (EBU Tech 3342). Before it was 20 LU below the 10th percentile, which let quiet passages inflate the range (25.2 LU instead of 10.2 LU on the synthetic test program).
- Without Numba the block-energy function was a pure-Python triple loop (6 s of stereo, one 3 s-window pass: 1.71 s). Replaced by a vectorized equivalent (13.5 ms, agrees to 3e-14 relative). Numba is still used when present.
- `soundfile` is imported inside `process_one`, so the measurement API works without libsndfile.

### Added
- `tests/test_calibration.py`: closed-form and independent-meter checks (K-weighting vs the published BS.1770-4 coefficients; 997 Hz stereo -20 dBFS = -20.00 LUFS at 44.1/48/96/192 kHz; mono 0 dBFS = -3.01; gating; intersample true peak; layouts; LRA; end-to-end normalization measured by an independent meter).
