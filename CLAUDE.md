# audiolab

Audio analysis tool using CM106 USB audio devices.
Cross-platform: works on Raspberry Pi or laptop.

## Hardware

- CM106 USB audio codec — full duplex (simultaneous playback + capture)
- Two units available: one on a Pi, one on the laptop
- Initially connected via null cable (loopback); future: DUT under test

## Architecture

Three UI layers, built in order:
1. **Text** — device listing, basic signal stats printed to stdout
2. **Curses** — live oscilloscope and FFT in terminal
3. **Browser** — full web UI (FastAPI + WebSocket, house dark-mode iOS style)

## Audio

Uses `sounddevice` which abstracts over ALSA / PulseAudio / PipeWire.
PipeWire config is handled separately — start simple, add config only when needed.

## Planned analyses

- Oscilloscope (time domain)
- FFT (frequency spectrum)
- Spectrogram
- Frequency response (sine sweep)
- Impedance (requires hardware discussion)

## Dev setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python3 -m audiolab devices
```
