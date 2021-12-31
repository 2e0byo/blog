---
title: "Reverse Engineering a Fridge: Part 3"
date: 2021-04-18T20:04:40+01:00
draft: false
categories: ["Engineering"]
---


OpenFridge has been running the fridge since the first post, which apparently
was in January. In that time:

* The fridge has been very cold (in fact so cold I increased the setpoint to 5
  degrees and moved the sensor to the bottom)
* The freezer has been cold, as desired
* The controller reboots pretty frequently
* The controller sometimes loses the network connection and can't allocate
  enough ram to recover it
* The controller occasionally latches up entirely, even with the software
  watchdog enabled, and refuses to respond to serial commands.
  
I speculate that this latter is caused either by 1. brown out/noise/bouncing
from switching a relay (it almost always happens after switching the compressor
*off*) or 2. noise on the lines causing the ESP32 to enter step/run debugging
mode.  I 'fixed' it by a. adding a 555-based hardware WDT and b. moving the
relay board ground line to separate the grounds.  Unfortunately, the
`RESET_CAUSE` property is not very reliable (reproducible) so I can't really get
any metrics on how often this is triggering.

The ram allocation problem needs looking into.  However, losing wifi isn't the
end of the world, and the uPy core carries on running just fine.

Eventually a new problem occurred:

* The fridge was far too cold.
* The cooler temperature readings made no sense.

I suspected the freezer had become iced up, and indeed, taking it apart showed
frosting comparable to the state at the very beginning.  I thus hacked the
controller to add a manual mode and ran the heaters.  After running them *all
day* and with a DS18B20 replacing the broken cooler thermistor the temperature
climbed as high as 1 degree.  This lead to the following (very obvious)
realisation:

> End of defrost can be detected by a sharp rise above zero on the cooler.

The reason, of course, is that as long as there is ice at the cooler it melts
and tries to maintain... 0 degrees (duh).  So defrosting = heat cooler till it
goes above, say, 5.  And that, clearly, for a much longer period than I was
doing before.

Other than this tweak, several more have been added:

* OpenFridge now outputs csv readings on the `kitchen/fridge/log` channel, which
  can be read by [Serial
  Studio](https://github.com/Serial-Studio/Serial-Studio).  This gives you a
  nice pretty dashboard for free.
* All sensors are now DS18B20s, and I bought some 'waterproof' (clones) off Ebay
  and wired it up properly.
* The Dashboard showed that invalid readings were occurring periodically,
  causing me to dig into the code: there was a race condition between the
  control loop and the log loop, both of which read the sensors.  This is why we
  use a separate sensor-polling loop...
* There is now a REST-full (hopefully) web API using picoweb.  At some point I
  might build a dashboard in e.g. vue.js.  Command/Control over MQTT is
  deprecated.
  
  
Further work to be done:

* Fix the RAM allocation problem.  (pre-compiling will likely sort it)
* Log properly over a long period to see how stable the firmware is.
* Secure the web API (& remove command over MQTT)
* Store some kind of history in ram on the device (using a preallocated buffer)
  so we can print a basic graph on demand.
  
However, *hopefully*, OpenFridge is now reasonably stable.
