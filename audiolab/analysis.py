"""FFT and spectral analysis."""

import numpy as np


def fft(data, samplerate=48000):
    """Compute magnitude spectrum. Returns (frequencies, magnitudes_dB)."""
    mono = data[:, 0] if data.ndim > 1 else data
    n = len(mono)
    window = np.hanning(n)
    spectrum = np.fft.rfft(mono * window)
    freqs = np.fft.rfftfreq(n, d=1.0 / samplerate)
    magnitude = np.abs(spectrum) / (n / 2)
    magnitude = np.maximum(magnitude, 1e-10)  # avoid log(0)
    db = 20 * np.log10(magnitude)
    return freqs, db


def peak_frequency(freqs, db, min_freq=20.0):
    """Return the frequency of the strongest spectral peak above min_freq (skips DC)."""
    mask = freqs >= min_freq
    if not np.any(mask):
        idx = np.argmax(db)
    else:
        sub = db.copy()
        sub[~mask] = -np.inf
        idx = np.argmax(sub)
    return freqs[idx], db[idx]
