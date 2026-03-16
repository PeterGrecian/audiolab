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


def peak_frequency(freqs, db):
    """Return the frequency of the strongest spectral peak."""
    idx = np.argmax(db)
    return freqs[idx], db[idx]
