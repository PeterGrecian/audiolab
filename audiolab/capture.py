"""Audio capture and basic stats."""

import numpy as np
import sounddevice as sd


def record(duration=1.0, device=None, samplerate=48000, channels=1):
    """Record audio and return as numpy array (float32, shape: [samples, channels])."""
    data = sd.rec(
        int(samplerate * duration),
        samplerate=samplerate,
        channels=channels,
        dtype='float32',
        device=device,
    )
    sd.wait()
    return data


def stats(data):
    """Return basic stats dict for a recorded buffer."""
    mono = data[:, 0] if data.ndim > 1 else data
    peak = float(np.max(np.abs(mono)))
    rms = float(np.sqrt(np.mean(mono ** 2)))
    db_peak = 20 * np.log10(peak) if peak > 0 else -np.inf
    db_rms = 20 * np.log10(rms) if rms > 0 else -np.inf
    return {
        "samples": len(mono),
        "peak": peak,
        "rms": rms,
        "dBFS_peak": db_peak,
        "dBFS_rms": db_rms,
    }
