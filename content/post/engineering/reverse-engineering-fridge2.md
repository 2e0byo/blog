---
title: "Reverse Engineering a Fridge: Part 2"
date: 2021-01-21T15:42:44Z
draft: false
categories: ["Engineering"]
---
{{<load-photoswipe>}}
# Hardware

So we have five mains circuits: the lamp, the fan, the heaters, the
compressor, and the 'superfreeze' button, which I think just adds the
starting coils permanently.  The original controller only switches
four of these on the board (the superfreeze is a manual switch), and
uses triacs for all except the compressor, which has a 10A relay.  Of
course, that requires the controller to be attached to the AC neutral,
which isn't a great idea with exposed hardware like a prototype
balanced on a fridge.  So we'll use relays for everything: three
low-current relays, and two great big 15A monsters, all from the
microwave control board.

I wired these all up on protoboard, with back-emf diodes and BC547s as
switches.  To save current they are switched with a resistor bypassed
by a capacitor: on connection the capacitor dumps full current on the
relay, but then charges up and effectively disappears, so changing the
resistor value allows us to set a lower holding current.  These were
picked by feel: 10k for the little relays, which seem fine with that
(remember we're talking 24v!).  One little relay is most over-used and
needed the resistor shorting out, and even *then* he did not make a
happy clicking sound like his friends.  I think he may be growing old,
but we'll use SSR in the final thing anyhow.

Here is the relay board:


{{<gallery caption-effect="fade">}}
	{{<figure src="/img/20210121_121502.jpg" caption="">}}
	{{<figure src="/img/20210121_121445.jpg" caption="">}}
{{</gallery>}}

And here's the rest of the hardware:

{{<gallery caption-effect="fade">}}
	{{<figure src="/img/20210121_121435.jpg" caption="">}}
	{{<figure src="/img/20210121_121524.jpg" caption="">}}
{{</gallery>}}



The rest of the hardware was fairly straightforward.  An ESP32, on a
generic Chinese dev board, drives the relays.  There are at present
three DS18B20 temperature sensors: two to calibrate the thermistors, but I
plan on removing them, and one to measure the room temperature, since
it might be interesting to know what difference very cold or hot days
make.  The thermistors are in a potential divider connected to the
ESP32's famously bad ADC.  A 100nF capacitor partly mitigates the ADC;
we don't need much resolution for this so we only read at 9-bits, and
it's pretty much useable.

# Firmware

The ESP32 is running MicroPython, which is brilliant.  Development is
measured in minutes, not hours, and compiling is unneeded, plus I can
actually read the final code.  Of course all this comes at a price in
terms of speed and current draw, but neither matter much here.  We can
also use asyncio, which saves having to think about the loop.

I first wrote a basic hal (`hal.py`) to turn things on and off.  The
light is handled directly in the hal, as a callback to Peter Hinch's
excellent async switch code.

With that the the fridge could be remote controlled over wifi using
`webrepl`, which is an amusing gimmick but not much use.  So we use
MQTT and have it respond to commands sent to
`kitchen/fridge/CommandControl`.  Simultaneously all the temperatures
are logged every five seconds over MQTT.

Now it was just a matter of picking resistor values to get a decent
range on the ADC, which took a bit of trial and error, and then
calibrating the thermistors against the DS18B20s.  I cable-tied one to
the thermistor attached to the heat exchange and ran some
experiments.  I'm not sure how hot you're supposed to take the
exchange, but 30 degrees seemed reasonable.  Just as well, as the
thermistor hits 0 at about that value.

Here is a graph of my first run, showing 511-thermistor value against
time and temperature against time:

{{<figure src="/img/raw-cal1.png.jpg" caption="">}}

Hmm.  That's not very linear.  Here's the calibration curve:

{{<figure src="/img/func-cal1.png.jpg" caption="">}}

I can certainly make a table of interpolations out of this, but it's
going to be big.  Let's try again:


{{<gallery caption-effect="fade">}}
	{{<figure src="/img/raw-cal2.png.jpg" caption="">}}
	{{<figure src="/img/func-cal2.png.jpg" caption="">}}
{{</gallery>}}

Which has very different raw values.  Here they are on top of each
other:

{{<figure src="/img/dual-func-cal.png.jpg" caption="">}}

Maybe the problem is thermal lag, even though the calibrating sensor
is attached to the thermistor?  In the last test I used the compressor
(with 'deep freeze') to lower the temperature, and then the fan to
warm it up (with the compressor off), and then the heater.  I did the
same for this test, but rather than switching to heaters at -4 I went
all the way up to zero.  I also left the fan on to slow the heating
effect, and opened the freezer door so as not to heat up the
enclosure.  (I turned the fan off at 15 degrees, as I was getting
impatient.)

How good does it need to be?  Not necessarily very good, though that
would be nice.  I don't mind leaving the sensors in permanently if
need be.

After a bit of thought, I aggregated all the data, did a polynomial
fit with numpy, excluded everything too far from the fit, did
*another* fit on the resultant data, and generated a 3rd-order
polynomial which fit the reduced data nicely:

{{<gallery caption-effect="fade">}}
	{{<figure src="/img/cal-agregate.png.jpg" caption="">}}
	{{<figure src="/img/cal-agregate-fit.png.jpg" caption="">}}
{{</gallery>}}

The only trouble is that this is backwards.  We want to go *from*
sensor reading *to* temperature.  The coefficients were horrendous,
and the rearrangement (courtesy of Wolfram Alpha) was horrible, so I
did the fit backwards.  It needed a 6th-order polynomial to fit, but
when I did a fit *on the previous fit* I got something which lay
neatly---enough---on top of the data:

{{<figure src="/img/cal-agregate-fit2.png.jpg" caption="">}}

The only problem is that we have to solve a 6th-order polynomial on an
MCU.  Given that there are only 512 possibly values, a lookup table
might be better, but then this MCU runs at 160MHz and doesn't seem to
care.  Of course there's no numpy for MicroPython (at least, not for
doing curve fitting) so we compute the output manually:

```python
def eval_poly(x, coeffs):
    """
    Evalulate polynomial.

    Coeffs should be passed little-endian, ie coeffs[0] = x^0.
    """
    y = 0
    for i, coeff in enumerate(coeffs):
        y += coeff * x ** i
    return y
```
In Cpython that returns slightly different values from numpy.
Presumably numpy implements this stuff in c.

When I have enough data I shall do the same for the fridge
thermistor.  For now I only have laggy noise:

{{<figure src="/img/laggy_noise.png.jpg" caption="">}}

These thermistors are very non-linear!  On the other hand, it seems
like they picked a thermistor which would work well at freezing
temperatures, which makes sense.


# Discoveries

- The compressor has a manual timeout after it is switched off,
  preventing you from turning it on again for around 5
  minutes. (Possibly temperature based?)
  
# Control logic

We control the fridge and freezer separately.  If the fridge is too
warm, we turn the compressor on.  If it is too cold, we turn the
compressor off.  If the freezer is too cold, we do nothing (as it
doesn't much matter anyhow).  But we could turn the heaters and fan
on.  But if it is too warm, we turn the fan + compressor on.

Every time we turn the compressor off we start a ten minute timer
which disables it until it elapses, to save wear and tear, just in
case the starter relay *doesn't* do so.

Every twelve hours we defrost, by running for five minutes or until
the cooler reaches 10 degrees.  Additionally, if the freezer
temperature fails to fall by 2 degrees in fifteen minutes (this might need
adjusting), we guess that it needs defrosting and run a panic defrost,
stopping the current cooling cycle.  If it fails to fall by one degree
in eight minutes, we turn on the deep freeze.  Hopefully this logic
would sooner or later catch an ice build up, but we can always review
it later---or indeed, command a manual defrost over mqtt.

The fridge temperature is taken from the fridge thermistor.   The
freezer temperature is taken from a DS18B20 on a bit of flat cable,
stuffed in a drawer.  The cooler temperature is taken from the
attached thermistor.  (I suspect they guessed the fridge temperature
by running the fan for a bit and then sampling the cooler.  This would
fail if the thing were awfully iced up, as it was this time.)  The
room temperature is taken from another DS18B20 on top of the fridge.
Whilst I plan to box up the controller and redeem the power supply
(currently it's running from a dual lm317 supply I built as a child),
I'll leave it separate and on top---that way it's easier to get at.

Everything can be remotely controlled, and everything is logged to
`kitchen/fridge/log` and `kitchen/fridge/temperature` so I should be
able to get some data on efficiency and hopefully tune it.

# Limitiations

At present the DS18B20s sometimes fail to convert (gives 85).  I've
reduced the frequency by trying repeatedly, but give up after 3
attempts (might need to wait longer).  The graphing code just ignores
any 85s.  I suspect the onboard 3.3v regulator is struggling to output
enough current to power the thing parasitically.  Additionally, I need
to check that DQ is properly pulled high in the waiting time: if it
isn't, then all the current is coming via the 1k pull up, which is
likely not enough.  The driver _ought_ to put the pin in output mode
and drive it high for the duration, but without a datalogger on
it/examining the source code there's no way to tell.

# Further developments

I should like to add a buzzer, so we can warn if the door is left open
or the device goes out of temperature range.  I'm also not quite sure
what happens at the moment if the wifi goes down: I suspect the
controller will be fine, but I need to test it (the risk is more a
buggy connection which never gets established).  And, of course, it
should be in a proper box so nobody goes a-gefingerpoken, which could
be interesting as nearly everything is at mains potential.

And, most importantly, we just need to get a lot more data so we can
characterise it a bit better.

```json
{"msg": "start cooling", "msg_id": 11, "timestamp": "2021-1-22 19:43:11"}
//response to status query
{"msg": "{'heaters': False, 'fan': False, 'deep_freeze': False, 'compressor': False, 'light': False}", "msg_id": 17, "timestamp": "2021-1-22 19:43:33"}
{"msg": "Turning compressor on", "msg_id": 57, "timestamp": "2021-1-22 19:47:34"}
{"msg": "Turning compressor and fan on", "msg_id": 58, "timestamp": "2021-1-22 19:47:34"}
//response to status query
{"msg": "{'heaters': False, 'fan': True, 'deep_freeze': False, 'compressor': True, 'light': False}", "msg_id": 74, "timestamp": "2021-1-22 19:49:3"}
{"msg": "Deep freezing as freezing slowly", "msg_id": 88, "timestamp": "2021-1-22 19:50:27"}
//response to status query
{"msg": "{'heaters': False, 'fan': True, 'deep_freeze': True, 'compressor': True, 'light': False}", "msg_id": 202, "timestamp": "2021-1-22 20:2:2"}


```
