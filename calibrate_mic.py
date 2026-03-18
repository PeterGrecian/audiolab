"""Quick mic SPL calibration — plays 1kHz tone, records dBFS, asks for phone SPL reading."""
import numpy as np
import sounddevice as sd
import time, datetime

sr = 48000
freq = 1000
duration = 8.0
amplitude = 0.5

t = np.linspace(0, duration, int(sr * duration), endpoint=False)
tone = (amplitude * np.sin(2 * np.pi * freq * t)).astype(np.float32)

n_record = int(sr * duration)
rec_buf = np.zeros(n_record, dtype='float32')
rec_pos = [0]

def callback(indata, frames, time_info, status):
    end = min(rec_pos[0] + frames, n_record)
    n = end - rec_pos[0]
    if n > 0:
        rec_buf[rec_pos[0]:end] = indata[:n, 0]
        rec_pos[0] = end

print("Hold phone SPL app next to mic. Playing 1 kHz tone in 3s...")
time.sleep(3)
print("Playing!")

with sd.InputStream(samplerate=sr, device=4, channels=1, callback=callback, dtype='float32'):
    time.sleep(0.3)
    sd.play(tone, samplerate=sr, device=4)
    for i in range(int(duration)):
        time.sleep(1)
        print(f"  {i+1}s...")
    sd.wait()
    time.sleep(0.3)

steady = rec_buf[int(0.5*sr) : int((duration-0.5)*sr)]
rms        = np.sqrt(np.mean(steady**2))
peak       = np.max(np.abs(steady))
dbfs_rms   = 20 * np.log10(max(rms,  1e-10))
dbfs_peak  = 20 * np.log10(max(peak, 1e-10))

print(f"\nMic level:  RMS {dbfs_rms:+.1f} dBFS   Peak {dbfs_peak:+.1f} dBFS   ({16 + dbfs_rms/6:.1f} bits)")
print()

spl = float(input("Phone SPL reading (dB slow/RMS): "))
offset = spl - dbfs_rms

print(f"\nCalibration offset : {offset:+.1f} dB")
print(f"Formula            : SPL = dBFS_rms + {offset:+.1f}")
print(f"\nSweep measurement (RMS ≈ −18 dBFS):")
print(f"  At mic (25cm)  : {-18 + offset:.0f} dBSPL")
print(f"  At 1m (−12dB)  : {-18 + offset - 12:.0f} dBSPL")

with open('mic_calibration.txt', 'w') as f:
    ts = datetime.datetime.now().isoformat(timespec='seconds')
    f.write(f"# CM106 mic + SF-666 calibration\n# {ts}\n# Method: 1kHz tone, phone SPL app\n")
    f.write(f"dbfs_rms_measured={dbfs_rms:.2f}\n")
    f.write(f"spl_phone={spl:.1f}\n")
    f.write(f"offset_db={offset:.2f}\n")
    f.write(f"# usage: SPL = dBFS_rms + {offset:.2f}\n")
print(f"\nSaved: mic_calibration.txt")
