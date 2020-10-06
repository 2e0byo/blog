---
title: 'Poor Man''s Rasberry Pi'
date: Thu, 19 Jul 2018 09:58:16 +0000
draft: false
categories: ['Computing', 'Electronics']
bigimg: [{src: "/img/openwrt-yagi.jpg"}, {src: "/img/dscf1115.jpg"}]
---

Embedded Linux is currently all the rage with little boards like the
Pi running a full-fledged Debian just to flash a few LEDs.  Now
certainly, the Pi would find uses here, but it's hardly cheap.  What
_is_ cheap—or even free—is defunct wireless routers.  They, too, are
embedded systems running Linux.  Unlike the Pi they have on-board wifi
and an ethernet switch; the cpu isn't usually too bad either.  I also
picked a few up for £0.99 on Ebay.  Here's one:

{{<figure src="/img/dscf1118.jpg" caption="">}}

and here's what the board looks like, minus one of the antennas and
with the two antenna outputs connected together—a really questionable
thing to do which seemed a good idea one evening.  I was using a pair
of these for an extended wifi signal with home-made (untuned!) Yagis:

{{<gallery caption-effect="fade">}}
	{{<figure src="/img/dscf1115.jpg" caption="">}}
	{{<figure src="/img/openwrt-yagi.jpg" caption="">}}
{{</gallery>}}


In fact the wifi hardware, at least under OpenWrt, isn't really up to
it: it keeps re-connecting and I never figured out why.  But enter
[OpenWrt](https://openwrt.org/) or these days
[LEDE](https://forum.lede-project.org/) which apparently is to merge
back into OpenWrt and take over the name (in the meantime you should
use LEDE, it's more up-to-date): originally alternative firmware for
the venerable WRT54G, it's now a generic embedded network Linux, and
it 'unofficially' supports these routers.  Installation is
straightforward and on boot you can ssh in and start setting things
up.  The only drawback is disk space, which is in the few tens of MB.
OpenWrt/LEDE uses a strange system with a read-only ultra-compressed
filesystem uncompressed on the fly and a read-write compressed file
system to store only _changes_ to the read-only system to enable
modification (think of it like persistent storage on a memory stick,
if you've ever run linux off a memory stick).  Fortunately these
things have a usb port, and we can put _another_ compressed read-write
filesystem on one, and then use the on-board filesystem to make _that_
the root; we can even mount other filesystems on the memory stick in
an ordinary sensible way.  Even more fortunately, all this
shadowed-file-system stuff is handled transparently by the kernel, and
we don't (usually) have to think about it.

Follow the instructions somewhere like
[here](https://wiki.openwrt.org/doc/howto/extroot) and remember that
there's no point installing anything except usb support before setting
it up as the internal / is only accessed during boot in order to
transfer to the external.

Need more usb devices?  Use a hub: the standard takes care of those.
GPIOs?  Available on the board, and quite a few
[free](https://wiki.openwrt.org/toh/arcadyan/ar7516) on this one.  I
do not know who had the time or energy to trace those… 

One of these formed the basis of a clock I built, which will get
posted here at some point; another is currently on the bench as part
of an internet keepalive, which I should really write up.  They're
really quite flexible, and the best thing is that they're dead cheap.
