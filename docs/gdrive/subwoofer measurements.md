Datasheet says: TF1525:

Fs=47R

Re = 5.21R

Qts = 0.59 (total)

Qms = 5.9 (mech) \-\-- fairly high

Qes = 0.66 (electrical) \-\-- dominates - strongly effected by BL -
magnet strength \* coil wire length

Mms=78.2g

Qes = 2 pi Fs Mms Re / (BL\^2)

Vas = 152L

https://en.wikipedia.org/wiki/Thiele/Small_parameters

Qts = Qms Qes / (Qms + Qes) (sum of recipricals) - datasheet is right

Zmax = Re(1 + Qms / Qes)

= 52R - datasheet shows Zmax = 20R at 50Hz

need to find the source of discrepancy.

Fs = 1/ (2 pi \* sqrt( Cms Mms))

Mms is mass of cone + coil + acoustic load

Cms is compliance of suspension

TS parameters can be measured by: Fb - resonant frequency in a sealed
box since

Vas = volume of air as complient/stiff as the driver suspension - can
then calculate Cms given the size of the cone / enclosure etc.

Fb = Fs sqrt(Vas / Vb + 1)

if Vb = Vas, Fb = 1.41 \* Fs - use different boxes/no box to calculate
Vas.

Fs = 47Hz

Fb if Vb = Vas = 66Hz

Fb if Vb = Vas/2 = 81Hz - which is what I have\...

[[http://sound.whsites.net/tsp.htm]{.underline}](http://sound.whsites.net/tsp.htm)

OR

add mass (blu-tak) to cone and measure decrease in resonant frequency.

Fm = sqrt(M / Mm + 1) - to compensate for Vb = Vas would need 78g!

This is odd: 6FE100 Faital pro (Tannoy replacement base driver 6")

Fs 61Hz

Re 5.4R

Qes 0.6

Qms 6.0

Vas 14.1 dm\^3 - 1/10th of the Celestion

The 15" Faital is Vas 126L (Fs=39Hz! - shame it's £150)

It's because the area of the driver is crucial.

T

Here\\s an interesting one:

ERP = Fs/Qes \<50 =\> sealed enclosures \>100 vented

49 / .66 = 70 all rounder

some of the 18 sound subwoofers

35Hz / .25 = 140 -\> vented
