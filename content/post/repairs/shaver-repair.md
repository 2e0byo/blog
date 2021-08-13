---
title: "Shaver Repair"
date: 2020-04-18
draft: false
categories: ["Repairs"]
tags: ["Lockdown work"]
bigimg: [{src: "/img/shaver/in_situ.jpg"}]
---


My father’s electric shaver wasn’t holding charge; he asked if I could
have a look at it and see if the internal battery could be replaced.
Here’s the exploded view:

{{<figure src="/img/shaver/orig.jpg">}}

The green battery is a NiMH, not NiCad as I'd expected.  I suppose
it's not _that_ old.  Which is as well, as I couldn't find any NiCads
in the drawer when hunting around before, and was planning on gutting
it and fitting a LiPo battery and tiny charging module.

I wasn't sure what the battery would turn out to be, but it's actually
just a single 1.~5V cell, with a little 'battery manager' through-hole
IC which implements a current-regulated SMPSU directly from the mains
feed in the base.  The waveform was not very pretty:

{{<figure src="/img/shaver/scope.jpg">}}

But then it _might_ well be sampling the cell voltage in the troughs
(sampling in the peaks is a good deal less reliable, particularly if
charging at anything approaching C).

The question was: would a standard AA fit?  That cell _looks_ AA
sized:

{{<figure src="/img/shaver/battery_comparison.jpg">}}

Hmm.  Probably.  And whilst we're at it, would it work?

{{<figure src="/img/shaver/trial.jpg">}}

Yes, it charged and _held charge_ this time.  Still, that cell's quite
old and I don't know how well it will last. 

Then to cut down a battery pack, as I had no single AA holders and it
needs to be _small_:

{{<figure src="/img/shaver/battery_holder.jpg">}}

and mount it to the board with little bits of wire, and cut away most
of the battery-supporting superstructure in the case to allow enough
space:

{{<gallery caption-effect="fade">}}
	{{<figure src="/img/shaver/in_situ.jpg">}}
	{{<figure src="/img/shaver/cut_carcasse.jpg">}}
{{</gallery>}}

And then try to get it back together.  It was a bit of a squeeze, and
I think I might need to bend the front switch contacts back a bit to
decrease resistance when it next needs opening, but it works, and
holds charge for a good while longer than before.  (Update: a few
months down the line it doesn't really hold charge any more.  Oh
well.  There are plenty more NiMHs in the cupboard: one is bound to be
good.  And at least it's a standard battery now.)
