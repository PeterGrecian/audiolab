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

    sub.add_parser("monitor", help="Live curses oscilloscope + FFT")

    args = parser.parse_args()

    if args.command == "devices":
        cmd_devices(args)
    elif args.command == "test":
        cmd_test(args)
    elif args.command == "monitor":
        cmd_monitor(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
