---
title: "Toaster"
date: 2020-10-11T21:01:29+01:00
draft: false
categories: ["Repairs"]
---
{{<load-photoswipe>}}

Somebody has bent the toaster.  It shouldn’t be looking like this:

{{<figure src="/img/toaster/bent1.jpg">}}

It should be looking rather like this:

{{<figure src="/img/toaster/unbent.jpg">}}

Oh well.  It's only mild steel and it bends easily.  Some springs got
out of place too, but it's easy enough to ping them all back,
particularly with the unbent side for comparison.  The hard thing is
normally taking toasters apart---cheapy ones are frequently  held
together with bent metal tabs, which sheer if you try to unbend
them---and of course it's always messy.  But this is a _quality_
toaster.  I got it half price, but if a tree fell on it tomorrow I
would go out and buy the same model.  It has the deepest slots of any
toaster in the local Tescos (and the local Tescos had many
toasters).  I know.  I measured them all.  (Back then nobody bothered
you in shops.  Now of course they'd probably arrest me for touching
the merchandise and spreading the coronavirus.)  And I was going to
award Russel Hobbs full marks for making something with no hidden
screws and only standard heads, until lo and behold! there was _one_
hidden screw with a star head.  Well I have screwdrivers a lot more
exotic than star heads, but that's one black mark against Russel
Hobbs.  So the toaster only scores 19/20.

- - -
Aside---Why, oh why, do they do this?  Everything abounds with hidden 'safety'
screws, weird screw heads, nonstandard threads, inverted genders---why
do you think WiFi equipment doesn't use an SMA plug?  Because it was
felt that the weird 'reverse SMA' it used would discourage users from
plugging in antennas with too high a gain and polluting the
spectrum---so they say. But how does this reasoning hold up?  Reverse
SMA connectors had to be _manufactured_, so of course one can buy a
dozen reverse-SMA-to-SMA adaptors, and any number of aftermarket wifi
antennas with ready-fitted reverse-SMA connectors.  They're no better
than the antennas without---I've seen 24db advertised, and that will
cause a _lot_ of interference if it's not very carefully sited in a
remote area---they're just more expensive.  Did some nutcase
bureaucrat decide that if we couldn't take our toasters apart, we
wouldn't die of electrocution?  And how many die of electrocution from
taking their toasters apart?  If it's more than one a year, I fear we
should keep it quiet---in the current climate they _might_ just lock
the country down until they can find a truly unopenable toaster...
- - -

But anyhow, it was very easy to bend everything back.  But while we've
got this open, what's inside?  I was impressed to see _two_ distinct
control boards, each of which controls _three_ wires running to
elements in the toasting grid (?! Perhaps for level control?  Although
it uses a triac so it could just dim them.  Or are they perhaps in
parallel---but in that case, why not just wire them together?).
There's what is evidently some kind of thermistor, probably for the
defrost and reheat cycles, which is nice to see.  Though I do notice
that this toaster is fairly reliable from cold and from hot, which
suggests it might be applying something cleverer than a timer.  Here
are all the innards from one side:

{{<figure src="/img/toaster/innards.jpg">}}

and here is the MPU:

{{<figure src="/img/toaster/mpu.jpg">}}

Unfortunately, beyond that it's an MPU, I couldn't find anything out
about this chip.  It appears to be something home-grown for the
Chinese market, and the only references I could find were marketing
references largely in Chinese.  But it's definitely an MPU, and quite
a modern one at that.  So there are now two computers in a toaster.
How times do change.
