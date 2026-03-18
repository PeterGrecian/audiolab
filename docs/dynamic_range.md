# Dynamic Range — dBFS, Bits, and Audio History

A reference note on how digital level relates to bit depth, and how various
analogue formats compare.

---

## dBFS

**dBFS** = decibels relative to Full Scale. The ceiling is 0 dBFS (clipping);
everything below is negative. It is independent of bit depth — −13.7 dBFS means
the same thing whether the hardware is 16-bit, 24-bit, or float32.

```
dBFS = 20 × log10(amplitude)       amplitude = 10^(dBFS / 20)
```

In sounddevice/PortAudio, signals are represented as float32 in the range ±1.0.
Full scale (1.0) = 0 dBFS. Clipping occurs above 1.0.

---

## Bits used

The number of bits a signal is actively using:

```
bits = 16 + dBFS / 6        (for a 16-bit system)
```

This follows from the **6 dB per bit** rule — each additional bit doubles the
amplitude resolution, which is +6 dB.

| dBFS | Float | 16-bit count | Bits used |
|-----:|------:|-------------:|----------:|
| 0    | 1.000 | 32,767       | 16        |
| −6   | 0.501 | 16,422       | 15        |
| −12  | 0.251 |  8,231       | 14        |
| −13.7| 0.207 |  6,770       | ~13       |
| −20  | 0.100 |  3,277       | 12        |
| −40  | 0.010 |    328       |  9        |
| −60  | 0.001 |     33       |  6        |
| −96  | 0.000016 |      1    |  1 (LSB)  |

At −60 dBFS the signal swings ±33 counts. The top 10 bits of the 16-bit word
are always zero — 10 bits of wasted resolution. The significant bits are at the
**LSB end** (right in standard notation):

```
+33  →  0000 0000 0010 0001
  0  →  0000 0000 0000 0000
-33  →  1111 1111 1101 1111   (two's complement)
         ^^^^^^^^^^  always zero
```

The 16-bit noise floor (1 LSB = −96 dBFS) sets the practical lower limit.
A measurement level of −13.7 dBFS uses ~13 bits, leaving 82 dB of dynamic
range above the noise floor — more than enough for acoustic work.

---

## Dynamic range of analogue formats

The **6 dB/bit** rule makes it easy to compare analogue formats to digital bit depths:

| Format | Dynamic range | Equivalent bits | Notes |
|--------|:-------------:|:---------------:|-------|
| Cassette (bare) | ~50 dB | ~8 bits | Hiss audible on quiet passages |
| Dolby B | ~60 dB | ~10 bits | ~10 dB HF noise reduction |
| Dolby C | ~70 dB | ~12 bits | ~20 dB NR, audiophile cassette |
| FM stereo | ~50–55 dB | ~8–9 bits | Pilot tone + subcarrier eat headroom |
| FM mono | ~60–65 dB | ~10–11 bits | Noticeably cleaner than stereo |
| Vinyl (good pressing) | ~60–65 dB | ~10–11 bits | Limited by surface noise + groove distortion |
| CD | 96 dB | 16 bits | 1644.1: 16-bit / 44.1 kHz |

Vinyl's dynamic range is real but asymmetric — the noise floor (surface noise)
is low (~−65 dB on a clean pressing), but the upper end is limited by groove
distortion, inner-groove tracking, and the cutting lathe's headroom. The numbers
are competitive with Dolby B but the distortion character is different.

Dolby FM existed to bring FM closer to CD quality but never achieved wide
adoption. Dolby B on a good chrome tape with a well-aligned deck genuinely
competed with FM.

The jump from cassette (~8 bits) to CD (16 bits) was an 8-bit / 48 dB improvement
— a factor of 256× in amplitude resolution. Audibly transformative, especially
on quiet classical music where the cassette hiss floor was always present.

---

## Practical measurement levels

For acoustic measurement with the CM106:

- **Target peak:** −12 to −6 dBFS (12–13 bits used) — strong signal, good SNR
- **Headroom:** at least 6 dB before clipping (avoid sustained peaks above −6 dBFS)
- **CM106 input noise floor:** approximately −80 dBFS (analogue noise, not quantisation)
- **Useful dynamic range for measurement:** ~70 dB (~12 bits)

A signal at −13.7 dBFS peak / −18 dBFS RMS is a good working level.
