pulseaudio crossover rack

is just what I need.

It\'s an interactive filter designer which writes to
\~/.config/pulse/default.pa thereby creating a pulse audio device and
filter chain

which can be chosen in pavucontrol as PaXoverRackInput for say Google
Chrome to write to.

Issues are: Using mono output in a filter causes the Input to be
insensitive (choosing a filter as input works)

with 2 outputs pulseaudio has a fit and repeats the same 2 seconds via
the filters.

Possibly a plugin/pulseaudio version mismatch?

pulseaudio is v15.0

plugins are ladspa-t5-plugins

/usr/lib/ladspa

[[https://t-5.eu/hp/Software/ladspa-t5-plugins]{.underline}](https://t-5.eu/hp/Software/ladspa-t5-plugins)

[[https://www.ladspa.org/]{.underline}](https://www.ladspa.org/)

An alternative is to put the plugins into alsa. .asoundrc

Alternatives to the t5 plugins?

The default.pa file format

load-module modulename moduleparameter=value \...

the device is identified as
usb-xxxx_USB_Sound_Device-00.analog-surrout-71 xxxx= udev.id in pactl
info or in lsusb

q: are the plugins available for raspberry pi?

[[http://audio.claub.net/software/LADSPA/Implementing%20Crossovers%20Using%20Ecasound%20and%20LADSPA.txt]{.underline}](http://audio.claub.net/software/LADSPA/Implementing%20Crossovers%20Using%20Ecasound%20and%20LADSPA.txt)

Implementing Loudspeaker Crossovers using Ecasound and ACDf LADSPA
plugins

document version 1.0

Charlie Laub, June 2016

[[http://rtaylor.sites.tru.ca/2013/06/25/digital-crossovereq-with-open-source-software-howto]{.underline}](http://rtaylor.sites.tru.ca/2013/06/25/digital-crossovereq-with-open-source-software-howto)

[[https://ecasound.seul.org/ecasound/]{.underline}](https://ecasound.seul.org/ecasound/)

The ACDf LADSPA plugin can implement a wide variety of first and second
order

filters and EQ.

I reckon delays are used for PAs to compensate for the speed of sound.

Basic 2-way crossover with a multi-channel DAC

ecasound -B:rt -z:mixmode,sum \\

-a:pre -i:mysong.mp3 -pf:pre.ecp -o:loop,1 \\

-a:woofer,tweeter -i:loop,1 \\

-a:woofer -pf:woofer.ecp -chorder:1,2,0,0 \\

-a:tweeter -pf:tweeter.ecp -chorder:0,0,1,2 \\

-a:woofer,tweeter -f:16,4,44100 -o:alsa,surround51:Device

The pre.ecp could be removing ultra and infra sonics. e.g. HPF 10Hz LPF
18kHz

woofer.ecp LPF, tweeter.ecp HPF. The woofer and tweeter chains are added
so that of 4 channels the output is W W T T to the alsa device.

loop I think means processing loop ie, looping over all the data.

to implement loudspeaker crossovers except for one **fantastic
tutorial** by

Richard Taylor, which should be required reading for the ecasound
novice. See:

[[http://rtaylor.sites.tru.ca/2013/06/25/digital-crossovereq-with-open-source-software-howto]{.underline}](http://rtaylor.sites.tru.ca/2013/06/25/digital-crossovereq-with-open-source-software-howto)

![](media/image1.png){width="6.4375in" height="1.53125in"}

[[http://faculty.tru.ca/rtaylor/rt-plugins/index.html]{.underline}](http://faculty.tru.ca/rtaylor/rt-plugins/index.html)

http://www.ladspa.org/cmt/overview.html
