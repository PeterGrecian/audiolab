"""Test signal generation."""

import numpy as np
import sounddevice as sd


def sine(freq=1000, duration=1.0, amplitude=0.5, samplerate=48000):
    """Generate a sine wave array."""
    t = np.linspace(0, duration, int(samplerate * duration), endpoint=False)
    return (amplitude * np.sin(2 * np.pi * freq * t)).astype(np.float32)


def sweep(f_start=20, f_end=20000, duration=5.0, amplitude=0.5, samplerate=48000):
    """Generate a logarithmic sine sweep."""
    t = np.linspace(0, duration, int(samplerate * duration), endpoint=False)
    # Logarithmic sweep: instantaneous frequency grows exponentially
    k = duration / np.log(f_end / f_start)
    phase = 2 * np.pi * f_start * k * (np.exp(t / k) - 1)
    return (amplitude * np.sin(phase)).astype(np.float32)


def noise(duration=1.0, amplitude=0.5, samplerate=48000):
    """Generate white noise."""
    n = int(samplerate * duration)
    return (amplitude * np.random.uniform(-1, 1, n)).astype(np.float32)


def play(signal, device=None, samplerate=48000):
    """Play a signal array and wait for completion."""
    sd.play(signal, samplerate=samplerate, device=device)
    sd.wait()
