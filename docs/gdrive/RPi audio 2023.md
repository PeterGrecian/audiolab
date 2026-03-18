RPi audio 2023

using pusleaudio volume control setting the configuration of the CM106
live sound device to

5.1 output + analog stereo input caused lockup

[[https://cdn-learn.adafruit.com/downloads/pdf/usb-audio-cards-with-a-raspberry-pi.pdf]{.underline}](https://cdn-learn.adafruit.com/downloads/pdf/usb-audio-cards-with-a-raspberry-pi.pdf)

discusses CM109 and CM108 chipsets (C-Media Electronics Inc)

[[https://www.raspberrypi-spy.co.uk/2019/06/using-a-usb-audio-device-with-the-raspberry-pi/]{.underline}](https://www.raspberrypi-spy.co.uk/2019/06/using-a-usb-audio-device-with-the-raspberry-pi/)

Using a USB Audio Device with the Raspberry Pi 4/6/2019

fairly sure alsa is fine. Its pulse audio which is causing the issues.

![](media/image1.png){width="9.197916666666666in"
height="4.645833333333333in"}

Jan 27 12:57:11 raspberrypi kernel: \[ 304.496783\] usb 1-1.1.3.2: new
full-speed USB device number 14 using xhci_hcd

Jan 27 12:57:11 raspberrypi kernel: \[ 304.669584\] usb 1-1.1.3.2: New
USB device found, idVendor=0d8c, idProduct=0102, bcdDevice= 0.10

Jan 27 12:57:11 raspberrypi kernel: \[ 304.669600\] usb 1-1.1.3.2: New
USB device strings: Mfr=0, Product=2, SerialNumber=0

Jan 27 12:57:11 raspberrypi kernel: \[ 304.669612\] usb 1-1.1.3.2:
Product: USB Sound Device

Jan 27 12:57:11 raspberrypi kernel: \[ 304.704488\] usb 1-1.1.3.2:
current rate 30464 is different from the runtime rate 96000

Jan 27 12:57:11 raspberrypi kernel: \[ 304.719524\] usb 1-1.1.3.2:
Warning! Unlikely big volume range (=8065), cval-\>res is probably
wrong.

Jan 27 12:57:11 raspberrypi kernel: \[ 304.719542\] usb 1-1.1.3.2: \[9\]
FU \[Mic Playback Volume\] ch = 2, val = -6144/1921/1

Jan 27 12:57:11 raspberrypi kernel: \[ 304.725506\] usb 1-1.1.3.2:
Warning! Unlikely big volume range (=8065), cval-\>res is probably
wrong.

Jan 27 12:57:11 raspberrypi kernel: \[ 304.725522\] usb 1-1.1.3.2:
\[11\] FU \[Line Playback Volume\] ch = 2, val = -6144/1921/1

Jan 27 12:57:11 raspberrypi kernel: \[ 304.753263\] usb 1-1.1.3.2:
Warning! Unlikely big volume range (=6928), cval-\>res is probably
wrong.

Jan 27 12:57:11 raspberrypi kernel: \[ 304.753281\] usb 1-1.1.3.2: \[8\]
FU \[Mic Capture Volume\] ch = 2, val = -4096/2832/1

Jan 27 12:57:11 raspberrypi kernel: \[ 304.763315\] usb 1-1.1.3.2:
Warning! Unlikely big volume range (=6928), cval-\>res is probably
wrong.

Jan 27 12:57:11 raspberrypi kernel: \[ 304.763338\] usb 1-1.1.3.2:
\[15\] FU \[Line Capture Volume\] ch = 2, val = -4096/2832/1

Jan 27 12:57:11 raspberrypi kernel: \[ 304.777261\] usb 1-1.1.3.2:
Warning! Unlikely big volume range (=6928), cval-\>res is probably
wrong.

Jan 27 12:57:11 raspberrypi kernel: \[ 304.777273\] usb 1-1.1.3.2: \[2\]
FU \[PCM Capture Volume\] ch = 2, val = -4096/2832/1

Jan 27 12:57:11 raspberrypi kernel: \[ 304.786402\] input: USB Sound
Device as Jan 27 12:57:11 raspberrypi kernel: \[ 304.847024\]
hid-generic 0003:0D8C:0102.000B: input,hidraw2: USB HID v1.00 Device
\[USB Sound Device \] on usb-0000:01:00.0-1.1.3.2/input3

Jan 27 12:57:11 raspberrypi mtp-probe: checking bus 1, device 14:
\"/sys/devices/platform/scb/fd500000.pcie/pci0000:00/0000:00:00.0/0000:01:00.0/usb1/1-1/1-1.1/1-1.1.3/1-1.1.3.2\"

Jan 27 12:57:11 raspberrypi mtp-probe: bus: 1, device: 14 was not an MTP
device

Jan 27 12:57:11 raspberrypi systemd-udevd\[1069\]: Process
\'/usr/sbin/th-cmd \--socket r/var/run/thd.socket \--passfd \--udev\'
failed with exit code 1.

Jan 27 12:57:11 raspberrypi mtp-probe: checking bus 1, device 14:
\"/sys/devices/platform/scb/fd500000.pcie/pci0000:00/0000:00:00.0/0000:01:00.0/usb1/1-1/1-1.1/1-1.1.3/1-1.1.3.2\"

Jan 27 12:57:11 raspberrypi mtp-probe: bus: 1, device: 14 was not an MTP
device

Jan 27 12:57:11 raspberrypi pulseaudio\[746\]: W: \[pulseaudio\]
alsa-mixer.c: Volume element Speaker has 8 channels. That\'s too much! I
can\'t handle that!

Jan 27 12:57:11 raspberrypi pulseaudio\[746\]: W: \[pulseaudio\]
alsa-mixer.c: Volume element Speaker has 8 channels. That\'s too much! I
can\'t handle that!

Jan 27 12:57:11 raspberrypi pulseaudio\[746\]: W: \[pulseaudio\]
alsa-mixer.c: Volume element Speaker has 8 channels. That\'s too much! I
can\'t handle that!

Jan 27 12:57:15 raspberrypi kernel: \[ 308.649405\] retire_capture_urb:
261 callbacks suppressed

Jan 27 12:57:15 raspberrypi pulseaudio\[746\]: W: \[alsa-sink-USB
Audio\] alsa-util.c: Got POLLNVAL from ALSA

Jan 27 12:57:15 raspberrypi pulseaudio\[746\]: W: \[alsa-sink-USB
Audio\] alsa-util.c: Could not recover from POLLERR\|POLLNVAL\|POLLHUP
with snd_pcm_prepare(): File descriptor in bad state

Jan 27 12:57:15 raspberrypi kernel: \[ 309.047402\] usb 1-1.1.3.2: USB
disconnect, device number 14

Jan 27 12:57:15 raspberrypi kernel: \[ 309.047452\] usb 1-1.1.3.2:
cannot submit urb (err = -19)

Jan 27 12:57:15 raspberrypi pulseaudio\[746\]: W: \[alsa-source-USB
Audio\] alsa-util.c: Could not recover from POLLERR\|POLLNVAL\|POLLHUP
and XRUN: Input/output error
