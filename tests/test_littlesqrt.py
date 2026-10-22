import math
import numpy as np
import soundfile as sf
from scipy.signal import sosfreqz
from littlesqrt import (
    integrated_lkfs, true_peak_dbtp, loudness_range,
    normalize_to_lufs, finite_status, k_weight_sos,
)


def test_silence_is_undefined():
    x = np.zeros((48000, 2), dtype=np.float64)
    assert integrated_lkfs(x, 48000) == float("-inf")


def test_lufs_gain_math():
    x = np.ones((48000, 1), dtype=np.float64) * 0.01
    l = integrated_lkfs(x, 48000)
    y, g = normalize_to_lufs(x, l, -23.0)
    assert math.isfinite(g)
    assert y.shape == x.shape


def test_true_peak_nonempty():
    x = np.zeros((1000, 2), dtype=np.float64)
    x[500, 0] = 0.5
    tp = true_peak_dbtp(x, 48000)
    assert math.isfinite(tp)
    assert tp < 0.0


def test_lra_silence():
    x = np.zeros((48000, 2), dtype=np.float64)
    assert loudness_range(x, 48000) == 0.0


def test_finite():
    assert finite_status(np.zeros((10, 2)))
    assert not finite_status(np.array([[np.nan, 0.0]]))


def test_roundtrip_file(tmp_path):
    x = np.random.default_rng(42).normal(0, 0.05, (48000, 2))
    p = tmp_path / "in.wav"
    q = tmp_path / "out.wav"
    sf.write(p, x, 48000, subtype="PCM_24")
    assert p.exists()
    data, sr = sf.read(p, always_2d=True, dtype="float64")
    sf.write(q, data, sr, subtype="PCM_24")
    assert q.exists()


# --------------------------------------------------------------------------
# v2.0.1 regression tests for the BS.1770-4 K-weighting stage-1 sign error.
# Both of these fail on pre-fix code by tens of dB.
# --------------------------------------------------------------------------

def test_k_weighting_matches_bs1770_48k():
    sos = k_weight_sos(48000)
    # BS.1770-4 Table 1 coefficients, 48 kHz
    assert abs(sos[0, 4] - (-1.69065929318241)) < 1e-6, \
        f"stage1 a1 = {sos[0, 4]!r}"
    assert abs(sos[1, 4] - (-1.99004745483398)) < 1e-6, \
        f"stage2 a1 = {sos[1, 4]!r}"
    # Combined K-weighting response at 1 kHz ≈ +0.683 dB
    _, h = sosfreqz(sos, worN=np.array([1000.0]), fs=48000)
    gain_db = 20.0 * np.log10(abs(h[0]))
    assert abs(gain_db - 0.683) < 0.02, f"1 kHz gain = {gain_db} dB"


def test_integrated_lufs_minus20_dbfs_997hz():
    sr = 48000
    t = np.arange(20 * sr) / sr
    mono = 0.1 * np.sin(2 * np.pi * 997.0 * t)     # -20 dBFS peak
    x = np.stack([mono, mono], axis=1)              # stereo
    measured = integrated_lkfs(x, sr)
    assert abs(measured - (-20.0)) < 0.05, f"got {measured} LUFS"
