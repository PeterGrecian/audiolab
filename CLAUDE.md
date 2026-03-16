# audiolab

Audio analysis tool using CM106 USB audio devices.
Cross-platform: works on Raspberry Pi or laptop.

## Devices

### turquoise — CM106 (laptop)

Name: `turquoise`. ALSA enumerates as `ICUSBAUDIO7D: USB Audio` (device 4).

| Ch | Signal | Jack | Colour |
|----|--------|------|--------|
| 1 | Front L | Output | Green (tip) |
| 2 | Front R | Output | Green (ring) |
| 3 | Centre | Output | Orange (tip) |
| 4 | LFE/Sub | Output | Orange (ring) |
| 5 | Rear L | Output | Black (tip) |
| 6 | Rear R | Output | Black (ring) |
| 7 | Side L | — | no jack |
| 8 | Side R | — | no jack |
| 1 | Line-in L | Input | Blue (tip) |
| 2 | Line-in R | Input | Blue (ring) |
| — | Mic | Input | Pink (mono) |

Jacks: 3 output (green/orange/black) + line-in (blue) + mic (pink) + S/PDIF.
Supported sample rates: 44100, 48000 Hz.

Known issues:
- Line-in R reads 0.5–2.4 dB lower than L (frequency-dependent, confirmed not cable)
- Orange jack channels 3,4 work but were not detected by earlier balance test (re-test needed)

Connections:
- **Analog loopback**: front out (green) → line in (blue), null cable
- **Digital loopback**: S/PDIF out → S/PDIF in, coaxial RCA or TOSLINK (not yet tested)

### Sweex SC016 (Raspberry Pi)

Name: `sc016`. On the Pi — not yet characterised.

| Ch | Signal | Jack | Colour |
|----|--------|------|--------|
| 1 | Front L | Output | Green (tip) |
| 2 | Front R | Output | Green (ring) |
| 3 | Rear L | Output | Black (tip) |
| 4 | Rear R | Output | Black (ring) |
| 5 | Centre | Output | Orange (tip) |
| 6 | LFE/Sub | Output | Orange (ring) |
| 7 | Side L | Output | Grey (tip) |
| 8 | Side R | Output | Grey (ring) |
| 1 | Line-in L | Input | Blue (tip) |
| 2 | Line-in R | Input | Blue (ring) |
| — | Headphone | Output | (separate jack, no mic) |

Jacks: 4 output (green/black/orange/grey) + line-in (blue) + headphone + S/PDIF. No mic jack.
Channel numbering above is typical for this class of device — verify with probe script before use.

## Application context

Primary use case: characterise and EQ a 15" bass/mid driver in a 5×4×3m room
for classical music at <90 dB SPL. Room is modal below ~163 Hz (Schroeder).
Strong room modes at 34, 43, 57 Hz. Triple axial coincidence at 171.5 Hz (c/2).
Speaker is corner-placed, sealed enclosure (too large), plan to port at Fb≈50Hz,
crossover at ~200 Hz.

Measurement workflow:
1. Impedance jig → driver T/S parameters, port tuning verification
2. Garden free-field sweep (mic at 1m) → driver + box response
3. In-room sweep (mic at listening position) → driver + box + room
4. Difference → room transfer function → DSP correction filter

See `docs/acoustic_workflow.md` for full detail.

## Architecture

Three UI layers, built in order:
1. **Text** — device listing, basic signal stats printed to stdout
2. **Curses** — live oscilloscope and FFT in terminal
3. **Browser** — full web UI (FastAPI + WebSocket, house dark-mode iOS style)

## Audio

Uses `sounddevice` which abstracts over ALSA / PulseAudio / PipeWire.
PipeWire config is handled separately — start simple, add config only when needed.

### ALSA note — multi-channel output

ALSA hw devices require a full N-channel output buffer. Sending a 2-channel
signal with output_mapping to non-default channels (e.g. [3,4] orange) is
silently ignored — signal lands on channels 1,2 instead. Fix: always build
an N-channel buffer and place signal in the correct column indices. This is
implemented in the balance command.

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
