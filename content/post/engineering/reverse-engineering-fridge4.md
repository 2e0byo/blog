---
title: "ClosedFridge: RIP OpenFridge"
date: 2021-10-14T12:07:57+01:00
draft: False
categories: ["Engineering"]
bigimg: [{src: "/img/closed-fridge/fridge-burnt.jpg"}, {src: "/img/closed-fridge/fridge-burnt.jpg"}]
---
Refrigerate in peace, OpenFridge.

The hardware OpenFridge was controlling is no more.  It now looks like this:


{{<gallery caption-effect="fade">}}
	{{<figure src="/img/closed-fridge/fridge-burnt.jpg" caption="Heat Exchange">}}
	{{<figure src="/img/closed-fridge/door-burnt.jpg" caption="Door">}}
{{</gallery>}}

Obviously, it should *not* look like this.  What follows is a post-mortem,
because it is worth learning from one's mistakes.

# The final moments of a fridge

After [fixing the defrost](/post/engineering/reverse-engineering-fridge3) I did
not get around to replacing the blown thermal fuse.  The Chinese sensors were
supplied with some kind of wire which breaks if you so much as look at it, and I
was afraid I would knock the wire at some point and crash the system.  Two
nights ago, putting something in the fridge, I knocked one block and wondered if
I had indeed snapped the wire---but I didn't look.  Last night my wife
complained that the fridge was 'melting', at which point I assumed the sensor
had indeed failed, and the fridge had used stale data and failed to cool.  No,
she meant the *fridge* was melting, or more specifically the freezer: the
plastic has melted, flown down into the heat exchange, and then fused in situ.
The whole thing is now one lump and cannot be separated.

The sensor had indeed come detached.  I stripped the broken wire, screwed it
into the block, and rebooted the fridge, at which point it instantly went into
deep freeze mode.  The freezer was sitting at around 50 C, whilst the fridge had
only got up to room temperature.  The element was still hot to the touch, but I
think the defrost had actually finished a while before.  A chicken breast in the
freezer had actually been cooked, and all the (little) food in it was ruined;
but there was still ice in the bottom drawer.

After a few minutes of cooling (with almost no air getting through the blocked
heat exchange to cool the freezer) everything was at a normal temperature and
the food in the fridge could be transferred out (it was all fine), the food in
the freezer binned, the controller hardware stripped away and the fridge removed
from the kitchen.  Then I spent the evening cleaning up, moving things around,
moping around, and wondering how I could be so very stupid.

We had another separate fridge and freezer, and placing them side by side where
the fridge was we now have another work surface and a lot more light in the
room.  My wife professes to prefer it this way, and I don't think she's just
trying to make me feel better.  So all is not too bad: and it could have caught
fire in the night or something horrible.  What follows is an attempt to
understand what *did* happen.

# Analysis

In order to understand how something like this could happen, it's necessary to
look at the architecture of OpenFridge.  The basic coding pattern is to isolate
all hardware interfaces inside HALs which respond to events ('turn on', 'turn
off', 'raise temperature') and take the appropriate actions by themselves.  Thus
the control loop is extremely simple, and is full of statements like this:

```python
if hal.sensors["fridge_temp"] < settings.get("fridge_setpoint") - settings.get("hysteresis"):
    if debugging:
        logger.debug("Fridge under temperature")
    hal.fridge_freezer.refridgerating = False
```

A similar control loop runs for refrigerating, and another for defrosting. The
`fridge_freezer` class has properties---`defrosting`, `freezing`,
`refridgerating` [sic]---and setting them causes it to change state. It then
works out the appropriate state for the hardware and commands that state to a
the HAL it inherits from. Some states are in conflict: you cannot be at once
heating and cooling. The control loop further checks that the commanded state is
not in conflict, forbidding turning on heating and cooling at once, or turning
the compressor on if it has been turned off in the last 5 minutes (thus giving
the gas time to reliquify, preventing undue load when starting the motor). These
double checks exist because the hardware can be directly controlled by the API
for testing purposes, and we still want safeguards.

OpenFridge uses a crude way of getting these synchronous properties into an
asychronous control loop:

```python
class FridgeFreezer(HAL):
    ...
    @property
    def freezing(self):
        return self._freezing
        
    @freezing.setter
    def freezing(self, val):
        if val and self.defrosting:
            raise FridgeError("Not allowed to freeze when defrosting")
        self._freezing = val
        if not val:
            self.set_state("fan", False)
            if not self._refridgerating:
                self.set_state("compressor", False)
                self.set_state("deep_freeze", False)
        else:
            self.set_state("fan", True)
            self.set_state("compressor", True)
            
    def set_state(self, name, val):
        self._state[name] = True if val else False
```

I've simplified a bit: `set_state` belongs on the underlying `HAL`, whereas
`freezing` is a property of the derived `FridgeFreezer`.  Then in the
`hardware_control_loop`, ignoring all the code for mocked control and conflict
checking, we have:

```python
async def hardware_control_loop(self):
    while True:
        self._wdt.feed()
        for name, val in self._state.items():
            if self.achieved_state(name):
                continue
            elif safe_to_achieve_state(name): # dummy
                await self._set_output(name, val)
        await asyncio.sleep(1)
```

This introduces a latency of *at least* 1 second between setting an output and
the hardware responding, but that doesn't matter here.  The wdt is fed from this
loop, as I was mostly interested in keeping this loop alive---after all, if it's
running, we can't get into any horrible state, can we?  Oops.  Having an
`.achieved_state` method is no bad thing, as we can use it in debugging.  But
all this could be much better written using an awaitable event with message,
which is what I now do:

```python
async def _loop(self):
    while True:
        msg = await self._update.wait()
        if msg is self.HEATING_ON:
            self.relay.on()
        ...
```
For this idiom we would need either to re-set the message, or use an queue and
only pop the task when we actually apply it.  But the advantage is
near-instantaneous transition from the synchronous property to the hardware
doing what you want, *despite* having to wait for the event loop to call your code.

## Sensor reading code

Here is the sensor reading code:

```python
async def get_temps()
    sensors = {
        "freezer_temp": None,
        "fridge_temp": None,
        "ext_temp": None,
        "cooler_temp": None,
    }

    for _ in range(5):
        sens.convert_temp()
        await asyncio.sleep(1)
        for sensor in sensors:
            if sensors[sensor]:
                continue
            rom = getattr(config, sensor.replace("temp", "rom"))
            temp = sens.read_temp(rom)
            if temp != 85:
                sensors[sensor] = temp
        if all(x for _, x in sensors.items()):
            break
        await asyncio.sleep_ms(100)
        
    return sensors
```

This code is rather odd, so it needs some explanation.  `sens` is a sensor
object, which communicates with the DS18X20 clones I'm using.  Sometimes those
sensors can fail to read, in which case they return 85.  It is possible to
distinguish this false 85 C from a true reading of 85 C, but since the fridge
was not supposed to get up to 85 C in the first place I simply checked it
directly.  What we do is:

* Trigger all the sensors to measure temperature
* Wait for them to do it
* Get the right rom code and address the bus to query the result for that sensor
* If the reading is 85, ignore it, else assign it
* If all sensors have been read successfully, return them, else keep trying for
  a maximum of 5 attempts.
  
Incidentally, this is not the best style in the world: `all(sensors.values())`
would have been better than `all(x for _, x in sensors.items())`, although
`all(1 for _, x in sensors.items())` would still have been better than what I
wrote; and `for sensor in (x for x in sensors if not sensors[x])` might well
have been more readable than continuing immediately.  But the code as written
worked fine for more than a year.  The trouble is in the line:

```python
temp = sens.read_temp(rom)
```

Detach the sensor and this raises an error, rather than returning 85.  At that
point, following the logic of this function, we should return `None`, so that
comparisons will fail higher up the call stack.  Instead we will raise an
uncaught error and die.  Worse, here is the calling code:

```python
async def temp_loop():
    global sensors
    while True:
        while not mock_temps:
            sensors = await get_temps()
            await asyncio.sleep(5)

        mocking_temps.set()

        while mock_temps:
            await asyncio.sleep(1)
```

Ignore the bit about mocking: that was used by the functional test routines to
simulate different conditions.  The event is used to signal to the test function
that we have entered mocking mode, as depending on the load it can take a while
to get back to the loop, and of course the loop has a 5s delay.

If `get_temps()` raises here, it will propagate back up this loop, which,
without an exception handler, will die.  Now the rest of the event loop will
continue on its merry way with the (stale) values, and the stage is set for the
*denouement*.

I thought of this problem a long time ago, and I now use a much more robust
temperature loop which captures exceptions originating at the hardware level,
but I was holding off touching the OpenFridge code until I'd finished writing
and testing some unrelated HTTP authentication code for the API.

## Defrosting Code

Here is the defrosting code.  It contains only one error:

```python
async def _defrost():
    i = 0
    while i < 60:
        try:
            hal.fridge_freezer.defrosting = True
            break
        except FridgeError:
            await asyncio.sleep(10)
    if not hal.fridge_freezer.defrosting:
        logger.info("Failed to start defrosting: timed out waiting")
        return

    while not hal.fridge_freezer.achieved_state("heaters"):
        await asyncio.sleep(10)

    # defrost till element reaches 10C or 120 minutes is up
    for i in range(60 * 12):
        if hal.sensors["cooler_temp"] >= 2:
            break
        await asyncio.sleep(10)
    await asyncio.sleep(60 * 5)  # reduce thermal stress
    hal.fridge_freezer.defrosting = False
```

Here we try to start defrosting for a maximum of 600s, and give up if we can't.
If we can, we defrost 'until the element reaches 10C or 120 minutes is up'.  The
error is that number: 120 minutes is *far* too long a defrost cycle.  It was
initially half an hour, but I increased it when trying to work out why the
freezer was icing up *whilst the thermal fuse was blown* and thus the heater
wasn't coming on at all.  The gentle heating I *thought* I was seeing was
actually just loss to the environment.  I noticed this as soon as I removed the
blown fuse, but forgot to go and change that constant for a smaller number.
**Had it been only 30 minutes, the Freezer would be absolutely fine**.  **Had it
been 60 minutes, the freezer would likely be mostly intact**.  In point of fact
*two hours* of defrosting---over by time we got to the freezer---cooked a
chicken breast very nicely!

## False Assumptions

When I knocked the wire I immediately thought of the risk, but I didn't worry
about it since I assumed a dead sensor would cause an error to propagate,
rebooting the fridge, at which point failure would be obvious. It would be stuck
in a reboot cycle (with all the hardware off), would fail to light up when
opened, and I could fix the problem and carry on. Nothing could get
over-temperature, because I hadn't damaged the all-important cooler sensor. This
assumption was wrong in several ways:

* I had not in fact implemented the stale reading timeout I since use as
  standard in all my code, so it happily believed the old readings were true.
  
* Whilst the other three sensors functioned perfectly correctly, the code was
  brittle: it couldn't cope with even a single failure.
  
* There was in fact no guarantee that throwing an exception would terminate the
  program.  This is something to bear in mind in `asyncio` code: we are so used
  to the synchronous assumption that throwing an uncaught exception terminates
  everything we rarely think about writing error handlers for unrecoverable
  cases.  Throwing an exception in `asyncio` code does *not* terminate the loop
  by default.
  
This latter point is counter-intuitive.  Consider the following code:

```python
# /tmp/test.py
import asyncio


async def errorfn():
    raise Exception("Error")


async def otherfn():
    await asyncio.sleep(1)
    print("I'm running")


loop = asyncio.get_event_loop()
loop.create_task(errorfn())
loop.create_task(otherfn())
loop.run_forever()
```

What happens if you run this?  The answer is this:

```python
Task exception was never retrieved
future: <Task finished name='Task-1' coro=<errorfn() done, defined at /tmp/test.py:4> exception=Exception('Error')>
Traceback (most recent call last):
  File "/tmp/test.py", line 5, in errorfn
    raise Exception("Error")
Exception: Error
I'm running
```
The worst thing is that I was well aware of this, and part of the work due to be
done on OpenFridge was to add a general bail-out-now function which signalled
that our current state really wasn't good enough.  Of course, this should be
checked in the watchdog, but I was only using the watchdog to detect if the loop
was running at all---because sometimes the whole processor would lock up for (I
suspect) EMI related reasons.

# Morals

OpenFridge controlled an otherwise dead fridge-freezer correctly for over a
year.  I bought this fridge-freezer for £90 around three years ago: since then:

* [the power failed](/post/repairs/hot-to-break-a-freezer) with a full load of food and I had to clean it out
* [the controller failed](/post/engineering/reverse-engineering-fridge) and was replaced with a breadboarded controller
* [the defrosting failed](/post/engineering/reverse-engineering-fridge3) with that controller after it got into a conflicted
  state (heating and cooling at once) and it was extensively re-written to avoid
  conflicts.  (This worked very well and is the basis for all embedded code I've
  written since.)

We got another year out of a junk fridge; I got a lot of experience writing
`asyncio` code in python, and a stable architecture for embedded systems with
`asyncio`; and now we've got a lot more space in the kitchen, and a fair bit
more light.

Still, I'm sad to see it go: a lot of work went into that fridge.  Particularly
for a completely avoidable bug I had actually predicted but hadn't got round to
fixing.

Some takeaways:

* Always pick safe fallback defaults.  120 minutes' defrosting was a stupid
  value.
* Look hard at failure points in asynchronous code.  You need to handle errors
  early, yourself.
* Replace brittle code as soon as you notice the assumptions.
* Don't leave state lying around if the code updating it has died.
* Replace your hardware interlocks *pronto*.  It was alright to run the fridge
  without the fuse for a few days to stop the food going off.  It wasn't alright
  to run it that way for a few *months*.

The lesson is very simple: **always have a hardware interlock**.  A £0.60
thermal fuse would have saved the whole system, and OpenFridge would still be
running today.

