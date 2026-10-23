"""Calibration tests for Little sQrt against closed-form references and an INDEPENDENT meter.
Nothing here uses the tool's own output as the reference.

Closed forms (BS.1770-4): a 997 Hz sine of peak A in each of N unity-weight channels measures
L = -0.691 + 10*log10( N * (A^2/2) * 1.1725 ), 1.1725 being the K-weighting power gain at 997 Hz
(10**0.0691). So stereo -20 dBFS peak -> -20.00 LUFS; mono 0 dBFS peak -> -3.01 LUFS.
"""
import math
import os
import sys
import time

import numpy as np
import pytest
from scipy import signal

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import littlesqrt as L


def sine(f, sr, secs, dbfs, ch=2, phase=0.0):
    t = np.arange(int(sr * secs)) / sr
    y = 10 ** (dbfs / 20) * np.sin(2 * np.pi * f * t + phase)
    return np.tile(y[:, None], (1, ch))


def independent_integrated_48k(x):
    """Reference meter written from the standard's published 48 kHz coefficients (BS.1770-4 Tables 1 and 2), not from littlesqrt."""
    b1 = [1.53512485958697, -2.69169618940638, 1.19839281085285]; a1 = [1.0, -1.69065929318241, 0.73248077421585]
    b2 = [1.0, -2.0, 1.0]; a2 = [1.0, -1.99004745483398, 0.99007225036621]
    y = signal.lfilter(b2, a2, signal.lfilter(b1, a1, x, axis=0), axis=0)
    blk, hop = 19200, 4800
    ms = np.array([np.mean(np.sum(y[s:s + blk] ** 2, axis=1)) for s in range(0, len(y) - blk + 1, hop)])
    lk = -0.691 + 10 * np.log10(np.maximum(ms, 1e-30))
    ms1 = ms[lk > -70]
    thr = -0.691 + 10 * np.log10(ms1.mean()) - 10
    ms2 = ms1[(-0.691 + 10 * np.log10(ms1)) > thr]
    return -0.691 + 10 * np.log10(ms2.mean())


def test_k_weighting_matches_published_coefficients_at_48k():
    b1 = [1.53512485958697, -2.69169618940638, 1.19839281085285]; a1 = [1.0, -1.69065929318241, 0.73248077421585]
    b2 = [1.0, -2.0, 1.0]; a2 = [1.0, -1.99004745483398, 0.99007225036621]
    w = np.geomspace(20, 20000, 400)
    _, ref = signal.freqz(np.polymul(b1, b2), np.polymul(a1, a2), worN=w, fs=48000)
    _, got = signal.sosfreqz(L.k_weight_sos(48000), worN=w, fs=48000)
    assert np.max(np.abs(20 * np.log10(np.abs(got) / np.abs(ref)))) < 0.01          # v2.0.0 was off by 38 dB (stage-1 a1 sign)


@pytest.mark.parametrize("sr", [44100, 48000, 96000, 192000])
def test_stereo_997hz_minus_20dbfs_reads_minus_20_lufs(sr):
    assert abs(L.integrated_lkfs(sine(997, sr, 10, -20.0), sr) - (-20.0)) < 0.05


def test_mono_full_scale_sine_reads_minus_3_01_lufs():
    assert abs(L.integrated_lkfs(sine(997, 48000, 10, 0.0, ch=1), 48000) - (-3.01)) < 0.03


def test_integrated_agrees_with_the_independent_meter_on_noise():
    rng = np.random.default_rng(3)
    x = signal.lfilter(*signal.butter(2, [150, 6000], btype="band", fs=48000), rng.standard_normal((48000 * 20, 2)) * 0.05, axis=0)
    assert abs(L.integrated_lkfs(x, 48000) - independent_integrated_48k(x)) < 0.02


def test_gating_ignores_silence_and_material_below_the_relative_gate():
    x = np.concatenate([sine(997, 48000, 10, -20), np.zeros((480000, 2))])
    assert abs(L.integrated_lkfs(x, 48000) + 20.0) < 0.15
    y = np.concatenate([sine(997, 48000, 10, -20), sine(997, 48000, 10, -50)])
    assert abs(L.integrated_lkfs(y, 48000) + 20.0) < 0.15


def test_true_peak_sees_the_intersample_peak():
    x = sine(12000, 48000, 1, 0.0, ch=1, phase=math.pi / 4)               # samples peak at -3.01 dBFS, waveform at 0 dBFS
    assert abs(L.sample_peak_dbfs(x) + 3.01) < 0.02
    assert abs(L.true_peak_dbtp(x, 48000)) < 0.3


def _six(idx):
    x = np.zeros((480000, 6)); x[:, idx] = sine(997, 48000, 10, -20, ch=1)[:, 0]; return x


def test_wav_layout_excludes_lfe_and_weights_surrounds():
    L.set_layout("wav")
    assert abs(L.integrated_lkfs(_six(2), 48000) + 23.01) < 0.05           # centre, unity
    assert L.integrated_lkfs(_six(3), 48000) == float("-inf")               # LFE (index 3) excluded
    for i in (4, 5):
        assert abs(L.integrated_lkfs(_six(i), 48000) + 21.52) < 0.05        # Ls / Rs: +1.5 dB


def test_lfe_last_layout_reproduces_the_old_assumption():
    L.set_layout("lfe-last")
    try:
        assert L.integrated_lkfs(_six(5), 48000) == float("-inf")
        assert abs(L.integrated_lkfs(_six(3), 48000) + 21.52) < 0.05
    finally:
        L.set_layout("wav")
    raises = False
    try:
        L.set_layout("nope")
    except ValueError:
        raises = True
    assert raises


def test_lra_uses_the_ebu_3342_relative_gate():
    parts = [(-23, 60), (-33, 30), (-48, 30), (-23, 40), (-62, 20)]
    x = np.concatenate([sine(300, 48000, s, db) * (1 + 0.3 * np.sin(np.arange(int(48000 * s)) / 48000 * 2 * np.pi * 0.7))[:, None] for db, s in parts])
    st = L.short_term_lkfs(x, 48000); st = st[np.isfinite(st) & (st > -70)]
    thr = 10 * np.log10(np.mean(10 ** (st / 10))) - 20.0                    # power mean, written here independently
    ref = np.percentile(st[st > thr], 95) - np.percentile(st[st > thr], 10)
    assert abs(L.loudness_range(x, 48000) - ref) < 0.01
    assert L.loudness_range(sine(997, 48000, 30, -20), 48000) < 0.1         # a steady tone has no range


def test_numpy_block_energy_matches_the_loop_and_is_fast():
    rng = np.random.default_rng(1)
    y = rng.standard_normal((48000 * 4, 6)); g = L.LAYOUTS["wav"][6]
    g = np.asarray(g, dtype=np.float64)
    a = L._weighted_block_ms_np(y, g, 48000, 4800)
    b = L._weighted_block_ms_loop(y[:48000 * 2], g, 48000, 4800)            # the loop is slow without numba, so compare on 2 s
    assert np.allclose(a[:len(b)], b, rtol=1e-10)
    big = rng.standard_normal((48000 * 60, 2))
    t = time.perf_counter(); L._weighted_block_ms_np(big, np.ones(2), 144000, 4800); assert time.perf_counter() - t < 2.0


def test_measurement_api_imports_without_soundfile():
    # soundfile is imported inside process_one only; the DSP/measurement functions must not need libsndfile
    assert "soundfile" not in open(L.__file__).read().split("def process_one")[0].replace("pip install numpy scipy soundfile", "")


def test_process_one_hits_the_target_by_an_independent_measurement(tmp_path):
    sf = pytest.importorskip("soundfile")
    rng = np.random.default_rng(0)
    x = signal.lfilter(*signal.butter(2, [200, 4000], btype="band", fs=48000), rng.standard_normal((48000 * 30, 2)), axis=0)
    x *= 10 ** (-26 / 20) / np.sqrt(np.mean(x ** 2))
    src, dst = str(tmp_path / "in.wav"), str(tmp_path / "out.wav")
    sf.write(src, x, 48000, subtype="PCM_24")
    rep = L.process_one(src, dst, -23.0, 24, 0.0, -1.0, False)               # no 8x: the published coefficients are for 48 kHz
    y, sr = sf.read(dst, always_2d=True)
    assert sr == 48000
    assert abs(independent_integrated_48k(y) + 23.0) < 0.1                    # TRUE loudness, not the tool's own reading
    assert L.true_peak_dbtp(y, sr) <= -1.0 + 0.05
    assert abs(rep.verification.loudness_error_lu) < 0.1
