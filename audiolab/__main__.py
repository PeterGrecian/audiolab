"""Entry point: python -m audiolab <command> [options]"""

import sys
import argparse


def cmd_devices(args):
    from audiolab.devices import list_devices
    list_devices()


def cmd_test(args):
    """Play a sine tone and record it, print stats."""
    from audiolab.devices import find_cm106
    from audiolab.generator import sine, play
    from audiolab.capture import record, stats
    from audiolab.analysis import fft, peak_frequency

    in_id, out_id = find_cm106()
    if in_id is None or out_id is None:
        print("CM106 not found — using system defaults")

    freq = args.freq
    duration = args.duration
    sr = 48000

    print(f"Generating {freq} Hz sine, {duration}s ...")
    signal = sine(freq=freq, duration=duration, samplerate=sr)

    print(f"Playing on device {out_id}, recording on device {in_id} ...")
    # Simultaneous play + record
    import sounddevice as sd
    recorded = sd.playrec(
        signal.reshape(-1, 1),
        samplerate=sr,
        input_mapping=[1],
        output_mapping=[1],
        device=(in_id, out_id),
        dtype='float32',
    )
    sd.wait()

    s = stats(recorded)
    print(f"\n--- Capture stats ---")
    print(f"  Samples : {s['samples']}")
    print(f"  Peak    : {s['peak']:.4f}  ({s['dBFS_peak']:.1f} dBFS)")
    print(f"  RMS     : {s['rms']:.4f}  ({s['dBFS_rms']:.1f} dBFS)")
    print(f"  Crest   : {s['crest_factor']:.3f}  (sine=1.414, square=1.0)")

    freqs, db = fft(recorded, samplerate=sr)
    pf, pdb = peak_frequency(freqs, db)
    print(f"  Peak freq: {pf:.1f} Hz @ {pdb:.1f} dB")


def cmd_response(args):
    """Log sweep frequency response, printed as ASCII chart."""
    import numpy as np
    import sounddevice as sd
    from audiolab.devices import find_cm106
    from audiolab.generator import sweep

    in_id, out_id = find_cm106()
    if in_id is None or out_id is None:
        print("CM106 not found — using system defaults")

    sr = 48000
    f_start, f_end = args.start, args.end
    duration = args.duration

    print(f"Sweep {f_start}Hz → {f_end}Hz, {duration}s at {sr}Hz ...")
    sig = sweep(f_start=f_start, f_end=f_end, duration=duration, amplitude=0.5, samplerate=sr)

    recorded = sd.playrec(
        sig.reshape(-1, 1),
        samplerate=sr,
        input_mapping=[1],
        output_mapping=[1],
        device=(in_id, out_id),
        dtype='float32',
    )
    sd.wait()

    # Transfer function: H(f) = Y(f) / X(f)
    n = len(sig)
    window = np.hanning(n)
    X = np.fft.rfft(sig * window)
    Y = np.fft.rfft(recorded[:, 0] * window)
    freqs = np.fft.rfftfreq(n, d=1.0 / sr)

    X_mag = np.abs(X)
    # Mask bins where sweep had less than 1% of median energy (avoids endpoint blow-up)
    valid = X_mag >= np.median(X_mag) * 0.01
    H = np.where(valid, np.abs(Y) / np.maximum(X_mag, 1e-10), np.nan)

    # Bin into log-spaced bands
    bands = np.logspace(np.log10(max(f_start, 20)), np.log10(f_end), 60)
    band_db = []
    for i in range(len(bands) - 1):
        mask = (freqs >= bands[i]) & (freqs < bands[i + 1])
        if np.any(mask):
            vals = H[mask]
            vals = vals[~np.isnan(vals)]
            if len(vals):
                band_db.append((np.sqrt(bands[i] * bands[i + 1]), 20 * np.log10(np.mean(vals) + 1e-10)))
            else:
                band_db.append((np.sqrt(bands[i] * bands[i + 1]), None))
        else:
            band_db.append((np.sqrt(bands[i] * bands[i + 1]), None))

    # Normalise to 0 dB at 1 kHz
    ref_vals = [d for f, d in band_db if d is not None and 800 <= f <= 1200]
    ref = np.mean(ref_vals) if ref_vals else 0.0
    band_db = [(f, d - ref if d is not None else None) for f, d in band_db]

    # Print ASCII chart
    bar_width = 40
    db_min, db_max = -30, 6
    print(f"\nFrequency Response (normalised to 0 dB @ 1kHz)")
    print(f"{'Freq':>7}  {'':40}  dB")
    print(f"{'':->7}--{'':->40}----")
    for f, d in band_db:
        if d is None:
            continue
        label = f"{f/1000:.1f}k" if f >= 1000 else f"{f:.0f}"
        filled = int((d - db_min) / (db_max - db_min) * bar_width)
        filled = max(0, min(bar_width, filled))
        zero_pos = int((0 - db_min) / (db_max - db_min) * bar_width)
        bar = list(' ' * bar_width)
        bar[zero_pos] = '│'
        if filled <= zero_pos:
            for i in range(filled, zero_pos):
                bar[i] = '▄'
        else:
            for i in range(zero_pos, filled):
                bar[i] = '█'
        print(f"{label:>7}  {''.join(bar)}  {d:+.1f}")

    print(f"\n         {db_min:+d}dB{' ' * (zero_pos - 6)}0dB{' ' * (bar_width - zero_pos - 3)}{db_max:+d}dB")


def cmd_rolloff(args):
    """Measure rolloff order at the low end using stepped sine tones."""
    import numpy as np
    import sounddevice as sd
    from audiolab.devices import find_cm106
    from audiolab.generator import sine
    from audiolab.capture import stats

    in_id, out_id = find_cm106()
    sr = 48000
    duration = args.duration

    freqs = [10, 15, 20, 25, 30, 40, 50, 60, 70, 80, 100, 120, 150, 200, 300, 500, 1000]

    def measure(f):
        sig = sine(freq=f, duration=duration, amplitude=0.5, samplerate=sr)
        rec = sd.playrec(sig.reshape(-1, 1), samplerate=sr,
                         input_mapping=[1], output_mapping=[1],
                         device=(in_id, out_id), dtype='float32')
        sd.wait()
        trim = int(0.1 * len(rec))
        return stats(rec[trim:-trim])['dBFS_rms']

    print("Measuring 1kHz reference ...")
    ref_db = measure(1000)

    print(f"Stepped sine tones, {duration}s each — measuring RMS level\n")
    print(f"{'Freq':>6}  {'dBFS':>7}  {'vs 1kHz':>8}  {'slope/oct':>10}  {'order':>6}")
    print(f"{'':->6}--{'':->7}--{'':->8}--{'':->10}--{'':->6}")

    prev_f, prev_db = None, None
    results = []

    for f in freqs:
        db = measure(f)
        results.append((f, db))
        rel = db - ref_db

        if prev_f is not None:
            octaves = np.log2(f / prev_f)
            slope = (db - prev_db) / octaves
            slope_str = f"{slope:+.1f} dB/oct"
            order_str = f"~{abs(slope)/6:.1f}"
        else:
            slope_str = order_str = ""

        marker = " <-- -3dB" if abs(rel + 3) < 1.0 else ""
        print(f"{f:>6}  {db:>7.1f}  {rel:>+8.1f}  {slope_str:>10}  {order_str:>6}{marker}")
        prev_f, prev_db = f, db

    # Fit a line to the log-log rolloff region (below 200 Hz)
    rolloff = [(f, db) for f, db in results if f <= 200]
    if len(rolloff) >= 3 and ref_db is not None:
        log_f = np.log2([f for f, _ in rolloff])
        rel_db = [db - ref_db for _, db in rolloff]
        coeffs = np.polyfit(log_f, rel_db, 1)
        slope_fit = coeffs[0]
        order_fit = abs(slope_fit) / 6.0
        print(f"\nBest-fit slope (≤200 Hz): {slope_fit:+.1f} dB/octave → order ≈ {order_fit:.2f}")
        print(f"  1st order = 6 dB/oct, 2nd order = 12 dB/oct")


def cmd_balance(args):
    """Stereo channel balance and crosstalk test — outputs CSV."""
    import csv
    import datetime
    import numpy as np
    import sounddevice as sd
    from audiolab.devices import find_cm106
    from audiolab.generator import sine
    from audiolab.capture import stats
    from audiolab.analysis import thd, balance_freqs

    in_id, out_id = find_cm106()
    sr = 48000
    duration = args.duration
    device_name = args.name
    out_ch = args.out_channels
    amplitudes_dbfs = [-6, -12, -18, -24]
    freqs = balance_freqs()
    modes = [('L_only', [1, 0]), ('R_only', [0, 1]), ('both', [1, 1])]

    total = len(freqs) * len(amplitudes_dbfs) * len(modes)
    eta_s = total * duration
    print(f"Device   : {device_name}")
    print(f"Out ch   : {out_ch}")
    print(f"Points : {len(freqs)} frequencies × {len(amplitudes_dbfs)} amplitudes × {len(modes)} modes = {total} tones")
    print(f"Est.   : {eta_s/60:.1f} min  ({duration}s per tone)")
    print(f"Output : {args.output}\n")

    # Write CSV header immediately so file exists even if interrupted
    fieldnames = [
        'timestamp', 'device', 'out_channels', 'mode', 'frequency_hz', 'amplitude_dbfs',
        'L_rms_dbfs', 'R_rms_dbfs', 'L_peak_dbfs', 'R_peak_dbfs',
        'L_crest', 'R_crest', 'balance_db',
        'L_thd_pct', 'R_thd_pct',
        'L_xtalk_dbfs', 'R_xtalk_dbfs',
    ]
    with open(args.output, 'w', newline='') as f:
        csv.DictWriter(f, fieldnames=fieldnames).writeheader()

    done = 0
    with open(args.output, 'a', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        for amp_dbfs in amplitudes_dbfs:
            amplitude = 10 ** (amp_dbfs / 20)
            for freq in freqs:
                sig = sine(freq=freq, duration=duration, amplitude=amplitude, samplerate=sr)
                trim = int(0.1 * len(sig))

                for mode_name, lr in modes:
                    # Always send a full n_out channel buffer — ALSA hw devices
                    # ignore output_mapping for non-default channels otherwise
                    n_out = sd.query_devices(out_id)['max_output_channels']
                    buf = np.zeros((len(sig), n_out), dtype=np.float32)
                    buf[:, out_ch[0] - 1] = sig * lr[0]
                    buf[:, out_ch[1] - 1] = sig * lr[1]
                    rec = sd.playrec(buf, samplerate=sr,
                                     input_mapping=[1, 2],
                                     device=(in_id, out_id),
                                     dtype='float32')
                    sd.wait()

                    rec_t = rec[trim:-trim]
                    sL = stats(rec_t[:, 0:1])
                    sR = stats(rec_t[:, 1:2])
                    thdL = thd(rec_t[:, 0:1], freq, samplerate=sr)
                    thdR = thd(rec_t[:, 1:2], freq, samplerate=sr)
                    balance = sL['dBFS_rms'] - sR['dBFS_rms']

                    # FFT-based crosstalk: level at driven frequency in the silent channel
                    def fft_bin_db(ch_data, f):
                        n = len(ch_data)
                        win = np.hanning(n)
                        spec = np.abs(np.fft.rfft(ch_data * win)) / (n / 2)
                        bin_hz = sr / n
                        idx = int(round(f / bin_hz))
                        lo, hi = max(0, idx - 2), min(len(spec), idx + 3)
                        rms = np.sqrt(np.mean(spec[lo:hi] ** 2))
                        return 20 * np.log10(max(rms, 1e-10))

                    # Crosstalk: FFT level in the channel that should be silent
                    if mode_name == 'L_only':
                        xtalk_L = None
                        xtalk_R = fft_bin_db(rec_t[:, 1], freq)
                    elif mode_name == 'R_only':
                        xtalk_L = fft_bin_db(rec_t[:, 0], freq)
                        xtalk_R = None
                    else:
                        xtalk_L = xtalk_R = None

                    writer.writerow({
                        'timestamp': datetime.datetime.now().isoformat(timespec='seconds'),
                        'device': device_name,
                        'out_channels': f"{out_ch[0]},{out_ch[1]}",
                        'mode': mode_name,
                        'frequency_hz': round(freq, 2),
                        'amplitude_dbfs': amp_dbfs,
                        'L_rms_dbfs': round(sL['dBFS_rms'], 2),
                        'R_rms_dbfs': round(sR['dBFS_rms'], 2),
                        'L_peak_dbfs': round(sL['dBFS_peak'], 2),
                        'R_peak_dbfs': round(sR['dBFS_peak'], 2),
                        'L_crest': round(sL['crest_factor'], 3),
                        'R_crest': round(sR['crest_factor'], 3),
                        'balance_db': round(balance, 3),
                        'L_thd_pct': round(thdL, 3),
                        'R_thd_pct': round(thdR, 3),
                        'L_xtalk_dbfs': round(xtalk_L, 2) if xtalk_L is not None else '',
                        'R_xtalk_dbfs': round(xtalk_R, 2) if xtalk_R is not None else '',
                    })
                    csvfile.flush()

                    done += 1
                    remain_est = (total - done) * duration
                    xt_str = ''
                    if mode_name == 'L_only' and xtalk_R is not None:
                        xt_str = f"  xtR={xtalk_R:.1f}"
                    elif mode_name == 'R_only' and xtalk_L is not None:
                        xt_str = f"  xtL={xtalk_L:.1f}"
                    print(f"  [{done:>3}/{total}  {done/total*100:3.0f}%  ~{remain_est/60:.1f}min]"
                          f"  {mode_name:<8}  {freq:>7.1f}Hz  {amp_dbfs:>4}dBFS"
                          f"  L={sL['dBFS_rms']:>6.1f}  R={sR['dBFS_rms']:>6.1f}"
                          f"  bal={balance:>+5.2f}dB"
                          f"  THD={thdL:.2f}%/{thdR:.2f}%{xt_str}")

    print(f"\nDone. {done} measurements written to {args.output}")


def cmd_impedance(args):
    """Measure impedance Z(f) via two-channel voltage divider method.

    Circuit (sense resistor on GND side of DUT):
        Amp ─── DUT ─── [R_sense] ─── GND
                    │              │
               line-in L       line-in R
               (V_ref)         (V_sense)

        Z(f) = R_sense × (V_ref(f) / V_sense(f) − 1)

    The CM106 output drives the external amp input.  Both line-in channels
    record simultaneously.  A log sweep is used for efficiency.
    """
    import csv
    import datetime
    import numpy as np
    import sounddevice as sd
    from audiolab.devices import find_cm106
    from audiolab.generator import sweep

    in_id, out_id = find_cm106()
    if in_id is None or out_id is None:
        print("CM106 not found — using system defaults")

    sr = 48000
    r_sense = args.r_sense
    duration = args.duration
    f_start, f_end = args.start, args.end
    n_bands = args.bands
    device_name = args.name
    out_ch = args.out_channel

    print(f"Impedance measurement")
    print(f"  R_sense : {r_sense} Ω")
    print(f"  Sweep   : {f_start}–{f_end} Hz, {duration}s")
    print(f"  Device  : {device_name}")
    print(f"  Out ch  : {out_ch}  (→ amp input)")
    print(f"  In L    : V_ref  (DUT input node)")
    print(f"  In R    : V_sense (R_sense node, I × R_sense)")
    print()

    # Build full N-channel output buffer (ALSA hw requires it)
    sig = sweep(f_start=f_start, f_end=f_end, duration=duration,
                amplitude=0.5, samplerate=sr)
    n_out = sd.query_devices(out_id)['max_output_channels']
    buf = np.zeros((len(sig), n_out), dtype=np.float32)
    buf[:, out_ch - 1] = sig

    print("Playing sweep and recording ...")
    rec = sd.playrec(buf, samplerate=sr,
                     input_mapping=[1, 2],
                     device=(in_id, out_id),
                     dtype='float32')
    sd.wait()
    print("Done.")

    # Check for clipping
    peak_ref = np.max(np.abs(rec[:, 0]))
    peak_sense = np.max(np.abs(rec[:, 1]))
    if peak_ref > 0.95:
        print(f"WARNING: V_ref clipping ({peak_ref:.3f})! Reduce amp output level.")
    if peak_sense > 0.95:
        print(f"WARNING: V_sense clipping ({peak_sense:.3f})! Reduce amp output level.")
    if peak_sense < 0.01:
        print(f"WARNING: V_sense very low ({peak_sense:.4f}). Check connections and R_sense.")

    # Transfer function H(f) = V_sense(f) / V_ref(f), complex
    n = len(sig)
    window = np.hanning(n)
    Y_ref = np.fft.rfft(rec[:n, 0] * window)
    Y_sense = np.fft.rfft(rec[:n, 1] * window)
    freqs = np.fft.rfftfreq(n, d=1.0 / sr)

    # Only use bins where V_ref has meaningful energy (avoids division by noise)
    ref_mag = np.abs(Y_ref)
    valid = (ref_mag >= np.median(ref_mag) * 0.01) & (freqs >= f_start) & (freqs <= f_end)

    H = np.where(valid, Y_sense / np.maximum(Y_ref, 1e-10), np.nan)
    H_mag = np.abs(H)

    # Z = R_sense × (1/H − 1)   (complex, but we report |Z| and phase)
    # Guard against H ≈ 0 (open circuit or bad connection)
    with np.errstate(divide='ignore', invalid='ignore'):
        Z = np.where(
            valid & (H_mag > 1e-6),
            r_sense * (1.0 / H - 1.0),
            np.nan + 0j,
        )

    Z_mag = np.abs(Z)
    Z_phase = np.angle(Z, deg=True)

    # Bin into log-spaced bands
    bands = np.logspace(np.log10(f_start), np.log10(f_end), n_bands + 1)
    results = []
    for i in range(len(bands) - 1):
        f_lo, f_hi = bands[i], bands[i + 1]
        f_mid = np.sqrt(f_lo * f_hi)
        mask = valid & (freqs >= f_lo) & (freqs < f_hi)
        z_vals = Z_mag[mask]
        ph_vals = Z_phase[mask]
        z_vals = z_vals[~np.isnan(z_vals)]
        ph_vals = ph_vals[~np.isnan(ph_vals)]
        if len(z_vals):
            results.append((f_mid, float(np.median(z_vals)), float(np.median(ph_vals))))

    if not results:
        print("No valid impedance data — check circuit and connections.")
        return

    # Find Fs (impedance peak) and Re (minimum Z)
    z_mags = [z for _, z, _ in results]
    fs_idx = int(np.argmax(z_mags))
    re_idx = int(np.argmin(z_mags))
    fs_freq = results[fs_idx][0]
    z_peak = results[fs_idx][1]
    re_est = results[re_idx][1]
    print(f"  Fs (peak)  : {fs_freq:.1f} Hz  |Z| = {z_peak:.1f} Ω")
    print(f"  Re (min)   : {re_est:.1f} Ω  @ {results[re_idx][0]:.1f} Hz")
    print()

    # ASCII chart: log-frequency axis, linear Z scale
    bar_width = 50
    z_min_plot = 0.0
    z_max_plot = max(z_peak * 1.1, 20.0)

    print(f"Impedance |Z| vs frequency  (0 – {z_max_plot:.0f} Ω)")
    print(f"{'Freq':>7}  {'':50}  |Z| Ω")
    print(f"{'':->7}--{'':->50}----")
    for f, z, ph in results:
        label = f"{f/1000:.2f}k" if f >= 1000 else f"{f:.1f}"
        filled = int((z - z_min_plot) / (z_max_plot - z_min_plot) * bar_width)
        filled = max(0, min(bar_width, filled))
        bar = '█' * filled
        marker = ' ← Fs' if abs(f - fs_freq) / fs_freq < 0.05 else ''
        print(f"{label:>7}  {bar:<50}  {z:.1f}{marker}")

    # Write CSV
    if args.output is None:
        ts = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        args.output = f"impedance_{device_name}_{ts}.csv"

    with open(args.output, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['timestamp', 'device', 'r_sense_ohm', 'frequency_hz',
                         'Z_ohm', 'Z_phase_deg'])
        ts = datetime.datetime.now().isoformat(timespec='seconds')
        for f_hz, z, ph in results:
            writer.writerow([ts, device_name, r_sense, round(f_hz, 2),
                             round(z, 3), round(ph, 2)])

    print(f"\n{len(results)} bands written to {args.output}")


def cmd_calibrate(args):
    """Derive L/R input correction curve from a balance CSV dataset.

    Reads a balance CSV (L_only and R_only modes) and computes per-frequency
    correction factors to compensate for line-in channel asymmetry.
    Output is a calibration CSV: frequency_hz, L_offset_db, R_offset_db.
    The convention is: corrected_L_dB = measured_L_dB - L_offset_db
    """
    import csv
    import numpy as np

    input_file = args.input
    output_file = args.output

    # Load relevant rows: L_only and R_only modes, all amplitudes
    rows = []
    with open(input_file, newline='') as f:
        for row in csv.DictReader(f):
            if row['mode'] in ('L_only', 'R_only'):
                rows.append(row)

    if not rows:
        print(f"No L_only/R_only rows found in {input_file}")
        return

    # Collect per-frequency measurements
    from collections import defaultdict
    by_freq = defaultdict(list)
    for row in rows:
        freq = float(row['frequency_hz'])
        mode = row['mode']
        L_db = float(row['L_rms_dbfs'])
        R_db = float(row['R_rms_dbfs'])
        amp_db = float(row['amplitude_dbfs'])
        # Use relative level (measured - amplitude) to remove amplitude effect
        by_freq[round(freq, 1)].append((mode, L_db - amp_db, R_db - amp_db))

    freqs_sorted = sorted(by_freq.keys())
    results = []
    print(f"{'Freq':>7}  {'L_gain':>8}  {'R_gain':>8}  {'Asym':>8}")
    print(f"{'':->7}--{'':->8}--{'':->8}--{'':->8}")

    for freq in freqs_sorted:
        measurements = by_freq[freq]
        # When L_only: L channel receives signal, R should be ~silent (crosstalk)
        # L_gain = median L level relative to amplitude (should be ~0 dB with flat response)
        # R_gain in R_only mode = R channel response
        l_gains = [L for mode, L, R in measurements if mode == 'L_only']
        r_gains = [R for mode, L, R in measurements if mode == 'R_only']
        if not l_gains or not r_gains:
            continue
        l_gain = np.median(l_gains)
        r_gain = np.median(r_gains)
        asym = l_gain - r_gain
        results.append((freq, l_gain, r_gain, asym))
        print(f"{freq:>7.1f}  {l_gain:>+8.2f}  {r_gain:>+8.2f}  {asym:>+8.2f}  dB")

    if not results:
        print("Could not compute calibration — check CSV format.")
        return

    # Reference: set mean of L and R to 0 dB (correction removes only the asymmetry,
    # not the absolute level — absolute level depends on hardware gain settings)
    mean_gain = np.mean([(l + r) / 2 for _, l, r, _ in results])
    print(f"\nMean channel gain: {mean_gain:+.2f} dB (not corrected — only asymmetry removed)")
    print(f"L vs R asymmetry range: {min(a for _,_,_,a in results):+.2f} to "
          f"{max(a for _,_,_,a in results):+.2f} dB")

    with open(output_file, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['frequency_hz', 'L_gain_db', 'R_gain_db', 'L_minus_R_db'])
        for freq, l, r, asym in results:
            writer.writerow([freq, round(l, 4), round(r, 4), round(asym, 4)])

    print(f"\n{len(results)} frequency points written to {output_file}")
    print("Apply correction: corrected_L = measured_L − L_gain, corrected_R = measured_R − R_gain")


def cmd_monitor(args):
    """Curses live oscilloscope + FFT."""
    from audiolab.curses_ui import run
    run(args)


def main():
    parser = argparse.ArgumentParser(prog="audiolab")
    sub = parser.add_subparsers(dest="command")

    sub.add_parser("devices", help="List audio devices")

    p_test = sub.add_parser("test", help="Play tone, record, print stats")
    p_test.add_argument("--freq", type=float, default=1000, help="Sine frequency Hz (default 1000)")
    p_test.add_argument("--duration", type=float, default=2.0, help="Duration seconds (default 2.0)")

    p_resp = sub.add_parser("response", help="Frequency response via log sweep")
    p_resp.add_argument("--start", type=float, default=20, help="Start frequency Hz (default 20)")
    p_resp.add_argument("--end", type=float, default=20000, help="End frequency Hz (default 20000)")
    p_resp.add_argument("--duration", type=float, default=5.0, help="Sweep duration seconds (default 5)")

    p_roll = sub.add_parser("rolloff", help="Measure low-end rolloff order via stepped sines")
    p_roll.add_argument("--duration", type=float, default=2.0, help="Duration per tone seconds (default 2)")

    p_bal = sub.add_parser("balance", help="Stereo channel balance and crosstalk test")
    p_bal.add_argument("--name", default="turquoise", help="Device name tag in CSV (default: turquoise)")
    p_bal.add_argument("--duration", type=float, default=2.0, help="Duration per tone seconds (default 2)")
    p_bal.add_argument("--out-channels", type=int, nargs=2, default=[1, 2], metavar=("L", "R"),
                       help="Output channel numbers (default: 1 2 front, use 5 6 for rear)")
    p_bal.add_argument("--output", default=None, help="CSV output filename (default: balance_<name>_<timestamp>.csv)")

    sub.add_parser("monitor", help="Live curses oscilloscope + FFT")

    p_imp = sub.add_parser("impedance", help="Measure Z(f) via sense resistor and two line-in channels")
    p_imp.add_argument("--r-sense", type=float, default=10.0, metavar="OHMS",
                       help="Sense resistor value in ohms (default: 10)")
    p_imp.add_argument("--start", type=float, default=20, help="Start frequency Hz (default 20)")
    p_imp.add_argument("--end", type=float, default=5000, help="End frequency Hz (default 5000)")
    p_imp.add_argument("--duration", type=float, default=30.0, help="Sweep duration seconds (default 30)")
    p_imp.add_argument("--bands", type=int, default=60, help="Number of log-spaced output bands (default 60)")
    p_imp.add_argument("--name", default="turquoise", help="Device name tag (default: turquoise)")
    p_imp.add_argument("--out-channel", type=int, default=1, metavar="CH",
                       help="Output channel number to amp (default: 1)")
    p_imp.add_argument("--output", default=None, help="CSV output filename (default: impedance_<name>_<timestamp>.csv)")

    p_cal = sub.add_parser("calibrate", help="Derive L/R input correction curve from balance CSV")
    p_cal.add_argument("input", help="Balance CSV file (must contain L_only and R_only mode rows)")
    p_cal.add_argument("--output", default="calibration.csv", help="Output calibration CSV (default: calibration.csv)")

    args = parser.parse_args()

    if args.command == "devices":
        cmd_devices(args)
    elif args.command == "test":
        cmd_test(args)
    elif args.command == "response":
        cmd_response(args)
    elif args.command == "rolloff":
        cmd_rolloff(args)
    elif args.command == "balance":
        if args.output is None:
            import datetime
            args.output = f"balance_{args.name}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        cmd_balance(args)
    elif args.command == "monitor":
        cmd_monitor(args)
    elif args.command == "impedance":
        cmd_impedance(args)
    elif args.command == "calibrate":
        cmd_calibrate(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
