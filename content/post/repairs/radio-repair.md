---
title: 'Radio repair'
date: Sun, 02 Dec 2018 13:55:22 +0000
draft: false
categories: ['Electronics', 'Repairs']
---


The radio we use in the kitchen to make washing up bearable stopped
working.  Specifically, it wouldn't turn on, but the power LED was
constantly flashing on and then fading off.  What makes me think the
power supply might have died? Lo and behold, after purchasing a cheap
multimeter (it's incredible how cheaply one can get some things now:
in ten years the price of test equipment has plumetted): the '8v'
output was about 3v, and the '15v' output was 0v.  Hmm.  Here's the
very crude power supply:

{{<figure src="/img/dscf1227.jpg" caption="">}}

Switchmode supplies like this one are very simple: on the bottom left
the AC enters, is smoothed, and then rectified so it can be chopped up
into higher frequency (in the KHz with this one---you can hear the
transformer) PWM, passed through a step-down transformer (much more
efficient at higher frequencies) and then rectified and smoothed again
at the target voltage.  The PWM duty cycle is adjusted to keep the
voltage constant.  For some reason surface mount components are still
quite rare on these boards—there are a few resistors and diodes on the
other side, but most things are still through-hole.  Normally I'd like
an oscilloscope to troubleshoot one of these things, but with only a
cheap multimeter I probed a bit, and found that the 15v output was
shorted to ground (obviously enough it was either shorted or
disconnected).  The usual culprit is the electolytic smoothing
capacitor, so I desoldered it, but it was fine.  Looking at the ouput
circuitry a little harder, could it be the diode?  It showed
continuity both ways, and sure enough, with the 15V rectifying diode
out of line the the 8V output worked (at 7.6v, but there we go). In
the short term I removed the diode and ran the 15V output off the 8V,
on the basis that I can't see any use for 15V in a radio except to run
the audio power amplifier:

{{<figure src="/img/dscf1226.jpg" caption="">}}

...and it powered up, decoded enough DAB and started playing:

{{<figure src="/img/dscf1228.jpg" caption="">}}

Not bad!  A replacement Schottky Barrier Diode cost £0.45 on CPC (it
would be less at Farnell proper, I'm sure—but my spare parts are at
home, not here).  So the whole radio, which retailed for a good deal
more than the £10 we got it for from BHF I'm sure, would probably have
been thrown out for a £0.45 diode.  When the new one came I installed
it and the 15V line came back to life (at 15.7V, so much for
regulation). 

{{<figure src="/img/dscf1230.jpg" caption="">}}

I suspect the thing was faulty—the specs allow 150V and 30A breakdown,
and I don't see how one could get even close to that.  But then, I
doubt the switch-on regulation is very well designed. This,
incidentally, is why electronics and practical engineering should be
taught in schools: it's not only economically and environmentally
desirable, it gives one the enjoyment of seeing things come back to
life.  While I was at it, I blocked the cardboard borts on the
speakers, which boom rather a lot: not entirely cured, but a good deal
better.  I've no idea why manufacturers over-port their speakers: I'd
much rather listen to a rather trebly sound than have about a major
third resonate and everything else sound oddly distorted. Tidying up I
realised that this is rather a good photographic summary of student
living:

{{<figure src="/img/dscf1229.jpg" caption="Student Living: books and tools.">}}
