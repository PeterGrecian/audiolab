"""Curses live monitor: oscilloscope (top) + FFT bar chart (bottom).

Keys:
  q       quit
  +/-     adjust input gain
  1-4     select input channel (if multichannel device)
"""

import curses
import queue
import threading
import numpy as np
import sounddevice as sd

from audiolab.analysis import fft


BLOCK = 1024       # samples per callback chunk
SAMPLERATE = 48000
DISPLAY_SAMPLES = 2048   # oscilloscope window width in samples


def run(args):
    from audiolab.devices import find_cm106
    in_id, _ = find_cm106()
    if in_id is None:
        print("CM106 not found — using default input device")

    q = queue.Queue(maxsize=20)

    def callback(indata, frames, time, status):
        if status:
            pass  # silently ignore under/overflows for now
        q.put(indata.copy())

    stream = sd.InputStream(
        device=in_id,
        channels=1,
        samplerate=SAMPLERATE,
        blocksize=BLOCK,
        dtype='float32',
        callback=callback,
    )

    with stream:
        curses.wrapper(_curses_main, q)


def _curses_main(stdscr, q):
    curses.curs_set(0)
    stdscr.nodelay(True)

    buf = np.zeros(DISPLAY_SAMPLES, dtype=np.float32)
    gain = 1.0

    while True:
        # Drain the queue into our rolling buffer
        while not q.empty():
            chunk = q.get_nowait()[:, 0]
            buf = np.roll(buf, -len(chunk))
            buf[-len(chunk):] = chunk * gain

        key = stdscr.getch()
        if key == ord('q'):
            break
        elif key == ord('+'):
            gain = min(gain * 1.5, 100.0)
        elif key == ord('-'):
            gain = max(gain / 1.5, 0.01)

        h, w = stdscr.getmaxyx()
        osc_h = h // 2 - 1
        fft_h = h - osc_h - 2

        stdscr.erase()

        # --- Oscilloscope (top half) ---
        _draw_oscilloscope(stdscr, buf, row=1, col=0, height=osc_h, width=w)

        # --- FFT (bottom half) ---
        freqs, db = fft(buf, samplerate=SAMPLERATE)
        _draw_fft(stdscr, freqs, db, row=osc_h + 2, col=0, height=fft_h, width=w)

        # Status bar
        peak_db = 20 * np.log10(max(np.max(np.abs(buf)), 1e-10))
        status = f" gain:{gain:.1f}x  peak:{peak_db:.1f}dBFS  [+/-] gain  [q] quit"
        try:
            stdscr.addstr(0, 0, status[:w - 1])
        except curses.error:
            pass

        stdscr.refresh()
        curses.napms(30)   # ~33 fps


def _draw_oscilloscope(stdscr, buf, row, col, height, width):
    mid = row + height // 2
    # downsample buf to width
    indices = np.linspace(0, len(buf) - 1, width).astype(int)
    samples = buf[indices]
    try:
        stdscr.addstr(row - 1, col, f"─── Oscilloscope ({'─' * (width - 18)})"[:width - 1])
    except curses.error:
        pass
    for x, s in enumerate(samples):
        y = int(mid - s * (height // 2))
        y = max(row, min(row + height - 1, y))
        try:
            stdscr.addch(y, x, ord('│'))
            stdscr.addch(mid, x, ord('·'))
        except curses.error:
            pass


def _draw_fft(stdscr, freqs, db, row, col, height, width):
    try:
        stdscr.addstr(row - 1, col, f"─── FFT (20Hz–20kHz) ({'─' * (width - 22)})"[:width - 1])
    except curses.error:
        pass

    # Only show 20Hz–20kHz
    mask = (freqs >= 20) & (freqs <= 20000)
    f_show = freqs[mask]
    d_show = db[mask]

    if len(f_show) == 0:
        return

    # Map to log frequency scale across width columns
    log_f = np.log10(f_show)
    log_min, log_max = np.log10(20), np.log10(20000)
    x_pos = ((log_f - log_min) / (log_max - log_min) * (width - 1)).astype(int)

    # For each column, take the max dB
    col_db = np.full(width, -120.0)
    for xi, d in zip(x_pos, d_show):
        if 0 <= xi < width:
            col_db[xi] = max(col_db[xi], d)

    db_min, db_max = -80, 0
    for x in range(width):
        d = col_db[x]
        bar_h = int((d - db_min) / (db_max - db_min) * height)
        bar_h = max(0, min(height, bar_h))
        for dy in range(bar_h):
            y = row + height - 1 - dy
            try:
                stdscr.addch(y, x, ord('█'))
            except curses.error:
                pass

    # Frequency labels
    for label_freq in [100, 1000, 10000]:
        lf = np.log10(label_freq)
        lx = int((lf - log_min) / (log_max - log_min) * (width - 1))
        label = f"{label_freq//1000}k" if label_freq >= 1000 else str(label_freq)
        try:
            stdscr.addstr(row + height, lx, label)
        except curses.error:
            pass
