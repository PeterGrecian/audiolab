# audiolab

Audio analysis tool using CM106 USB audio devices.
Cross-platform: works on Raspberry Pi or laptop.

## Hardware

- CM106 USB audio codec — full duplex (simultaneous playback + capture)
- Two units available: one on a Pi, one on the laptop
- On this laptop the CM106 enumerates as **`ICUSBAUDIO7D: USB Audio`** (ALSA device 4)
- Connections:
  - **Analog loopback**: front out (green) → line in (blue), null cable
  - **Digital loopback**: S/PDIF out → S/PDIF in, coaxial RCA or TOSLINK (not yet tested)

## Architecture

Three UI layers, built in order:
1. **Text** — device listing, basic signal stats printed to stdout
2. **Curses** — live oscilloscope and FFT in terminal
3. **Browser** — full web UI (FastAPI + WebSocket, house dark-mode iOS style)

## Audio

Uses `sounddevice` which abstracts over ALSA / PulseAudio / PipeWire.
PipeWire config is handled separately — start simple, add config only when needed.

### CM106 ALSA mixer setup (laptop)

The CM106 defaults to mic input — must be switched to line-in before use.
These settings reset on unplug/reboot:

```bash
# Switch capture source to Line (analog loopback via null cable)
amixer -c 1 cset numid=16 1   # PCM Capture Source = Line
amixer -c 1 cset numid=11 on  # Line Capture Switch = on
amixer -c 1 cset numid=12 4096,4096  # Line Capture Volume = 0 dB

# Switch capture source to S/PDIF (digital loopback via coaxial/TOSLINK)
amixer -c 1 cset numid=16 2   # PCM Capture Source = IEC958 In
amixer -c 1 cset numid=13 on  # IEC958 In Capture Switch = on

# Persist settings across unplug (saves to /var/lib/alsa/asound.state)
alsactl store
```

Capture source enum: 0=Mic, 1=Line, 2=IEC958 In, 3=Mixer

### S/PDIF loopback notes

The CM106 supports S/PDIF I/O (IEC958). Looping S/PDIF out → in on the same
device works because the chip recovers its own transmitted clock. This gives a
purely digital round-trip — eliminates ADC/DAC noise, ideal for clean measurements.
Not yet tested (cable needed).

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
