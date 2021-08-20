---
title: "Motorcycle Alarm"
date: 2021-08-19T18:45:21+02:00
draft: false
categories: ["Electronics"]
bigimg: [{src: "/img/motorcycle-alarm/alarm-in-situ.jpg"}]
---
Apparently one of the local bike thieves was eyeing up the bike.  Certainly a
car was driving down the road, crawling opposite the bike, and then driving off
again.  Having had one bike nicked I didn't much fancy losing another.  Thus we
had to make the house look a lot more secure in a hurry; and the shops were
closing that evening and not reopening till Tuesday.  For it was the New Year.

## CCTV

External CCTV cameras are still not exactly cheap.  But internal 'cctv/baby
monitor' cameras are now as little as £25---that with wifi.  And ARGOS is open
late... 

Thus a cheapo camera was obtained and stuck inside by a window.  I had to
disable the IR leds, and the 'motion detector' caused a flashing alarm which
blinded the camera by illuminating the window, but it worked.  I left it like
that for a few days while waiting for Screwfix to reopen.

Then I cut a perspex window from some scrap and glued it inside a large
weatherproof box:

{{<gallery caption-effect="fade">}}
    {{<figure src="/img/motorcycle-alarm/window1.jpg">}}
    {{<figure src="/img/motorcycle-alarm/window2.jpg">}}
    {{<figure src="/img/motorcycle-alarm/window3.jpg">}}
    {{<figure src="/img/motorcycle-alarm/window4.jpg">}}
    {{<figure src="/img/motorcycle-alarm/window5.jpg">}}
{{</gallery>}}

Then the camera was placed inside and an LED floodlight wired in via a grommet,
all screwed to a wooden board:

{{<gallery caption-effect="fade">}}
    {{<figure src="/img/motorcycle-alarm/interior1.jpg">}}
    {{<figure src="/img/motorcycle-alarm/interior2.jpg">}}
{{</gallery>}}

I will not include details of how I wired it, but there was a grille directly
below and I steal some current from the lighting main without having to make any
holes in anything.  Which is as well, as this was an emergency and I hadn't
asked the landlord.

{{<gallery caption-effect="fade">}}
    {{<figure src="/img/motorcycle-alarm/installed1.jpg">}}
    {{<figure src="/img/motorcycle-alarm/installed2.jpg">}}
{{</gallery>}}

Since I have no intention of leaving the camera connected to the proprietary
network it came set up on, I set up a basic script rotating 1h files on the main
computer.  If I ever build a file server it can move over there.  At some point
we'll see if the camera isn't vulnerable to a hardware attack.  If it still has
a serial port life should be very easy; I'm pretty certain it's running linux.

## Motorcycle alarm

How do you alarm a motorcycle?  I wasn't content with just making a loud noise:
does anyone really pay any attention to loud noises from alarms?  We all assume
it's a mistake and ignore it.  On the other hand, the bike is *heavy* (at least
300kg) and it is unlikely it could be moved without rolling.  So a wire through
the front wheel would have to be cut.

Here, then, is a basic alarm:

{{<figure src="/img/motorcycle-alarm/alarm-breadboard.jpg">}}

An ESP8266 running micropython monitors the state of a pin pulled low via he
cable.  Cut the cable and it will go high and trigger an alarm state.  In
ordinary operation the device sends an MQTT packet every *n* seconds.  If *k*
packets are not received, an alarm sounds inside the house.  (Originally this
code ran on a laptop; later it was added into the towel heater controller
running in our bedroom.)  The alarm has an 'arm' button which gives you around a
minute to install before triggering if the wire isn't there.

Here is the system installed in a waterproof box protecting the bike:

{{<figure src="/img/motorcycle-alarm/alarm-in-situ.jpg">}}

The snow gives some idea of the kind of problems we encountered:

- Using the onboard linear regulator, battery life is less than a day.  (I
  logged discharge curves and the effect of temperature was evident).
- Wifi is quite battery consuming.  But if you put the chipset to sleep it
  doesn't always reconnect, so you have to increase *k* to handle missed
  packets, decreasing responsiveness.
- The ESP8266 has a deep sleep mode, but it involves rebooting the whole SoC.
  But the onboard code takes around a minute to come online, since at the moment
  I use Peter Hinch's [resilient Async MQTT driver](https://github.com/peterhinch/micropython-mqtt).  So the code should be
  rewritten with boot-sleep-reboot in mind.
  
In practice, it was used in this form for a few weeks, recharging batteries
every day.  Then the box was left with dead batteries for a bit, and then I got
fed up with it and it went back inside the house.  But with some redesign---the
best would be for cutting the cable to *trigger* a power up, so the device could
remain powered down for increments more like 20m, coming online only to report
its battery status and then going down again---it could have the kind of battery
life needed to be useful when we're on holiday.  For now, we've got the
camera---and who *really* wants to nick a >10 year old Pan?

## Postscript

All alarms are defeatable.  This one is quite easy to defeat: the thief just
needs to bridge the wire (I used some Cat5 cable just to make it harder to guess
*what* needed bridging).  If the box is opened it would be quite easy to see how
to do it (although I could easily add a spring-loaded 'box open' alarm).  But it
adds one more layer of nuisance to send someone elsewhere.  When I have finished
restoring the previous stolen bike I mean to build something much more reliable
of the same kind, to give me some certainty that the bike really is there.
