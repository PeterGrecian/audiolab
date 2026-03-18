## Requirements

TV Modest power.

Music room:

Sub woofer. Low pass, v.high power

tweeter. High pass modest power x 2

woofers high pass high power x 2

to complement QUAD 303/33. Might sell them\...don't like the smell :(

tweeter amp could start wotj: sourced from the full range drive signal
at the speaker, switched selection of gain/crossover frequency. +/- 12V.
Use existing xover for woofer.

## Powers and power supplies

Linear for low noise or

pairs of commodity PSUs +/- {5, 12, 19, 26}V Avoid working with mains.

Various powers including 2W and 50W. It is possible to use 4 for each
channel.

It would be interesting to use all the power transistors I have and
experiment with all the configurations:

complementary + sizlaki

2N3044 (.1W)

D882(1W)

MOSFET IRFZ34 (10-50W)

MOSFET others (200W subwoofer)

Should be able to swap out/experiment with for different applications (3
or 4 of them)

## Radiator heatsink.

Class A in winter, class AB in summer :)

Switchable generally. Heat detection/cutout. Dead bug superglued
temperature probes.

Use existing in-use radiator as heatsink

Ruggedize because of exposed location (or does it go behind the rad?)
Hoses for cable protection.

Example temperature derating, D882 3Amp power transistor to 70 degC
infinite heat sink is about 6W

![](media/image1.png){width="5.0in" height="2.6354166666666665in"}

Class 'A' current 1A with an emitter resistor of .5R which will
dissipate a reasonable 500mW

2W into 8R requires V RMS 10V pk-pk etc

OpAmp driving circuit.

1)  simulate

2)  bread board - try out ASAP

3)  protoboard

## Attachment to Radiator

The paint on the rad is a good insulator - probably too good a thermal
insulator.

Couple via oil bath? Non solid state components :)

glue temp sensor to top of transistor

The hotter the radiator, the more useful the heat is, the more bias you
could run...

Bias heavily during evenings and weekends...

One of the problems with Mosfets is that it's difficult to get
rail-to-rail output because the gate voltage is quite large. Maybe 4V.

So +/-44V psu -\> 40V

123W into 8R (pk-pk = 88, rms = pk-pk / 2.8, V\^2/R)

102W

More important at lower voltages. At +/-12V its 9W vs 4W

Solution is to power the drive circuit with an additional 2 x 5V PSUs
which are as cheep as chips.

You might have 3 rails, for OpAmp regulated down from +/- 26V, Drive +/-
26V + +/-5V and Output +/- 26V (LED driver PSU)

Experimenting and simulation, to achieve, n-type MOSFET output
transistors only, would be a big success. Szilaki PNP/ n type mosfet

This case only need one extra 5v on the vcc+.

## Hi Power Resistors:

a novel approach would be to make my own.

These could be nichrome wire based

or graphite pencil lead.

The main benefit would be that high power resistors are expensive to buy
and I would be able to experiment.

Power handling. 1W per cm? 1Amp 1 Ohm\...

contacts: wrap wire

Could be a mosfet. How linear are they?
