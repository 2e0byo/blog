---
title: 'End-of-Charge'
date: 
draft: true
categories: ['Electronics']
tags: ['Battery charger']
---

Initially I thought this was easy: just look for negative dV/dt.  It
turns out _that_ isn't as easy as it might seem, because of the
resolution of the ADC: we don't want to terminate on last digit
error.  It also turns out that dV/dt [might not be as
good](http://www.st.com/resource/en/application_note/cd00003825.pdf)
as I remembered it being; also it seems there are people whose hobby
is rechargeable batteries (!) who [advise against
it](http://www.candlepowerforums.com/vb/showthread.php?188349-AA-fast-chargers-Delta-V). 
The ST application note recommends differentiating and looking for the
inflection point, but that's going to be even more fun with an MPU.

### Simulation

I now have some charge
[data](https://ofalltrades126687660.wordpress.com/2018/07/20/proof-of-concept/). 
The clever thing to do would be to play with plotting it, smoothing
it, etc with a python script before I try anything on the PIC.  If I
were a science student I'd know how to do this already.  As I'm a
theologian, I've never delved into plotting graphs in Python, but how
hard can it get? The first thing is to plot the data, which turns out
to be incredibly easy: \[sourcecode language="python"\] import
matplotlib.pyplot as plt plt.plot(x, data, 'go', markersize=0.25) #
3rd argument is point colour and style plt.ylabel("Battery
Voltage/(2.5/1023)V") plt.xlabel("Time/S") plt.show() \[/sourcecode\]
Which produces a nice set of points.  It'd be nice to have a basic
smooth line; for now we just use '[somebody else's
code](https://scipy-cookbook.readthedocs.io/items/SignalSmooth.html)'
and a Hanning window (which is not really the 'right' solution).  
There's now a dedicated
[GitLab](https://gitlab.com/2e0byo/battery_charger) repository
attached to this project; files will be added over the next few days.
