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


def thd(data, fundamental_hz, samplerate=48000, n_harmonics=5):
    """Return THD as a percentage for a single-channel buffer."""
    mono = data[:, 0] if data.ndim > 1 else data
    n = len(mono)
    window = np.hanning(n)
    spectrum = np.abs(np.fft.rfft(mono * window)) / (n / 2)
    freqs = np.fft.rfftfreq(n, d=1.0 / samplerate)
    bin_hz = samplerate / n

    def bin_rms(f):
        # Sum energy in a ±2 bin window around the target frequency
        idx = int(round(f / bin_hz))
        lo, hi = max(0, idx - 2), min(len(spectrum), idx + 3)
        return np.sqrt(np.mean(spectrum[lo:hi] ** 2))

    fundamental_rms = bin_rms(fundamental_hz)
    if fundamental_rms < 1e-10:
        return 0.0
    harmonic_power = sum(
        bin_rms(fundamental_hz * k) ** 2
        for k in range(2, n_harmonics + 1)
        if fundamental_hz * k < samplerate / 2
    )
    return 100.0 * np.sqrt(harmonic_power) / fundamental_rms


def balance_freqs():
    """Return measurement frequencies: 16 below 1kHz, 8 above (2:1 ratio)."""
    low = np.logspace(np.log10(20), np.log10(999), 16)
    high = np.logspace(np.log10(1000), np.log10(20000), 8)
    return np.concatenate([low, high])


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
