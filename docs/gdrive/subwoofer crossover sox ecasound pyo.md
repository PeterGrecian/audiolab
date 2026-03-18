alternatives to sox could be ecasound or pyo (python) or portaudio (low
level)

http://ajaxsoundstudio.com/pyodoc/api/classes/filters.html

could use sox - use line input and mix to outputs bandpass...

This is the solution if I am doing stereo active passovers

Alsa has this buit in - with .asoundrc files and pcm ldspa upmix
settings

sox manual says...

***Input File Combining -m mix -M merge (channels)***

*[SoX\'s input combiner can be configured (see OPTIONS below) to combine
multiple files using any of the following methods: \'concatenate\',
\'sequence\', \'mix\', \'mix-power\', or \'merge\'. The default method
is \'sequence\' for **play**, and \'concatenate\' for **rec** and
**sox**.]{.mark}*

*[For all methods other than \'sequence\', multiple input files must
have the same sampling rate; if necessary, separate SoX invocations can
be used to make sampling rate adjustments prior to combining.]{.mark}*

*[If the \'concatenate\' combining method is selected (usually, this
will be by default) then the input files must also have the same number
of channels. The audio from each input will be concatenated in the order
given to form the output file.]{.mark}*

*[The \'sequence\' combining method is selected automatically for
**play**. It is similar to \'concatenate\' in that the audio from each
input file is sent serially to the output file, however here the output
file may be closed and reopened at the corresponding transition between
input files - this may be just what is needed when sending different
types of audio to an output device, but is not generally useful when the
output is a normal file.]{.mark}*

*[If either the \'mix\' or \'mix-power\' combining method is selected,
then two or more input files must be given and will be mixed together to
form the output file. The number of channels in each input file need not
be the same, however, SoX will issue a warning if they are not and some
channels in the output file will not contain audio from every input
file. A mixed audio file cannot be un-mixed (without reference to the
orignal input files).]{.mark}*

*[If the **\'merge\'** combining method is selected, then two or more
input files must be given and will be merged together to form the output
file. The number of channels in each input file need not be the same. A
merged audio file comprises all of the channels from all of the input
files; un-merging is possible using multiple invocations of SoX with the
**remix** effect. For example, two mono files could be merged to form
one stereo file; the first and second mono files would become the left
and right channels of the stereo file.]{.mark}*

*[When combining input files, SoX applies any specified effects
(including, for example, the **vol** volume adjustment effect) after the
audio has been combined; however, it is often useful to be able to set
the volume of (i.e. \'balance\') the inputs individually, before
combining takes place.]{.mark}*

*[For all combining methods, input file volume adjustments can be made
manually using the **-v** option (below) which can be given for one or
more input files; if it is given for only some of the input files then
the others receive no volume adjustment. In some circumstances,
automatic volume adjustments may be applied (see below).]{.mark}*

*[The **-V** option (below) can be used to show the input file volume
adjustments that have been selected (either manually or
automatically).]{.mark}*

## *[Effects]{.mark}*

*[In addition to converting and playing audio files, SoX can be used to
invoke a number of audio \'effects\'. Multiple effects may be applied by
specifying them one after another at the end of the SoX command line;
forming an effects chain. Note that applying multiple effects in
real-time (i.e. when playing audio) is likely to need a high performance
computer; stopping other applications may alleviate performance issues
should they occur.]{.mark}*

*[Some of the SoX effects are primarily intended to be applied to a
single instrument or \'voice\'. To facilitate this, the **remix** effect
and the global SoX option **-M** can be used to isolate then recombine
tracks from a multi-track recording.]{.mark}*

***[Multiple Effect Chains]{.mark}***

*[A single effects chain is made up of one or more effects. Audio from
the input in ran through the chain until either the input file reaches
end of file or an effects in the chain requests to terminate the
chain.]{.mark}*

*[SoX supports running multiple effects chain over the input audio. In
this case, when one chain indicates it is done processing audio the
audio data is then sent through the next effects chain. This continues
until either no more effects chains exist or the input has reach end of
file.]{.mark}*

*[A effects chain is terminated by placing a **:** (colon) after an
effect. Any following effects are apart of a new effects chain.]{.mark}*

*[It is important to place the effect that will stop the chain as the
first effect in the chain. This is because any samples that are buffered
by effects to the left of the terminating effect will be discarded. The
amount of samples discarded is related to the **\--buffer** option and
it should be keep small, relative to the sample rate, if the terminating
effect can not be first. Further information on stopping effects can be
found in the **Stopping SoX** section.]{.mark}*

*[**remix** \[**-a**\|**-m**\|**-p**\] \<out-spec\>]{.mark}*

*[out-spec = in-spec{**,**in-spec} \| **0**]{.mark}*

*[in-spec = \[in-chan\]\[**-**\[in-chan2\]\]\[vol-spec\]]{.mark}*

*[vol-spec = **p**\|**i**\|**v**\[volume\]]{.mark}*

*[Select and mix input audio channels into output audio channels. Each
output channel is specified, in turn, by a given out-spec: a list of
contributing input channels and volume specifications.]{.mark}*

*[Note that this effect operates on the audio channels within the SoX
effects processing chain; it should not be confused with the **-m**
global option (where multiple files are mix-combined before entering the
effects chain).]{.mark}*

*[An out-spec contains comma-separated input channel-numbers and
hyphen-delimited channel-number ranges; alternatively, **0** may be
given to create a silent output channel. For example,]{.mark}*

*[sox input.au output.au remix 6 7 8 0]{.mark}*

*[creates an output file with four channels, where channels 1, 2, and 3
are copies of channels 6, 7, and 8 in the input file, and channel 4 is
silent. Whereas]{.mark}*

*[sox input.au output.au remix 1-3,7 3]{.mark}*

*[creates a (somewhat bizarre) stereo output file where the left channel
is a mix-down of input channels 1, 2, 3, and 7, and the right channel is
a copy of input channel 3.]{.mark}*

*[Where a range of channels is specified, the channel numbers to the
left and right of the hyphen are optional and default to 1 and to the
number of input channels respectively. Thus]{.mark}*

*[sox input.au output.au remix -]{.mark}*

*[performs a mix-down of all input channels to mono.]{.mark}*

*[By default, where an output channel is mixed from multiple (n) input
channels, each input channel will be scaled by a factor of Â¹/ n .
Custom mixing volumes can be set by following a given input channel or
range of input channels with a vol-spec (volume specification). This is
one of the letters **p**, **i**, or **v**, followed by a volume number,
the meaning of which depends on the given letter and is defined as
follows:]{.mark}*

*[If an out-spec includes at least one vol-spec then, by default, Â¹/ n
scaling is not applied to any other channels in the same out-spec
(though may be in other out-specs). The -a (automatic) option however,
can be given to retain the automatic scaling in this case. For
example,]{.mark}*

*[sox input.au output.au remix 1,2 3,4v0.8]{.mark}*

*[results in channel level multipliers of 0.5,0.5 1,0.8,
whereas]{.mark}*

*[sox input.au output.au remix -a 1,2 3,4v0.8]{.mark}*

*[results in channel level multipliers of 0.5,0.5 0.5,0.8.]{.mark}*

*[The -m (manual) option disables all automatic volume adjustments,
so]{.mark}*

*[sox input.au output.au remix -m 1,2 3,4v0.8]{.mark}*

*[results in channel level multipliers of 1,1 1,0.8.]{.mark}*

*[The volume number is optional and omitting it corresponds to no volume
change; however, the only case in which this is useful is in conjunction
with **i**. For example, if input.au is stereo, then]{.mark}*

*[sox input.au output.au remix 1,2i]{.mark}*

*[is a mono equivalent of the **oops** effect.]{.mark}*

*[If the **-p** option is given, then any automatic Â¹/ n scaling is
replaced by Â¹/ âˆšn (\'power\') scaling; this gives a louder mix but
one that might occasionally clip.]{.mark}*

*[One use of the **remix** effect is to split an audio file into a set
of files, each containing one of the constituent channels (in order to
perform subsequent processing on individual audio channels). Where more
than a few channels are involved, a script such as the following (Bourne
shell script) is useful:]{.mark}*

*[#!/bin/sh\
chans=\`soxi -c \"\$1\"\`\
while \[ \$chans -ge 1 \]; do\
chans0=\`printf %02i \$chans\` \# 2 digits hence up to 99 chans\
out=\`echo \"\$1\"\|sed \"s/\\(.\*\\)\\.\\(.\*\\)/\\1-\$chans0.\\2/\"\`\
sox \"\$1\" \"\$out\" remix \$chans\
chans=\`expr \$chans - 1\`\
done]{.mark}*

*[If a file input.au containing six audio channels were given, the
script would produce six output files: input-01.au, input-02.au, \...,
input-06.au.]{.mark}*

*[See also **mixer** and **swap** for similar effects.]{.mark}*

failed attempt Linux novices

[[http://sox.10957.n7.nabble.com/implementing-loudspeaker-crossovers-using-Sox-LADSPA-plugins-td5464.html]{.underline}](http://sox.10957.n7.nabble.com/implementing-loudspeaker-crossovers-using-Sox-LADSPA-plugins-td5464.html)

Ecasound:

[[http://rtaylor.sites.tru.ca/2013/06/25/digital-crossovereq-with-open-source-software-howto/]{.underline}](http://rtaylor.sites.tru.ca/2013/06/25/digital-crossovereq-with-open-source-software-howto/)

**ecasound** -z:mixmode,sum -x \\\
-a:pre -i:mysong.mp3 -pf:pre.ecp -o:loop,1 \\\
-a:woofer,tweeter -i:loop,1 \\\
-a:woofer -pf:woofer.ecp -chorder:1,2,0,0 \\\
-a:tweeter -pf:tweeter.ecp -chorder:0,0,1,2 \\\
-a:woofer,tweeter -f:16,4,44100 -o:alsa,surround51:Device

[[http://nosignal.fi/ecasound/Documentation/users_guide/html_uguide/users_guide.html]{.underline}](http://nosignal.fi/ecasound/Documentation/users_guide/html_uguide/users_guide.html)

[[http://nosignal.fi/ecasound/Documentation/examples.html#rtrecording]{.underline}](http://nosignal.fi/ecasound/Documentation/examples.html#rtrecording)

excellent examples:

Jack + JackRack LADSPA (Loinux Audio Developer's Simple Plugin API)

jack is how I get multiple USB cards to work together.
