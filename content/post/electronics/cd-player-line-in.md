---
title: 'CD Player Line-In'
date: Tue, 31 Jul 2018 12:11:45 +0000
draft: false
categories: ['Electronics', 'Repairs']
---

This is a very simple project indeed: add a line-in input feeding the
amplifier in my sister's CD/Tape/Radio, which has much better sound
than the 'device' she mainly plays music from.  How hard can it be to
find the amplifier IC and feed in directly?

Taking the thing apart was none too hard, and it's cheap '90s hardware
so all through-hole and single-sided PCB. I found the mode switch,
traced it back to the amplifier, paid careful attention to the pinouts
and soldered a small cable onto one input, the other end going to a
555 'signal generator' kit I had lying around.  Power up: the signal
generator exploded and the lcd backlight died. 

Apparently I'm not so good at tracing PCBs as I thought.  The thing
now was to repair the backlight: it showed no continuity in either
direction so I wondered if it were blown.  Getting at it to find out
required taking the whole front off, in the process of which I lost a
tiny screw and had to find a replacement, and an annoying half hour of
trying not to break everything.  And then the thing was fine… So now I
needed some way to turn it on when in CD mode.  Fortunately I'd taken
everything apart, so it was quite easy to trace the connection to the
CD board and _carefully_ measure the voltage at the requisite pin.  I
found two: 12v and 5.2v, switched by the mode switch.  Trying to trace
back the led driving circuit showed a lot of very complicated things
everywhere; I've no idea why.  A 220R (I think) and the backlight
lights up fine. 

On the way I brushed the probe against the next pin, and the left
speaker crackled.  So I got interested, guessed, and touched another
pin: the right speaker.  Attaching a 3.5mm socket in place of my dead
signal generator confirmed that I got good sound out with about 50%
volume in.  I should probably fit an attenuator, but meh.  What
happens if both CD _and_ external input run?  I expected a simple
mixing, but instead one dominates.  It's probably not a good idea to
risk backfeeding the A/D converter by doing this: really I should add
a switch, and have it illuminate the LCD when the internal CD is
selected.  But after hunting I couldn't find a 3-pole double-throw
switch _anywhere_ and gave up.  So here is the new unit:

{{<gallery caption-effect="fade">}}
	{{<figure src="/img/dscf1128.jpg" caption="Drill">}}
	{{<figure src="/img/dscf1129.jpg" caption="Ugly, but functional.">}}
	{{<figure src="/img/dscf1130.jpg" caption="Completed.">}}
{{</gallery>}}

\[gallery ids="164,165,166" type="rectangular"\] The flexible lamp in
the first photo is jolly handy for this kind of thing, even if
over-using it gives me a headache.  It also uses the worlds silliest
regulator.  Maybe at some point I'll write that up as well…

If you try this with a bit of old audio equipment don't rush in with a
signal: just _brush_ the suspected input pin with a probe or a bit of
wire: if you've got the right pin you'll hear crackling, and if you
haven't it won't blow anything up ;)
