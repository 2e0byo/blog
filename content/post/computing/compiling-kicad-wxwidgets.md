---
title: 'Compiling KiCAD/WxWidgets'
date: Mon, 13 Aug 2018 20:52:36 +0000
draft: false
categories: ['Computing']
---

Since this has, alongside other things, occupied a whole day, I
thought I'd put it up here in case anyone else tries. Back in the day
KiCAD had a python scripting console.  Currently that would be very
useful: but it's implemented with gtk2, and everything ships with
wxwidgets compiled against gtk3.  So we have to compile wxwidgets,
which is fairly straightforward: get the
[sources](https://wiki.wxwidgets.org/Compiling_and_getting_started)
compile---except it's not a ./configure, make, make install job:
rather a python script calls other python scripts, and so on.  And of
course there was a problem: a function whose argument might not be a
char buffer throws a format-security error, and the whole thing won't
work.  Normally we'd just edit the GCC flags and set
`-Wno-format-security`, but how to do that here?  I spent ages ag-ing
around the sources trying to find out where the python code actually
called gcc, and was about to give up.  Then I thought of environment
variables.  In fish (which is not _quite_ bash-compatible) we do:
```fish
env CPPFLAGS='-Wno-format-security' python2 build-wxpython.py --build-dir=../bld
```
and it works! Turns out environment variables are inherited unless
strictly barred, or something like that. Anyhow, I didn't think it
would get through the subprocess.run or whatever, and it does. Then
the KiCAD sources are semi-easy: unless you actually know how CMake
works or are lucky (unlike me) don't worry about trying to get it to
select your just-compiled wxwidgets: I just temporarily replaced
`/usr/bin/wx-config` with a symlink to `/usr/local/bin/wx-config` and it
used the right library.  Compilation takes a lot of time---more than
an hour on this system---but after setting `LD_LIBRARY_PATH` here (I
have no login manager and use startx to load i3, so I tend to have to
set things: if you're on gdm you're possibly fine) it loads. Now
hopefully if anyone else tries it won't take them a whole day.
