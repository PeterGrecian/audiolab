"""Audio device enumeration and selection."""

import sounddevice as sd


def list_devices():
    """Print all audio devices, highlighting CM106 units."""
    devices = sd.query_devices()
    hostapis = sd.query_hostapis()

    print(f"\n{'ID':>4}  {'Name':<45}  {'In':>3}  {'Out':>3}  {'API':<12}")
    print("-" * 75)

    for i, d in enumerate(devices):
        api = hostapis[d['hostapi']]['name']
        marker = " <-- CM106" if any(x in d['name'] for x in ("CM106", "C-Media", "ICUSBAUDIO")) else ""
        print(f"{i:>4}  {d['name']:<45}  {d['max_input_channels']:>3}  {d['max_output_channels']:>3}  {api:<12}{marker}")

    default_in, default_out = sd.default.device
    print(f"\nDefaults: input={default_in}, output={default_out}")
    print()


def find_cm106():
    """Return (input_id, output_id) for the first CM106 found, or (None, None)."""
    devices = sd.query_devices()
    input_id = output_id = None
    for i, d in enumerate(devices):
        if any(x in d['name'] for x in ("CM106", "C-Media", "ICUSBAUDIO")):
            if input_id is None and d['max_input_channels'] > 0:
                input_id = i
            if output_id is None and d['max_output_channels'] > 0:
                output_id = i
    return input_id, output_id


def get_device_info(device_id):
    return sd.query_devices(device_id)
