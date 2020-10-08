---
title: "Anti Rsi"
date: 2020-10-08T18:12:00+01:00
draft: false
categories: ["Coding"]
bigimg: [{src: "/img/computer_usage.jpg"}]
---
There are lots of anti-rsi packages out there for windows.  I even
found a few for Linux.  None did what I wanted them to do: to enforce
short and long breaks at configurable intervals, allowing me to push
them back when I was in the middle of something, but getting
increasingly insistent that I actually took them.

Enter [anti-rsi](https://gitlab.com/2e0byo/anti-rsi), a python script
which does everything an anti-rsi package needs to do and nothing
more.  It can be paused, resumed, postponed, and forced to run early.
It uses some idleprinter (`xprintidle`) to keep track of when the
computer isn’t in use and pause itself.  It logs the total time it
considers that the system has been in use.  Communication is by unix
signals, which is a bit naughty, but I found enough.  It will output
usage when `sigpoll`ed to `/dev/shm/usage`, which I then pickup with a
wrapper script for `i3status`.  It also logs, and I run a few services
to conglomerate all these logs onto the main workstation and generate
a nice pretty graph of them with the wonderful
[mlpd3](http://mpld3.github.io/) which 'brings matplotlib to the browser'.

{{<figure src="/img/computer_usage.jpg">}}

There are many possible improvements, but I wrote this a few years ago
and it’s been in use ever since.
