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
                    stereo = np.column_stack([sig * lr[0], sig * lr[1]])
                    rec = sd.playrec(stereo, samplerate=sr,
                                     input_mapping=[1, 2],
                                     output_mapping=out_ch,
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
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
