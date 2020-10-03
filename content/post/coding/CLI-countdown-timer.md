---
title: "CLI Countdown Timer"
subtitle: Stop procrastinating and do some work
date: 2020-09-29T13:05:10+01:00
draft: false
categories: ['Coding']
---
I wrote this a while ago, and it’s been in use ever since: a very
simple script which counts down (or up) while printing the remaining
time.  Controlled with standard job control, it’s one up on `sleep` as
you can _see how long is left_.  This is occasionally handy; if I only
have ten seconds on the clock before lunch I’ll not start something
new, but if I’ve got fifteen it might make sense.

When elapsed, it exits.  So chain it:
```bash
countdown.py 10m && tput bel && notify-send "Elapsed!"
```

Better still, just drop that in an alias.

Code is on [gitlab](https://gitlab.com/2e0byo/cli-countdown-timer) but
you could probably write it in the time it took you to read this.  So
I wonder why no such basic utility seems to exist in the package managers?
