---
title: "Thermostat"
date: 2020-10-11T20:44:46+01:00
draft: false
categories: ["Repairs"]
---
{{<load-photoswipe>}}

Our thermostat has an annoying feature.  If you press any button---but
particularly the ‘OK’ button you have to press a lot to change
anything---it reboots.  Worse, it loses everything you’ve just
entered.  Last night it started doing this _without_ my pressing
anything.  I first thought a dead battery might be to blame, but even
with a steady 3V from my bench power supply it refused to work.  I put
it aside, and when it came back on ten minutes later, very _carefully_
increased the temperature till it turned on.  Here is a dud
thermostat:

{{<figure src="/img/thermostat/thermostat.jpg">}}

It looked a nightmare to take apart, but in fact they have helpfully
told you where to lever it open:

{{<figure src="/img/thermostat/helpful.jpg">}}

and indeed it does just pop open, revealing a single board with
everything soldered in place, and two battery clips:

{{<figure src="/img/thermostat/board.jpg">}}

...except the two battery clips, which are a push-contact, and have
corroded:

{{<figure src="/img/thermostat/corrosion.jpg">}}

Something about these clips was niggling, but I turned the soldering
iron on to solder a little bit of wire to each one and have no more
problems.  It wouldn't take.  Not with a lot of scratching, which will
normally make nickel behave itself, nor with a lot of heat and
preheating.  Bother.  Yet it _was_ magnetic: it had to be nickel or
steel.  And both of those have good to moderate solderability...

Wikipedia, of course, has an article on solderability.  And it points
out that _some_ steels---like stainless---have _poor_ solderability.
That was what had been niggling: the clips are stainless steel (though
they've corroded all the same).  I have no acid flux, and whilst I
could buy some tomorrow, it's a bit much just for this job.  So I
cleaned both sides up thoroughly, bent them a bit and put it all back
together.  Whilst we're at it, here's a close up of the ICs used (the
other side of the board is just the lcd, capacitance switches, and
tracks):

{{<gallery caption-effect="fade">}}
	{{<figure src="/img/thermostat/atmel.jpg" caption="It's an Atmega!">}}
	{{<figure src="/img/thermostat/antenna.jpg" caption="'Antenna'">}}
{{</gallery>}}

I can't imagine that 'antenna' works very well.  If you had a large
house, this thing would probably need to be in the kitchen.  But
anyhow, it now works, and doesn't reboot no matter how hard I press
the buttons.  Now to see how long it lasts.
