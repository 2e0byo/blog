---
title: 'Background'
date: Thu, 19 Jul 2018 12:50:36 +0000
draft: false
categories: ['Electronics']
tags: ['orphaned projects', 'Battery Charger']
---

There are lots of 'smart' chargers out there.  Most of them boast that
they can charge your batteries quicker than the competition, and that
a 'smart' algorithm will somehow prevent packing as much current as
possible into a cell in the shortest time from having deleterious
effects.  _Slow_ chargers are harder to come by: there are the cheap
constant-current things you run for a certain amount of time—but if
your batteries are not _absolutely_ dead they _will_ overcharge, and
probably overheat and explode, as mine did.  So not ideal. A few
vacations ago, as a break from reading, I converted an old analogue
ammeter into a basic adjustable-current charger with current and
voltage read-off.  The current regulation is not particularly clever.
It uses the 'trick' I devised for my AS Electronics coursework

{{<figure src="/img/current_reg1.jpg" caption="">}}

Unfortunately I neglected to allow for heat, and this thing drifts
after a while.  It does eventually stabilise, but not much of a
regulator.  But I _also_ had an ARM MBed someone gave me, so I logged
the voltage over USB and graphed it: when the batteries hit charge
there's a negative dV/dt which you can easily see and turn off the
charger.

The usual, sensible solution is to put the resistive element in the
_adj_ line, which avoids power dissipation in it.  But oh well.  Here,
incidentally, is the only picture I can find of the coursework.  It wasn't
pretty, but it
worked. 

{{<figure src="/img/dscf3093.jpg" caption="">}}

It used RDL / RDTL logic for everything; I was being difficult.

# Wishlist

The ability to watch the charge on a computer is very useful: I've
been able to recover some 'dead' batteries by watching the curve at
low current—the 'smart' chargers were terminating on the first 'blip',
long before the battery was full.  Also, one should be able to leave a
charger running and know it'll turn off; and the conditions for doing
so as well as the shape of the charge should be easily modifiable in
software.  I no longer have a laptop with serial or parallel ports, so
communication really needs to be over USB.  Lastly, this is merely a
break from reading, so it should be built easily with things I have on
hand.  So:

*   MPU based (how else?)
*   programmable and logging over USB
*   voltage sense
*   software controllable charging current
*   programmable charge profile

### Hardware

The only MPUs I have on hand are PIC18 devices.  I've written a _lot_
of assembler in the past, and cannot remember any of it.  So it needs
to be higher level than that: I spent a fruitless few hours looking
through usb stacks in C.  All much too complicated to throw together
in a hurry, or refusing to compile: I spent a few more fruitless hours
compiling an old version of
[SDCC](https://sourceforge.net/projects/sdcc/) to compile one of them,
only to discover that I had no development board spare.  Meanwhile
reading is not getting done nor batteries charged. Rooting through old
files I rediscovered the (rather dormant)
[Pinguino](http://www.pinguino.cc/) project.  Arduino-like simplicity
(and no doubt overhead, but who cares?), native USB and LCD libraries,
etc.  That would be nice.  So now I need a development board, and then
at the very least I can have the PIC log over serial like the MBed
used to.  The current regulator, etc, will come later, but the PIC has
two PWM outputs and I can implement at least one more in software if
need be; smooth the voltage and you just need a voltage-controlled
current source of no great stability or power, which is not exactly
unheard of.
