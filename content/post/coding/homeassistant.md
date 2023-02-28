---
title: Migrating Home Assistant (and thoughts on over-engineering)
date: 2023-02-28T11:19:25Z
draft: false
categories: ["Coding"]
---

Home Automation is largely a gimmic.  Even the founder of Home Assistant writes
[blog posts](https://www.home-assistant.io/blog/2016/01/19/perfect-home-automation/)
pointing out that turning the lights on from your phone is pretty pointless,
except for showing off (not that I've *ever* turned a light on from my phone to
show off...).  [Another](https://danielbkr.net/reasons-for-home-automation/) of
these posts tries to think of a *useful* smart light and comes up with:

> Imagine a brave new world where you walk into a room and the light is already
> on, as you have naturally come to expect after years of living with such a
> technology. When you leave the room the light is turned off and nobody even
> takes note of it because it is completely taken for granted. This leaves you
> more mental capactiy to worry about other things.

Hmm.  What about if you subtract all the mental energy spent setting the thing
up in the first place?  Is it really less than all that energy we burned
thinking about turning lights on?

But this isn't the point.  Home Automation is mostly a gimmic, but there's
nothing wrong with gimmics---providing they don't actually get in the way and
prevent you e.g. turning the lights on with the switch.  Everyone needs a hobby.

Anyhow, I didn't set out to do Home Automation.  Above all not with Home
Assistant.  But we do have a towel radiator---because otherwise the towels don't
dry and go musty---so naturally I stuck a timer on it for when we forgot to turn
it off.  But that timer was (because I am lazy) written in micropython and
running on an esp8266, and to justify the use of a whole SoC with wifi and
bluetooth to turn a radiator on for 45 minutes I gave it a REST-like API.  Then
I thought it would be cool (see: all the adjectives are actually aesthetic, we
only pretend otherwise) if the radiator turned itself on the morning, say half
an hour before we got up, so the towels were warm.  So I wrote a whole
scheduling backend (with CRUD) which matched arbitrary conditions like 'every
third tuesday when the month is even', because writing code is much more
addictive than actually *using* it.  Of course, this implementation had bugs
(although being in Python I could at least write tests easily to find them), but
when I'd ironed them out I found it was only ever used with one rule---which I
could have hard coded---which was wrong half the time anyhow.  It was also a
nuisance to change, because although I *like* curl, I had to read the source
every time to remember what I'd called the parameters.  And of course they were
different from the automatic watering system, which *also* has an HTTP api, and
the fridge (before that [died](/post/engineering/reverse-engineering-fridge-4)).
Now I *like* reading source---it's a good way to  make sure refactoring
actually happens, and nothing is more embarassing than a bad hack after two
years---but still.

Then our daughter came along, and meanwhile Mr. Putin invaded Ukraine and the
gas bills went through the roof.  So I wanted to know that the room was at a
reasonable temperature overnight without just setting the heating up for the
whole house.  And that radiator timer had, by now, gained a DS18X20 (fake) and
had an api.  So I could just poll it and graph.  But then how to display the
results?  Previously I had just built a quick website.  But...

At this point I decided to bite the bullet and have a look at Home Assitant
again.  My first impressions were the same as before: it's horrendously
over-engineered, and popular in the wonderful (but frustrating) community of
people who post bug reports of 'it doesn't work!  So I changed a billion things,
but it still doesn't work!'  In other words, it's as bad as the Raspberry Pi
for signal/noise ratio; or in still other words, it's genuinely popular.  But
yes, you *can* just drag-and-drop a 'sensor' component and you get a website
with graph.  I'm rubbish at graphic design, so it even looks better than
anything I'd make.  Unfortunately my random hardware isn't HA compatible, so I
need to write an integration.

There are several hundred pages of docs, which start by telling you about the
state machine at the heart of HA. (!)  There are also a billion ways to do
everything.  Unfortunately the people who wrote HA *really* love writing
code---so they do so even when they don't need to.  Every sensor, for instance,
is ultimately a subclass of `Sensor`, which makes sense, and the base class has
a bunch of attributes which then got overriden.  Fair enough.  But these are
allowed to be properties *or* attributes.  Attributes are named `_attr_thing`
and the base class has---for *every* attribute---a property consisting of:

```python
@property
def thing(self):
    return self._attr_thing
```

Yep.  They didn't just override `__getattr__`.  Now multiply that by the whole
codebase...

Then there seem to be half a dozen ways of registering a component, doubled by
async and non async functions (where we duplicate python's syntax by requiring
all async functions to be called `_async_thing` coz introspection is for
losers[^1]); and they're all called things like 'config flow'.  Fortunately there is
also code to read.

Anyhow, three months later:

- I've replaced the radiator timer code with
  [esphome](https://esphome.io/)---write a bit of yaml (even including c++
  lambdas!) and you get OTA, HA integration, etc for free
- In a vain attempt to save on heating, we got an electric blanket, so that has
  another controller
- There's a sensor in the shed, mostly to tell me it's cold and wet and all my
  tools are rusting
- The bedside lamp has an integration... mostly for the fun, but also so the
  alarm time can be coordinated with the radiator, and so I don't have to make a
  website to control its music server
- The camera we sometimes use as a baby monitor is integrated, because that way
  everything's in one place

and doubtless more gimmics will arrive.

Now, Home Assistant is running on my machine.  But this is silly; when guests
use that room I have to turn it off, and now the radiator doesn't come
on---which is exactly why I didn't want to use an overblown server to switch a
few relays in the first place.  Ergo it must migrate.  And I have a spare Pi.

First, I tried just installing the docker container; but it has random
connection problems and anyhow I hate administering docker by hand.  Why not
just install HomeAssistant?  Well---not only did they reinvent `getattr()`, they
also reinvented `pip`.  A *sensible* ecosystem would distribute plugins as pip
packages and let pip handle dependencies.  Home Assistant instead made its own
format, which includes a `manifest.json` file containing dependencies.  Then it
calls `pip` and installs them to a local `.cache`.  Now when we upgrade the system's
python, everything can break!  Even more fun, it calls `pip` with `--timeout
60`, which isn't long enough on a Pi for everything to work.

Never mind.  If we're going to devote a whole machine to the task of turning
relays on and off, we can use their Pi image and forget about it.

But how to get the old data into it?  There's a 'backup' facility, so, let's
make a backup and download it.  Unpack the `.tar` and we get a bunch of
`.tar.gz` and a `backup.json`.  Right.  Let's build a script to make these
archives:

```python
#!/usr/bin/python
from pathlib import Path
from subprocess import run

gz = []
for d in (x for x in Path(".").iterdir() if x.is_dir()):
    run(["tar", "-C", str(d), "-czvf", f"{d.name}.tar.gz", "."])
    gz.append(str(d.with_suffix(".tar.gz")))

run(["tar", "-cvf", "faked.tar", *gz, "backup.json"])
```

Yeah, my bash is really rusty.  But python is really fast; why use a
stringly-typed language when you can have proper objects?

Now we can just copy our old `.yaml` files, database and `.storage` over. We'll
lose the custom integrations, but that's alright for now.  Nope. Of course,
failed, claiming `backup.json` wasn't present (it is).  But it turns out there's
a `backup` feature in all HA installations, so you can spin up the old
installation, make a backup, upload it, restore, restart... and nope, that
didn't work too, although no error this time.

Ah well.  There's a terminal 'app' which also apparently enables ssh (only it
doesn't, as the port is blocked somewhere---oh, it's disabled but defaults to
22, unless you manually set it to 22, at which point it's *enabled* and 22.
Great UI that.).  But we can do *outgoing* ssh, scp
(no rsync) the files over, use `vim` (hurrah!  not just `vi`) to edit
`configuration.yaml` to remove the custom integrations, use qutebrowser to pass
through the `ESC` needed to use vim, reboot and we have the same inteface as
before.  Right.

Enable ssh port and we have incoming ssh---as root, but then we're in a
container.  Let's install `HACS`---the hack which pulls components off github:

```bash
$ wget -O - https://get.hacs.xyz | bash -
INFO: Trying to find the correct directory...
INFO: Found Home Assistant configuration directory at '/root/config'
INFO: Creating custom_components directory...
INFO: Changing to the custom_components directory...
INFO: Downloading HACS
Connecting to github.com (140.82.121.3:443)
Connecting to github.com (140.82.121.3:443)
Connecting to objects.githubusercontent.com (185.199.108.133:443)
saving to 'hacs.zip'
hacs.zip             100% |**************************************************************************************************************| 3885k  0:00:00 ETA
'hacs.zip' saved
INFO: Creating HACS directory...
INFO: Unpacking HACS...

INFO: Verifying versions
INFO: Current version is 2023.2.5, minimum version is 2022.11.0

INFO: Removing HACS zip file...
INFO: Installation complete.

INFO: Remember to restart Home Assistant before you configure it
```
hmm, did that just make a `custom_components` dir?  And if so, can I just drop
the integrations in there?  Yep.

Does it work?  Well, not immediately.  The Pi is rather slow, and we get
timeouts which I hadn't bothered to handle.  HA makes handling them ridiculously
complicated, but eventually I figured out the right place to raise the exception
and it seems to connect the second time round.

Then there's LetsEncrypt for ssl, and all the rest.  Quick?  No.  Easier than
building a bunch of scripts?  Barely.  Will just work if I don't tinker with it?
Yes---which is more than you can say for anything home-rolled...

[^1]: Even more fun: some of these aren't async functions at all, but 'async
    friendly callbacks', whatever they are.
