# Acoustic Measurement Workflow

## Goal

Design and EQ a 15" bass/mid driver in a domestic room for classical music
reproduction below 90 dB SPL. Avoid room modes, apply DSP correction.

## The Room

5m × 4m × 3m (height). Volume 60 m³. Corner-placed speaker.

### Axial room modes

| Hz | Dimension | Note |
|----|-----------|------|
| 34.3 | 5m (1st) | |
| 42.9 | 4m (1st) | Almost exactly double bass open E (41.2 Hz) |
| 57.2 | 3m (1st) | |
| 68.6 | 5m (2nd) | |
| 85.7 | 4m (2nd) | |
| 102.9 | 5m (3rd) | |
| 114.3 | 3m (2nd) | |
| 128.6 | 4m (3rd) | |
| 137.2 | 5m (4th) | |
| **171.5** | **5m(5th) + 4m(4th) + 3m(3rd)** | **Triple axial coincidence — c/2** |

171.5 Hz = c/2. All three room dimensions independently produce an axial mode
here (n/L = 1 for each: 5th mode of 5m, 4th of 4m, 3rd of 3m). Will be strong.

### Schroeder frequency

f_s ≈ 2000 × √(RT60 / V) ≈ 2000 × √(0.4 / 60) ≈ **163 Hz**

Below 163 Hz the room behaves modally. The entire subwoofer/bass range is modal.
Above it, diffuse-field behaviour — carpets and curtains start to help.

### What carpets and curtains do (and don't do)

Effective above ~800 Hz. At 50 Hz the wavelength is 6.9 m — you'd need 1.7 m
thick absorbers for quarter-wave absorption. Furnishings have negligible effect
on bass modes. DSP correction or careful placement is the practical solution.

---

## The Speaker

15" bass/mid driver, sealed enclosure (currently too large → low Qtc, lean).
Plan: add port, Fb ≈ 50 Hz. Crossover to mid/treble at ~200 Hz.

Corner placement gives +6–9 dB bass loading — maximally excites room modes
but also extends useful bass response. A high-pass filter at Fb protects the
driver below port tuning where the cone is unloaded (excursion rises steeply).

Driver T/S parameters (Fs, Qts, Vas, Xmax) to be measured with impedance jig.

---

## Measurement Workflow

### Stage 1 — Driver characterisation (impedance)

```
Amp → [10Ω sense] ──┬── DUT (driver/speaker) ── GND
                    │
               line-in L (V_ref)   line-in R (V_sense)
```

Z(f) = R_sense × (V_ref / V_sense − 1)

From Z curve: read Fs (impedance peak), identify port tuning Fb (second peak
for ported), voice coil inductance (rising Z at HF). Derive Qts from bandwidth
of resonance peak, Vas from Fs shift with known added mass.

Amp must be characterised first (frequency response, output impedance) so
V_drive(f) is known. Once calibrated, both line-in channels are free for
dual-speaker simultaneous measurement.

### Stage 2 — Free-field reference (garden)

Place speaker + enclosure on the ground outdoors. Mic at 1 m on-axis.
Ground plane measurement: floor reflection reinforces, all other reflections
absent. Gives true driver + box + port response without room contribution.

```bash
python -m audiolab measure --name driver_garden --distance 1.0
```

### Stage 3 — In-room measurement

Same mic, same gain, at listening position.

```bash
python -m audiolab measure --name driver_room --distance 3.0
```

### Stage 4 — Room correction

Room transfer function = in-room SPL(f) − garden SPL(f)
Correction filter = inverse of room transfer function (within limits)

Apply via miniDSP, convolution plugin, or similar DSP processor.

### Notes on uncalibrated microphones

For relative measurement (garden vs room), mic frequency response cancels —
the same mic sees both conditions and the difference is the room alone.
Absolute SPL accuracy is not required for EQ correction. Any microphone works.

A calibrated mic (e.g. MiniDSP UMIK-1 with correction file) is needed only
for absolute SPL measurements or comparing between different sessions.

---

## Planned audiolab commands

| Command | Description |
|---------|-------------|
| `impedance` | Z(f) measurement via sense resistor and two-channel line-in |
| `calibrate` | Derive L/R input correction curve from balance CSV data |
| `measure` | Acoustic SPL sweep — plays through amp/speaker, captures via mic |
| `response` | (existing) Electrical loopback frequency response |

## Amp calibration for impedance measurement

1. Connect: CM106 out → amp → R_load (10Ω power resistor) → GND
2. Line-in L: V at amp output (before sense resistor)
3. Line-in R: V_sense (across sense resistor)
4. Store H_amp(f) = V_out(f) / V_in(f) as calibration file

Once stored, V_drive(f) is known for all subsequent measurements without
re-measuring. Stored on sticker as gain/frequency plot. If amp output
impedance < 1Ω, single-point calibration is sufficient.

For parallel speaker measurements:
- Line-in L → sense resistor 1 → speaker 1 current
- Line-in R → sense resistor 2 → speaker 2 current
- V_drive(f) from calibration
- Simultaneous Z1(f), Z2(f), Z_parallel(f) in one sweep
