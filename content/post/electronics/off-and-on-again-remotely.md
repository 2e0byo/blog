---
title: '''Off and on again'' remotely'
date: Thu, 02 Aug 2018 08:30:53 +0000
draft: false
categories: ['Computing', 'Electronics']
bigimg: [{src: "/img/dscf1146.jpg"}]
---

The internet in Durham, which was allowing me to use the workstation
there remotely, has gone down; support tell me to 'turn it off and on
again'.  But obviously I can't do that remotely.  Ah well, it wasn't
really needed.  But what if it _were_?  I've run servers over
unreliable wifi links with good uptime before, with a failsafe script
which rebooted everything if it couldn't ping the gateway for too
long—and looking at the logs, sometimes it was needed.  But I can't
reboot the router (and though I'll replace it, there's little
opensource DSL firmware, so I'm never going to be able to reboot
the _modem_).  So what we need is the remote equivalent of pulling the
plug out and putting it back in again. I have a few of those [Poor
Man’s Rasberry
Pi](/post/electronics/poor-mans-raspberry-pi) boards
lying around; one could surely be made to pulse a relay if it can't
ping after a while?  But the only relays I have (mainly rescued from a
faulty boiler) are designed for industrial 24v DC.  I hunted for a
while and then gave up on finding any 12v relays.  Isn't there a
circuit called a voltage doubler?  As usual, SM0VPO has some
[information](http://www.sm0vpo.com/).  I was going to use a 555
timer, but that shamed me: I can still build a discrete
multivibrator—it was one of the first circuits I ever built, after
all.  But first off the relay inline in an extension cord.  Here I
made a completely daft error: the box is about 100% too long, because
I thought the cable exit grommets went the other way round.  But
anyhow, here is how to make a box out of hardboard, that most
intractable thing:

{{<gallery caption-effect="fade">}}
	{{<figure src="/img/dscf1086.jpg" caption="Cut">}}
	{{<figure src="/img/dscf1087.jpg" caption="Mark holes">}}
	{{<figure src="/img/dscf1088.jpg" caption="Drill">}}
	{{<figure src="/img/dscf1089.jpg" caption="Temporary clamp to drill ends">}}
	{{<figure src="/img/dscf1090.jpg" caption="Enlarge holes">}}
	{{<figure src="/img/dscf1091.jpg" caption="Glue ends">}}
	{{<figure src="/img/dscf1092.jpg" caption="Glue up">}}
{{</gallery>}}



Well that wasn't too bad.  One face is screwed with _very_ small
screws into small bits of ply glued on the inside of another face.
Here's the thing all wired up:

{{<figure src="/img/dscf3169.jpg" caption="">}}

Now for the circuitry.  First I built a simple doubler and switched
the whole thing as the load of a bc547 common-emmiter switch.  Then I
found an easily accessible gpio and soldered a length of magnet wire
to it: first problem—it boots up _high._ Now we can't simply invert
that, as the line will go low when the board reboots, and it should be
able to do that without switching the load.  So the first idea was to
AND one inverted and one ordinary GPIO, so I built the rather silly
bit of RT/DL on the LHS of the schematic.  Except that the firmware
goes into failsafe mode if it detects any kind of load on some of the
GPIOs, and one of those I'd picked was clearly one of them.  Worse, in
testing it I managed to short the 12v rail to ground, and something on
the board blew up with a nasty smell.  On reboot it refused to boot; I
hunted for a while and then gave up.  So that board is now scrap
(aren't we glad it's not a Pi!).  For the 99p it cost you couldn't
even get the PSU, so I'm not too heartbroken. A better idea, I
decided, was to use the power LED and the GPIO it _didn't_ mind me
connecting to something.  So the final schematic:

{{<figure src="/img/dscf1149_v1.jpg" caption="">}}

And after logging in remotely, I can turn the relay on and off by
setting gpio 18 low:

{{<figure src="/img/dscf1146.jpg" caption="">}}

Now to take it up to Durham and see if it works up there—and whether
it scares anyone. _Update: _After about two months of constant usage,
I have not had to reset the internet by hand once.  Looking at the
logs, it frequently goes down, but generally resets itself; so far
we've needed about three reboots.  Incidentally, when using this
_manually_ to reboot the internet, one must remember to start screen
and then execute something like `relay_on.sh; sleep 10; relay\_off.sh`
otherwise it _turns off the router you are using to connect_ and you
can't turn it on again, short of unplugging the relay. The board has
plenty of spare cpu power, and is also the DNS server, and keeps track
of the public IP address.
