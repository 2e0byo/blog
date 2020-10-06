---
title: 'PIC Development Board'
date: Thu, 19 Jul 2018 17:09:12 +0000
draft: false
categories: ['Electronics']
---

As part of the [Battery Charger](/categories/battery-charger/)
project I need a basic PIC dev board.  I built one a long time ago for
A2 coursework, and I even found the artwork lying around, but the
tracks and pads were too small for hand etching and drilling.  Trying
to open the cad files in KiCad I discovered that they've changed
everything, and half the symbols 'cannot be found'.  I've also
completely forgotten how to use KiCad or schematic capture/Pcb design
software in general: all pointing to a need to redraw. 

After rather too long I proudly examined the result: 

{{<gallery caption-effect="fade">}}
	{{<figure src="/img/2018-07-19-150302-screenshot-png.jpg" caption="">}}
	{{<figure src="/img/2018-07-19-150330-screenshot-png.jpg" caption="">}}
{{</gallery>}}
{{<load-photoswipe>}}

It's incredibly basic: just a few headers, crystal, usb, and a few
resistors and capacitors.  The wiggle in that track is to balance up
the differential length; it's completely pointless at this scale but I
quite liked it.  If you look closely at the schematic you can see what
I didn't: the D+ and D- are wired to the wrong pins.  If you look even
harder you'll notice that not-MCLR is tied to _ground_ not VCC, so the
MPU won't even run.  I didn't notice that; more frustration. 

The Pcb was made the usual way: print to photo paper from a laser,
clean board with wire wool and ethanol, iron on, soak paper, scrub off
with scourer, etch, clean.  Google 'toner transfer pcb' and you can
find a lot of people who know a lot about it.  I half-remembered, but
it worked fine: 

{{<gallery caption-effect="fade">}}
	{{<figure src="/img/dscf10931.jpg" caption="">}}
	{{<figure src="/img/dscf10941.jpg" caption="">}}
	{{<figure src="/img/dscf10951.jpg" caption="">}}
	{{<figure src="/img/dscf10971.jpg" caption="">}}
	{{<figure src="/img/dscf11001.jpg" caption="">}}
	{{<figure src="/img/dscf10981.jpg" caption="">}}
{{</gallery>}}


Does anyone know the concentration of ferric cholride for etching?
I've lost the scrap of paper I used to keep pinned to the board with
it written on, and it seems no-one thinks of niceties like that
online...  in the end I took a ratio, which was too dilute.  But it
etched in the end. Then to assemble, and mount on a bit of ply with an
lcd module, regulator, and a scrap of pcb to develop on: 

{{<gallery caption-effect="fade">}}
	{{<figure src="/img/dscf11031.jpg" caption="">}}
	{{<figure src="/img/dscf11021.jpg" caption="">}}
	{{<figure src="/img/dscf11011.jpg" caption="">}}
{{</gallery>}}

Program:

{{<figure src="/img/dscf11051.jpg" caption="">}}

...and test.  Of course, it didn't work, because of those two idiotic
mistakes.  

Moving the resistor was easy, moving the usb lines more
annoying: 

{{<gallery caption-effect="fade">}}
	{{<figure src="/img/dscf11061.jpg" caption="">}}
	{{<figure src="/img/dscf11091.jpg" caption="">}}
{{</gallery>}}

Plug in the programmer, download the Pinguino bootloader (only
available from a GitHub repository!), plug the usb into the computer
and 'lsusb': it shows up! Artwork and files will go up on my [Gitlab
repository](https://gitlab.com/2e0byo) when I have re-drawn.
