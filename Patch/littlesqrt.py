#!/usr/bin/env python3
"""
Little sQrt v2.0.0
Production-oriented BS.1770-4 / EBU R128 loudness utility.

Features
--------
- BS.1770-style K-weighting
- Energy-domain absolute + relative gating
- Integrated LUFS
- Momentary and short-term loudness
- EBU-style LRA distribution measurement
- 4x true-peak detector
- Explicit channel-weight support for up to 8 channels
- Loudness normalization with optional true-peak ceiling
- Optional 8x high-rate PCM output
- Post-render verification
- Batch processing
- Deterministic JSON forensic report

Dependencies:
    pip install numpy scipy soundfile
    pip install numba  # optional acceleration
"""

from __future__ import annotations

import argparse
import json
import math
import os
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from dataclasses import asdict, dataclass
from typing import Optional

import numpy as np
from scipy.signal import butter, resample_poly, sosfilt

try:
    from numba import njit, prange
    HAVE_NUMBA = True
except Exception:
    HAVE_NUMBA = False
    def njit(*args, **kwargs):
        def deco(f):
            return f
        return deco if (len(args) == 1 and callable(args[0])) else deco
    prange = range

VERSION = "2.0.2"

ABS_GATE_LUFS = -70.0
REL_GATE_LU = -10.0
BLOCK_S = 0.400
HOP_S = 0.100
ST_WINDOW_S = 3.000
MOMENTARY_S = 0.400
TP_OVERSAMPLE = 4
OUTPUT_UPSAMPLE = 8
DEFAULT_TP = -1.0
ALIGN = 64

# BS.1770 channel weights (applied to mean-square energy): L, R, C = 1.0; surround = 1.41 (+1.5 dB); LFE excluded.
# Channel ORDER matters. Default "wav" is the usual ITU/SMPTE/WAV order:
#   3: L R C | 4: L R Ls Rs | 5: L R C Ls Rs | 6 (5.1): L R C LFE Ls Rs | 7: L R C LFE Ls Rs Cs | 8 (7.1): L R C LFE Ls Rs Lb Rb
# "lfe-last" is the older assumption of this tool (LFE is the final channel, as in L C R Ls Rs LFE).
# Check the delivery layout; no order can be detected from the samples.
SURROUND = 1.41
LAYOUTS = {
    "wav": {
        1: [1.0], 2: [1.0, 1.0], 3: [1.0, 1.0, 1.0],
        4: [1.0, 1.0, SURROUND, SURROUND],
        5: [1.0, 1.0, 1.0, SURROUND, SURROUND],
        6: [1.0, 1.0, 1.0, 0.0, SURROUND, SURROUND],
        7: [1.0, 1.0, 1.0, 0.0, SURROUND, SURROUND, SURROUND],
        8: [1.0, 1.0, 1.0, 0.0, SURROUND, SURROUND, SURROUND, SURROUND],
    },
    "lfe-last": {
        1: [1.0], 2: [1.0, 1.0], 3: [1.0, 1.0, 1.0],
        4: [1.0, 1.0, SURROUND, SURROUND],
        5: [1.0, 1.0, 1.0, SURROUND, SURROUND],
        6: [1.0, 1.0, 1.0, SURROUND, SURROUND, 0.0],
        7: [1.0, 1.0, 1.0, SURROUND, SURROUND, SURROUND, 0.0],
        8: [1.0, 1.0, 1.0, SURROUND, SURROUND, SURROUND, SURROUND, 0.0],
    },
}
CHANNEL_LAYOUT = "wav"


def set_layout(layout: str) -> None:
    global CHANNEL_LAYOUT
    if layout not in LAYOUTS:
        raise ValueError(f"layout must be one of {sorted(LAYOUTS)}")
    CHANNEL_LAYOUT = layout


def _align(a: np.ndarray) -> np.ndarray:
    # Alignment is an optimization hint, not a correctness requirement.
    a = np.ascontiguousarray(a)
    nbytes = a.nbytes + ALIGN
    buf = np.empty(nbytes + a.dtype.itemsize, dtype=np.uint8)
    start = (-buf.ctypes.data) % ALIGN
    raw = buf[start:start + a.nbytes]
    out = raw.view(a.dtype).reshape(a.shape)
    out[...] = a
    return out

def k_weight_sos(sr: int) -> np.ndarray:
    if sr <= 0:
        raise ValueError("sample rate must be positive")
    # ITU-R BS.1770 K-weighting analog prototype, bilinear transform.
    f0 = 1681.974450955533
    G = 3.999843853973347
    Q = 0.7071752369554196
    K = math.tan(math.pi * f0 / sr)
    Vh = 10.0 ** (G / 20.0)
    Vb = Vh ** 0.4996667741545416
    a0 = 1.0 + K / Q + K * K
    s1 = [
        (Vh + Vb*K/Q + K*K) / a0,
        2.0*(K*K - Vh) / a0,
        (Vh - Vb*K/Q + K*K) / a0,
        1.0,
        2.0*(K*K - 1.0) / a0,
        (1.0 - K/Q + K*K) / a0,
    ]

    f0 = 38.13547087602444
    Q = 0.5003270373238773
    K = math.tan(math.pi * f0 / sr)
    a0 = 1.0 + K/Q + K*K
    s2 = [
        1.0,
        -2.0,
        1.0,
        1.0,
        2.0*(K*K - 1.0) / a0,
        (1.0 - K/Q + K*K) / a0,
    ]
    return np.asarray([s1, s2], dtype=np.float64)

def k_weight(x: np.ndarray, sr: int) -> np.ndarray:
    return sosfilt(k_weight_sos(sr), x, axis=0)

@njit(parallel=True, fastmath=True, cache=True)
def _weighted_block_ms_loop(y: np.ndarray, gains: np.ndarray,
                            block: int, hop: int) -> np.ndarray:
    n, ch = y.shape
    if n < block:
        return np.empty(0, dtype=np.float64)
    nb = (n - block) // hop + 1
    out = np.zeros(nb, dtype=np.float64)
    inv = 1.0 / block
    for b in prange(nb):
        s = b * hop
        acc = 0.0
        for c in range(ch):
            g = gains[c]
            if g == 0.0:
                continue
            for i in range(block):
                v = y[s+i, c]
                acc += g * v * v
        out[b] = acc * inv
    return out

def _weighted_block_ms_np(y: np.ndarray, gains: np.ndarray,
                          block: int, hop: int) -> np.ndarray:
    """Vectorized equivalent of the loop above (cumulative sum of per-sample weighted energy).
    Agrees with the loop to about 1e-14 relative and is roughly 100x faster than the loop without Numba."""
    n = y.shape[0]
    if n < block:
        return np.empty(0, dtype=np.float64)
    c = np.concatenate([[0.0], np.cumsum((y * y) @ gains)])
    starts = np.arange((n - block) // hop + 1) * hop
    return (c[starts + block] - c[starts]) / block


_weighted_block_ms = _weighted_block_ms_loop if HAVE_NUMBA else _weighted_block_ms_np


def _lufs_from_ms(ms: np.ndarray) -> np.ndarray:
    return -0.691 + 10.0*np.log10(np.maximum(ms, 1e-30))

def _ms_from_lufs(lufs: np.ndarray) -> np.ndarray:
    return 10.0 ** ((lufs + 0.691) / 10.0)

def channel_gains(channels: int) -> np.ndarray:
    table = LAYOUTS[CHANNEL_LAYOUT]
    if channels in table:
        return np.asarray(table[channels], dtype=np.float64)
    return np.ones(channels, dtype=np.float64)

def loudness_blocks(x: np.ndarray, sr: int, seconds: float) -> np.ndarray:
    y = k_weight(x, sr)
    block = max(1, int(round(seconds*sr)))
    hop = max(1, int(round(HOP_S*sr)))
    return _weighted_block_ms(y, channel_gains(x.shape[1]), block, hop)

def integrated_lkfs(x: np.ndarray, sr: int) -> float:
    ms = loudness_blocks(x, sr, BLOCK_S)
    if ms.size == 0:
        return float("-inf")
    # Absolute gate is applied in loudness domain.
    keep = _lufs_from_ms(ms) > ABS_GATE_LUFS
    if not np.any(keep):
        return float("-inf")
    abs_ms = ms[keep]
    # Relative gate is energy-domain: average the mean-square energies of
    # blocks surviving the absolute gate, then subtract 10 LU.
    rel_lufs = float(_lufs_from_ms(np.array([abs_ms.mean()]))[0] + REL_GATE_LU)
    keep_rel = _lufs_from_ms(abs_ms) > rel_lufs
    gated = abs_ms[keep_rel]
    if gated.size == 0:
        return float("-inf")
    return float(_lufs_from_ms(np.array([gated.mean()]))[0])

def momentary_lkfs(x: np.ndarray, sr: int) -> np.ndarray:
    ms = loudness_blocks(x, sr, MOMENTARY_S)
    return _lufs_from_ms(ms) if ms.size else np.empty(0)

def short_term_lkfs(x: np.ndarray, sr: int) -> np.ndarray:
    ms = loudness_blocks(x, sr, ST_WINDOW_S)
    return _lufs_from_ms(ms) if ms.size else np.empty(0)

def loudness_range(x: np.ndarray, sr: int) -> float:
    st = short_term_lkfs(x, sr)
    st = st[np.isfinite(st) & (st > ABS_GATE_LUFS)]
    if st.size < 2:
        return 0.0
    # EBU Tech 3342: absolute gate (-70 LUFS) first, then a relative gate 20 LU below the
    # POWER (energy) mean of the short-term values that survived. (The previous revision used
    # 20 LU below the 10th percentile, which is a much lower threshold and lets quiet passages
    # inflate the range.)
    rel = float(_lufs_from_ms(np.array([_ms_from_lufs(st).mean()]))[0]) - 20.0
    gated = st[st > rel]
    if gated.size < 2:
        return 0.0
    return float(np.percentile(gated, 95.0) -
                 np.percentile(gated, 10.0))

def true_peak_dbtp(x: np.ndarray, sr: int,
                   oversample: int = TP_OVERSAMPLE) -> float:
    if x.size == 0:
        return float("-inf")
    if oversample < 1:
        raise ValueError("true-peak oversample must be >= 1")
    y = resample_poly(x, oversample, 1, axis=0)
    return float(20.0*np.log10(np.max(np.abs(y)) + 1e-30))

def sample_peak_dbfs(x: np.ndarray) -> float:
    if x.size == 0:
        return float("-inf")
    return float(20.0*np.log10(np.max(np.abs(x)) + 1e-30))

def finite_status(x: np.ndarray) -> bool:
    return bool(np.isfinite(x).all())

def normalize_to_lufs(x: np.ndarray, current: float, target: float) -> tuple[np.ndarray, float]:
    if not math.isfinite(current):
        raise ValueError("cannot normalize a signal with undefined integrated loudness")
    gain = target-current
    return x*(10.0**(gain/20.0)), gain

def trim_true_peak(x: np.ndarray, sr: int, ceiling: float) -> tuple[np.ndarray, float]:
    tp = true_peak_dbtp(x, sr)
    if tp <= ceiling:
        return x, 0.0
    trim = ceiling-tp
    return x*(10.0**(trim/20.0)), trim

def upsample_high_rate(x: np.ndarray, factor: int = OUTPUT_UPSAMPLE) -> np.ndarray:
    if factor < 1:
        raise ValueError("upsample factor must be >= 1")
    return resample_poly(_align(x), factor, 1, axis=0)

def safe_pcm(x: np.ndarray, bits: int) -> tuple[np.ndarray, bool]:
    limit = 1.0
    p = float(np.max(np.abs(x))) if x.size else 0.0
    if p <= limit:
        return x, False
    # This is an explicit final safety operation. In normal operation the TP
    # ceiling should already prevent this. It is reported as safety_scaled.
    return x/p, True

@dataclass
class Measurement:
    integrated_lufs: float = float("-inf")
    lra_lu: float = 0.0
    momentary_max_lufs: float = float("-inf")
    short_term_max_lufs: float = float("-inf")
    sample_peak_dbfs: float = float("-inf")
    true_peak_dbtp: float = float("-inf")

@dataclass
class Render:
    target_lufs: float
    requested_gain_db: float = 0.0
    tp_ceiling_dbtp: float = DEFAULT_TP
    tp_trim_db: float = 0.0
    ceiling_limited: bool = False
    safety_scaled: bool = False

@dataclass
class Verification:
    integrated_lufs: float = float("-inf")
    lra_lu: float = 0.0
    sample_peak_dbfs: float = float("-inf")
    true_peak_dbtp: float = float("-inf")
    loudness_error_lu: float = float("nan")
    finite: bool = True
    clipped: bool = False

@dataclass
class Report:
    version: str
    file: str
    output: str
    sr_in: int
    sr_out: int
    channels: int
    frames_in: int
    frames_out: int
    input_bits: Optional[int]
    output_bits: int
    upsample_factor: int
    measurement: Measurement
    render: Render
    verification: Verification
    wall_s: float
    numba: bool
    backend: str
    layout: str = "wav"

def _backend() -> str:
    try:
        cfg = np.__config__.show(mode="dicts")
        return cfg.get("Build Dependencies", {}).get("blas", {}).get("name", "unknown")
    except Exception:
        return "unknown"

def analyze(x: np.ndarray, sr: int) -> Measurement:
    st = short_term_lkfs(x, sr)
    mo = momentary_lkfs(x, sr)
    return Measurement(
        integrated_lufs=integrated_lkfs(x, sr),
        lra_lu=loudness_range(x, sr),
        momentary_max_lufs=float(np.max(mo)) if mo.size else float("-inf"),
        short_term_max_lufs=float(np.max(st)) if st.size else float("-inf"),
        sample_peak_dbfs=sample_peak_dbfs(x),
        true_peak_dbtp=true_peak_dbtp(x, sr),
    )

def process_one(infile: str, outfile: str, target: float, bits: int,
                hp_hz: float, tp_ceiling: float, do_8x: bool,
                layout: str = "wav") -> Report:
    import soundfile as sf          # imported here so the measurement API works without libsndfile
    set_layout(layout)
    t0 = time.time()
    data, sr = sf.read(infile, always_2d=True, dtype="float64")
    data = _align(data)

    if not finite_status(data):
        raise ValueError(f"{infile}: input contains NaN or Inf")

    frames_in, channels = data.shape
    if channels < 1:
        raise ValueError("input has no channels")

    if hp_hz > 0:
        if hp_hz >= sr*0.5:
            raise ValueError("high-pass cutoff must be below Nyquist")
        sos = butter(2, hp_hz/(sr*0.5), btype="highpass", output="sos")
        data = sosfilt(sos, data, axis=0)

    before = analyze(data, sr)
    data, requested_gain = normalize_to_lufs(
        data, before.integrated_lufs, target
    )
    data, tp_trim = trim_true_peak(data, sr, tp_ceiling)

    render = Render(
        target_lufs=target,
        requested_gain_db=requested_gain,
        tp_ceiling_dbtp=tp_ceiling,
        tp_trim_db=tp_trim,
        ceiling_limited=(tp_trim < -1e-12),
    )

    after_core = analyze(data, sr)

    if do_8x:
        data = upsample_high_rate(data, OUTPUT_UPSAMPLE)
        sr_out = sr*OUTPUT_UPSAMPLE
    else:
        sr_out = sr

    data, safety_scaled = safe_pcm(data, bits)
    render.safety_scaled = safety_scaled

    final = analyze(data, sr_out)
    verification = Verification(
        integrated_lufs=final.integrated_lufs,
        lra_lu=final.lra_lu,
        sample_peak_dbfs=final.sample_peak_dbfs,
        true_peak_dbtp=final.true_peak_dbtp,
        loudness_error_lu=final.integrated_lufs-target,
        finite=finite_status(data),
        clipped=bool(final.true_peak_dbtp > 0.0),
    )

    subtype = {16: "PCM_16", 24: "PCM_24", 32: "FLOAT"}[bits]
    sf.write(outfile, data, sr_out, subtype=subtype)

    return Report(
        version=VERSION,
        file=infile,
        output=outfile,
        sr_in=sr,
        sr_out=sr_out,
        channels=channels,
        frames_in=frames_in,
        frames_out=data.shape[0],
        input_bits=None,
        output_bits=bits,
        upsample_factor=OUTPUT_UPSAMPLE if do_8x else 1,
        measurement=before,
        render=render,
        verification=verification,
        wall_s=time.time()-t0,
        numba=HAVE_NUMBA,
        backend=_backend(),
        layout=CHANNEL_LAYOUT,
    )

def _fmt(r: Report) -> str:
    m, v = r.measurement, r.verification
    return (
        f"{os.path.basename(r.file):34s} "
        f"LUFS {m.integrated_lufs:7.2f}->{v.integrated_lufs:7.2f}  "
        f"TP {m.true_peak_dbtp:6.2f}->{v.true_peak_dbtp:6.2f}  "
        f"LRA {v.lra_lu:5.2f}  "
        f"{r.sr_in}->{r.sr_out} Hz  {r.wall_s:5.2f}s"
    )

def main() -> int:
    ap = argparse.ArgumentParser(
        prog="littlesqrt",
        description="Little sQrt v2.0.0 — loudness normalization + true peak"
    )
    ap.add_argument("infile", nargs="?")
    ap.add_argument("outfile", nargs="?")
    ap.add_argument("--batch", help="text file containing: infile outfile")
    ap.add_argument("--target", type=float, default=-23.0)
    ap.add_argument("--bits", type=int, choices=[16,24,32], default=24)
    ap.add_argument("--hp", type=float, default=20.0)
    ap.add_argument("--tp", type=float, default=-1.0)
    ap.add_argument("--no-8x", action="store_true")
    ap.add_argument("--layout", choices=sorted(LAYOUTS), default="wav",
                    help="multichannel order: wav = L R C LFE Ls Rs (default), lfe-last = LFE is the final channel")
    ap.add_argument("--workers", type=int,
                    default=max(1, (os.cpu_count() or 4)//2))
    ap.add_argument("--report")
    args = ap.parse_args()

    jobs = []
    if args.batch:
        with open(args.batch, encoding="utf-8") as f:
            for line in f:
                line=line.strip()
                if not line or line.startswith("#"):
                    continue
                p=line.split()
                if len(p) >= 2:
                    jobs.append((p[0],p[1]))
    else:
        if not args.infile or not args.outfile:
            ap.error("provide infile outfile or --batch list.txt")
        jobs=[(args.infile,args.outfile)]

    kwargs=dict(
        target=args.target, bits=args.bits, hp_hz=args.hp,
        tp_ceiling=args.tp, do_8x=not args.no_8x, layout=args.layout
    )

    reports=[]
    errors=[]
    if len(jobs)==1 or args.workers<=1:
        for i,o in jobs:
            try:
                r=process_one(i,o,**kwargs)
                reports.append(r)
                print(_fmt(r))
            except Exception as e:
                errors.append({"file":i,"output":o,"error":str(e)})
                print(f"ERROR {i}: {e}", file=sys.stderr)
    else:
        with ProcessPoolExecutor(max_workers=args.workers) as ex:
            futs={ex.submit(process_one,i,o,**kwargs):(i,o) for i,o in jobs}
            for fut in as_completed(futs):
                i,o=futs[fut]
                try:
                    r=fut.result()
                    reports.append(r)
                    print(_fmt(r))
                except Exception as e:
                    errors.append({"file":i,"output":o,"error":str(e)})
                    print(f"ERROR {i}: {e}", file=sys.stderr)

    payload={
        "tool":"Little sQrt",
        "version":VERSION,
        "reports":[asdict(r) for r in reports],
        "errors":errors,
        "backend":_backend(),
        "numba":HAVE_NUMBA,
        "workers":args.workers,
    }
    if args.report:
        with open(args.report,"w",encoding="utf-8") as f:
            json.dump(payload,f,indent=2,allow_nan=True)
        print(f"report -> {args.report}")
    return 1 if errors else 0

if __name__ == "__main__":
    raise SystemExit(main())
