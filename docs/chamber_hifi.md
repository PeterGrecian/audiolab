# Chamber Hifi — System Notes

*A bedroom system for chamber music. And The Smiths.*

---

## System

### Satellites — "chamber" speakers

- **Driver:** Faital Pro 3FE25 — 3" full-range, 8Ω, 91 dB/W/m, Fs = 110 Hz
- **Enclosure:** 1 litre sealed, hand-built
- **Range:** usefully flat ~150 Hz – 20 kHz in-box; sub handles below

The 3FE25 is a professional full-range driver — copper-cap demodulation, 19mm aluminium voice coil. Chosen for low distortion in a compact sealed box. At 91 dB sensitivity it barely exercises the T3250W's amp.

### Amplifier / subwoofer — Creative T3250W (mildly modded)

- Original plastic satellite speakers removed; replaced by the Faital chambers above
- T3250W internal electronics retained: amp, subwoofer, crossover, DSE processing
- Crossover between satellites and sub: nominally ~100–130 Hz
- 6000mAh internal battery — no mains cable for bedside use
- Bluetooth A2DP input from laptop

**DSE (Dynamic Sound Enhancement):** Creative's proprietary processing — claims wider sweet spot and more mid-bass. With the original cheap satellites gone and 91 dB professional drivers installed, the DSE tuning may no longer be optimal. Worth measuring and potentially bypassing or EQ-correcting.

---

## Signal Chain for Acoustic Measurement

```
laptop ──BT A2DP──► T3250W amp ──► Faital 3FE25 (1L sealed)
                                          │
                                       [air]
                                          │
                                    CM106 mic input
                                          │
                                      laptop
```

- **Output device:** Creative T3250W (BT device, PipeWire sink 132)
- **Input device:** CM106 "turquoise" (mic jack, pink, mono channel 1)
- **Microphone:** SF-666 condenser, 3.5mm, on tripod stand
- **sounddevice device:** `pulse` (device 4) — PipeWire routes both via default sink/source
- **Mic position:** 25 cm on-axis, flush with driver

### SF-666 microphone limits

| Parameter | Value |
|-----------|-------|
| Frequency response | 50 Hz – 16 kHz |
| Connection | 3.5mm → CM106 pink mic jack |
| Sensitivity | −30 dB ±3 dB |

- Below 50 Hz: unreliable — capsule rolls off, any readings are noise/artifact
- Above ~15 kHz: capsule resonates before rolling off hard — produces a false peak
  (measured +23 dB at 18.9 kHz in first sweep — this is the mic, not the speaker)
- **Trustworthy measurement window: ~50 Hz – 15 kHz**
- Combined with Faital 3FE25 useful range (Fs = 110 Hz), reliable satellite data: **~110 Hz – 15 kHz**

**PipeWire routing commands:**
```bash
wpctl set-default 132      # route output to T3250W
# CM106 is default source (PW source 57) — no change needed
```

**ALSA mic setup (resets on unplug):**
```bash
amixer -c 1 cset numid=16 0   # PCM Capture Source = Mic (0=Mic, 1=Line, 2=IEC958)
```

**Signal check (2026-03-18, The Smiths playing):**
- Peak: −13.7 dBFS / ~6,770 counts / ~13 bits used
- RMS: −18.1 dBFS
- Healthy level — no clipping, 13 bits of the 16 active

---

## Measurement Notes

### What the measurement captures

A sweep through this chain measures: T3250W amp response + DSE EQ + crossover
high-pass + Faital 3FE25 driver + 1L sealed box response + room + CM106 mic response.

For relative work (comparing positions, box tunings, EQ changes) the mic response
cancels — it's constant between measurements. Absolute SPL accuracy is not needed
for EQ work.

### Crossover interaction

The sub crossover will cause the satellite response to roll off below ~120 Hz.
The sub will appear as a separate acoustic source (different position, different
delay). For satellite characterisation, stay above 200 Hz.

### DSE unknown shape

The DSE processing is a black box. It likely adds a mid-bass shelf to compensate
for the small original satellite enclosures — which no longer apply. Measuring
the system with and without DSE (if bypassable) would reveal its shape. Otherwise
treat the measured curve as "system including DSE" and EQ from that baseline.

### Balance measurement review (2026-03-16)

Six balance runs were made with the CM106 electrical loopback (null cable). Key
findings relevant to acoustic work:

- All three output jacks (green/orange/rear) are electrically identical in response
- Mid-band channel balance ±0.1 dB — negligible
- Low-frequency rolloff below 200 Hz (−12 dB at 20 Hz) is the CM106 ADC/DAC
  electrical path — **not** the speaker or cable. Acoustic measurements will
  show a different (real) rolloff from the Faital + box.
- Line-in L noise floor ~−34 dBFS; R ~−44 dBFS — 10 dB asymmetry in input stage

**Redundant runs:** Of the six, only three were needed — one null orange result
would have sufficed, and the first green run was superseded by the enhanced-format
repeat. A focused test protocol would have been: green (1 run), rear (1 run),
orange (1 run, with ALSA bug already fixed).

---

## Acoustic Measurements (2026-03-18)

Three sweeps taken: 25cm on-axis, 15cm on-axis, 25cm vertical mic orientation.
Log sweep 20Hz–20kHz, BT output to T3250W, CM106 mic input (SF-666).

| File | Position | Peak |
|------|----------|------|
| `measure_chamber_20260318_105600.csv` | 25cm on-axis | −7.3 dBFS |
| `measure_chamber_15cm_20260318_112831.csv` | 15cm on-axis | −5.8 dBFS |
| `measure_chamber_25cm_vertical_20260318_112954.csv` | 25cm vertical | −10 dBFS |

**Notable features (25cm on-axis):**

- **5–6 kHz peak / 6–7 kHz dip** — cone breakup + baffle edge diffraction at
  2nd harmonic (~6.2 kHz). Characteristic of 3" full-range drivers.
- **Wall reflection nulls** — speaker in corner; image sources at side wall
  (d=11cm, null ≈780Hz), back wall (d≈22.4cm, null ≈382Hz), corner image
  (d=25cm, null ≈343Hz) produce comb-filter structure in mid-bass.
- **High-frequency rise above 15kHz** — SF-666 capsule resonance artifact,
  not the speaker.

### SPL calibration

1kHz tone at −18.2 dBFS RMS → phone SPL app = 61 dB at 25cm.

| Parameter | Value |
|-----------|-------|
| Calibration offset | +79.2 dB |
| Formula | SPL = dBFS_rms + 79.2 |
| Sweep level at 25cm | ~61 dBSPL |
| Estimated at 1m (−12dB) | ~49 dBSPL |

At 49 dBSPL the Fletcher-Munson equal-loudness curves show significantly
reduced bass sensitivity — this explains why the sub is turned up.

---

## Response Correction — Results (2026-03-18)

A 4096-tap linear-phase FIR inverse filter was derived from the 25cm on-axis
measurement (correction range 200Hz–9kHz, ±12dB limit). Pink noise was played
alternating flat / corrected every 2 seconds.

**Results: flat preferred both times.**

The corrected version was described as sounding like "a sea shell" — the
500–800Hz range was noticeably over-boosted. This is the wall-reflection null
(comb filter trough measured at the mic position) being inverted. That null
does **not exist at the listening position** — the correction is making the
speaker compensate for a room artefact that vanishes at bed distance.

**Lesson: near-field measurement is not a valid basis for listening-position
room EQ.** The near-field captures driver + box response cleanly but also
includes local room reflections that are specific to that position.

---

## Next Steps — Listening Tests

*"Pink noise 'better' is an odd concept."*

Pink noise ABX is not a meaningful perceptual test for EQ work. Music reveals
what matters. The following experiments are planned:

### 1. Correction only above 6kHz (most interesting)

The 5–6 kHz peak and the steep fall to 7 kHz are real driver characteristics
(cone breakup + diffraction), not room artefacts. They exist at all mic
positions. Applying correction only above 6kHz would:

- Tame the cone breakup peak without over-correcting mid-bass
- Avoid inverting any wall-reflection nulls
- Give a cleaner high-frequency extension

**Target: apply FIR correction ≥6kHz only, AB test with music (not pink noise).**

### 2. Measure from listening position

For meaningful room EQ, the mic must be at the listening position (bed), not
25cm from the driver. At bed distance the wall reflections integrate into a
smoother average response — the comb-filter nulls partially fill in.

### 3. Baffle ears

Adding side panels ("ears") to the baffle would widen the effective baffle
width, pushing the baffle-step and edge-diffraction features to lower
frequencies. Remeasure to see if the 6kHz diffraction dip shifts.

### 4. Super tweeter modulation test (audibility)

Add a super tweeter (6kHz+), drive it on and off every few seconds during
music playback. Perceptual test: is the high-frequency correction audible at
this listening level (~49 dBSPL)?
