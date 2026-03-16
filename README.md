# audiolab

Audio analysis and measurement tool using CM106 USB audio devices.
Cross-platform — runs on a Raspberry Pi or laptop.

## Usage

```bash
source .venv/bin/activate

python -m audiolab devices                        # list audio devices, highlight CM106
python -m audiolab test                           # 1kHz loopback tone, print stats
python -m audiolab test --freq 440 --duration 3   # custom tone
python -m audiolab response                       # frequency response (5s log sweep)
python -m audiolab response --duration 30         # slower sweep, better resolution
python -m audiolab rolloff                        # low-end rolloff order via stepped sines
python -m audiolab balance                        # stereo channel balance + crosstalk (~10 min)
python -m audiolab balance --name myamp           # tag CSV with device name
python -m audiolab balance --out-channels 5 6     # use rear output (black jack)
python -m audiolab monitor                        # live curses oscilloscope + FFT
python -m audiolab impedance                      # Z(f) measurement (needs external amp + sense resistor)
python -m audiolab impedance --r-sense 10 --end 2000 --duration 30
python -m audiolab calibrate balance_turquoise_20260316_132606.csv   # L/R correction curve
```

## Installation

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Requires `python3.13-venv` on Ubuntu/Debian: `sudo apt install python3.13-venv`

### CM106 ALSA setup (run once after plugging in)

The CM106 defaults to mic input — switch to line-in before use:

```bash
amixer -c 1 cset numid=16 1    # capture source = Line
amixer -c 1 cset numid=11 on   # Line Capture Switch on
amixer -c 1 cset numid=12 4096,4096   # Line Capture Volume = 0 dB
alsactl store                  # persist across reboot
```

Capture source enum: `0`=Mic, `1`=Line, `2`=IEC958 (S/PDIF), `3`=Mixer

## Hardware

### turquoise — CM106 (laptop)

ALSA: `ICUSBAUDIO7D: USB Audio`. Jacks: 3 output + line-in + mic + S/PDIF.
Sample rates: 44100, 48000 Hz. Bandwidth: −3 dB at ~85 Hz and ~17 kHz.

| Ch | Signal | Jack | Colour |
|----|--------|------|--------|
| 1 | Front L | Output | Green (tip) |
| 2 | Front R | Output | Green (ring) |
| 3 | Centre | Output | Orange (tip) |
| 4 | LFE/Sub | Output | Orange (ring) |
| 5 | Rear L | Output | Black (tip) |
| 6 | Rear R | Output | Black (ring) |
| 1 | Line-in L | Input | Blue (tip) |
| 2 | Line-in R | Input | Blue (ring) |
| — | Mic | Input | Pink (mono) |

Known: line-in R reads 0.5–2.4 dB low vs L (frequency-dependent, confirmed not cable).

### Sweex SC016 (Raspberry Pi)

Jacks: 4 output + line-in + headphone + S/PDIF. No mic.
Channel numbering to be verified with probe script — typical layout below.

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

### S/PDIF loopback (not yet tested, both devices)

Connect S/PDIF out → in with coaxial RCA or TOSLINK. Switch capture source:

```bash
amixer -c 1 cset numid=16 2    # capture source = IEC958 In
amixer -c 1 cset numid=13 on   # IEC958 In Capture Switch on
```

Expected benefit: flat response to 22 kHz, bypasses analog frontend entirely.

## Measurements

### `impedance` — impedance Z(f) measurement

Requires external power amp and 10 Ω (1%) wirewound sense resistor. Circuit:

```
Amp ─── DUT ─── [R_sense] ─── GND
            │              │
       line-in L       line-in R
       (V_ref)         (V_sense)

Z(f) = R_sense × (V_ref(f) / V_sense(f) − 1)
```

CM106 output → amp input (low-level signal only). Both line-in channels record simultaneously.
Log sweep, transfer function computed per frequency band. Output: ASCII chart + CSV with |Z| and phase.

```
timestamp, device, r_sense_ohm, frequency_hz, Z_ohm, Z_phase_deg
```

Identifies Fs (impedance peak → resonant frequency) and Re (minimum Z → voice coil DC resistance).

### `calibrate` — L/R input correction

Reads a `balance` CSV and computes per-frequency gain offsets to correct CM106 line-in channel asymmetry
(L reads 0.5–2.4 dB higher than R). Output CSV: `frequency_hz, L_gain_db, R_gain_db, L_minus_R_db`.

### `balance` — channel balance and crosstalk

Plays sine tones at 24 log-spaced frequencies (2:1 density below 1 kHz),
4 amplitudes (−6 to −24 dBFS), 3 modes (L only, R only, both).
288 tones, ~10 min. Output is a CSV written row-by-row (safe to interrupt).

```
timestamp, device, out_channels, mode, frequency_hz, amplitude_dbfs,
L_rms_dbfs, R_rms_dbfs, L_peak_dbfs, R_peak_dbfs,
L_crest, R_crest, balance_db,
L_thd_pct, R_thd_pct, L_xtalk_dbfs, R_xtalk_dbfs
```

Crosstalk is measured via FFT at the driven frequency, not broadband RMS.
Measured isolation: >113 dBFS (at the noise floor — true crosstalk is unmeasurable).

### `response` — frequency response

Log sine sweep, transfer function H(f) = Y(f)/X(f), binned to log-spaced bands,
normalised to 0 dB at 1 kHz. ASCII chart output. Energy masking prevents
endpoint blow-up artifacts. 30s sweep recommended for best low-end resolution.

### `rolloff` — filter order at low end

Stepped sine tones with per-octave slope and best-fit filter order.
CM106 result: ~4 dB/oct (order ~0.7) — sub-first-order, consistent with
combined analog coupling capacitor and digital DC-blocking high-pass.

## Findings — turquoise CM106

- **Bandwidth**: −3 dB at ~85 Hz (low) and ~17 kHz (high)
- **Low-end rolloff**: ~4 dB/octave, order ~0.7 — sub-first-order, consistent
  with combined analog coupling cap and digital DC-blocking HP filter.
  Same rolloff on all three output jacks — confirms digital origin.
- **Input asymmetry**: line-in R reads 0.5–2.4 dB lower than L, frequency-
  dependent. Confirmed not the cable (verified across three output jacks and
  two cables). Calibration correction required before L/R comparison measurements.
- **Channel isolation**: >113 dBFS — true crosstalk is below the noise floor.
- **Orange output (ch 3,4)**: works but requires full 8-channel output buffer.
  ALSA silently ignores output_mapping for partial channel counts.
- **Orange output balance**: matches green and black within 0.1 dB — all three
  outputs are consistent.

## Datasets

| File | Device | Output | Cable | Notes |
|------|--------|--------|-------|-------|
| `balance_turquoise_20260316_110658.csv` | turquoise | green ch1,2 | long | First run — broadband RMS crosstalk (unreliable), balance valid |
| `balance_turquoise_rear_20260316_112832.csv` | turquoise | black ch5,6 | long | FFT crosstalk |
| `balance_short_orange_20260316_121241.csv` | turquoise | orange ch3,4 | short | **No signal** — ALSA channel bug, discard |
| `balance_short_green_20260316_123219.csv` | turquoise | green ch1,2 | short | Confirms cable not responsible for imbalance |
| `balance_turquoise_orange_20260316_131439.csv` | turquoise | orange ch3,4 | short | **No signal** — same bug, discard |
| `balance_turquoise_orange_20260316_132606.csv` | turquoise | orange ch3,4 | short | **Good** — full channel buffer fix applied |

## Planned

### Next: acoustic measurement (mic)

Uncalibrated mic is sufficient for relative (garden vs room) measurements.
Mic response cancels in the difference. Connects to CM106 mic-in or line-in.

```
Garden  → free-field SPL(f)  = driver + box
Room    → in-room SPL(f)     = driver + box + room
Difference                   = room transfer function → DSP correction
```

See `docs/acoustic_workflow.md` for full workflow including room mode analysis.

### Outputs (printable)

- Power amp sticker: gain/frequency plot (matplotlib, fixed label dimensions)
- Preamp dial: calibrated gain/SPL scale (SVG, input speaker sensitivity)

### Further

- `measure` command — acoustic SPL sweep (plays through amp/speaker, captures via mic)
- S/PDIF loopback characterisation (Toslink cable now available)
- Sweex SC016 characterisation (on Raspberry Pi)
- Live curses monitor improvements
- Browser UI (FastAPI + WebSocket, dark-mode iOS style)
