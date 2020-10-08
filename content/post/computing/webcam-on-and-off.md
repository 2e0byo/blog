---
title: "Webcam on and Off"
date: 2020-10-08T17:17:55+01:00
draft: false
categories: ["Computing"]
---

Currently we are all stuck in front of webcams, at least half the
time.  I do have a laptop---a gift from a kind friend---and it does
get used, but the rest of the time I am sitting before two old
monitors (one of which recently had to be repaired) and a lovely
cherry keyboard: and no webcam.  No matter: I’ve a cheapo usb-thing
and it works fine.  I’ve also an old phone handset from an 80s
landline wired into two 3.5mm jacks---it had an electret microphone
and works fine.  It gets laughs on zoom, but it’s easier to pick up
and put down than a headset, and I can hear if anyone’s creeping up
behind me.

Problem: the el-cheapo usb camera is permanently on when plugged in.
And crawling down behind the computer to plug it in isn’t really an
option.  Worse, it has no status indicating light.  Now I’m not _that_
paranoid---if the NSA wants to see me in jumpy 640x480 frames, they
can probably get at my webcam.  I doubt they care much.  But still,
not knowing whether one’s webcam is on is a little unsettling...

It’s a usb device, so the first thing to look at is `/sys`.  A quick
google suggested that first we need the bus and port ID, and then we
can bind and unbind a driver by writing to
`/sys/bus/usb/drivers/unbind`.   Thus:

```python
def get_webcam():
    """Get webcam usb."""
    cameras = []
    for product in Path("/sys/bus/usb/devices").glob("*/product"):
        if "camera" in product.read_text().lower():
            cameras.append(str(product).split("/")[-2])
    return cameras
```

Liable to have fals positives if a digital camera is plugged in, but
better safe than sorry (don’t go running `--disable` unless you’re
*sure* only one webcam is attached...)

and then something like:

```python
def disable_webcam(webcam: str):
    with Path("/sys/bus/usb/drivers/usb/unbind").open("w") as f:
        f.write(webcam)
```

To query the status, we can look to see if 1. any webcams are found
and 2. they have a bound driver.  I run [i3](https://i3wm.org/) and
use [i3status](https://i3wm.org/i3status/) with a python wrapper
script as per the docs to display the status of `redshift` and the
amount of time I have spent typing at the computer that day, from my
anti-rsi package.  Thus it was easy enough to add another function:

```python
def webcam_status():
    webcam = get_webcam()
    if webcam:
        status = get_webcam_status(webcam)
        if status:
            return "R", red
        else:
            return "", green
    else:
        return "O", orange
```

where the colours are html codes defined elsewhere.  This is then
injected into the json:

```python
j.insert(0, {"full_text": webcam, "name": "webcam", "color": colour})
```

and if the webcam is recording, a red ‘R’ appears in the status line.

I’m sure there are ways to trick this, but the kind of access you’d
need to the system to be able to rename a usb device or access it
without the kernel knowing a driver had been bound (or indeed, just
replace my `wrapper.py`) is probably more than I care to defend
against anyhow.

The script is up on [GitLab](https://gitlab.com/2e0byo/webcam_status)
if anyone else has need of it.
