# Electronics Project Ideas

Projects emerging from component stock audit (March 2026).

## BTL Stereo Amp

Low-power bedside amplifier, ~150mW per channel into 8Ω.

**Topology:** Single-supply BTL (bridge-tied load), no output coupling cap.

| Part | Role | Qty |
|------|------|-----|
| MCP6004 | Quad op-amp, gain + BTL phase inversion | 1 |
| BC859B SOT-23 | PNP output emitter followers, 2 per half-bridge | 8 (+2 spare for bias) |
| BC849B SOT-23 | NPN output emitter followers, 2 per half-bridge | 8 |
| 3.3Ω 0603 | Emitter degeneration / current sharing | 16 |
| LM1117-3.3 | 3.3V LDO from transformer | 1 |

Supply: 3V single rail (old transformer → bridge → LDO). Transistors at <15% Vceo — no thermal concerns.

Op-amp inside global feedback loop; output transistors correct for crossover nonlinearity. MCP6004 works at 3V, RRIO.

2 spare BC859Bs thermally coupled to output cluster for Vbe bias spreader.

---

## LED Star Field

Truly random (hardware entropy) twinkling star display. Wall-mounted art piece.

**Components:**
- 20× RGB 3528 SMD LEDs (two brightness grades, foreground stars with colour variation)
- ~90× single-colour LEDs (background field)
- BC848B reverse-biased BE junction → avalanche white noise source
- Amplifier chain → comparator → shift register chain
- Pi drives LED matrix via shift registers, seeded with hardware entropy

**Architecture:** Pi + shift registers for the matrix. Hardware noise source feeds true randomness — not pseudo-random. RGB LEDs used for prominent foreground stars (colour temperature variation: warm/cool). Singles for background.

**Enclosure:** Deep-framed canvas, acrylic cover, components visible.

---

## Electromechanical 7-Segment Clock

Half-metre tall, 4-digit display. Each segment is a toy DC motor snapping between physical stops.

**Status:** Half a digit built and proven — one segment ran continuously for 1 month. All hard problems solved.

**Remaining work:**
- 27 more segments (motors + H-bridges)
- Pi + GPIO expanders (already in stock, ready)
- Field test multi-segment operation before enclosure commitment
- Deep-framed art canvas enclosures with acrylic covers

**Notes:** 28 motors total. Through-hole NPN transistors for H-bridges (bag in stock). 1:120 gearmotor from Rapid stash likely the prototype motor.
