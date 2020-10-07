---
title: "Volatile Tmp"
date: 2020-10-07T11:00:07+01:00
draft: false
categories: ["Coding"]
---
What does one do with temporary files?  For things one really doesn’t
need, there’s `/tmp`, which is wiped on boot---though sometimes it’s a
ramdisk, and one should be wary of dropping large files into
ramdisks.  But what about e.g. downloaded isos, pdfs prepared for
printing, and the like?  Things one needs _now_, might need
_tomorrow_, but definitely won’t need in a year’s time?

Like most people I used to use `~/Downloads` and go through it (with
`ncdu`) every time it got too large.  But this isn’t really
satisfying: one can accumulate thousands of files each only a megabyte
in size.  I considered using `cron` to wipe downloads ever so often,
but sometimes one wants to keep things.

The solution is a dedicated directory, `~/volatile-tmp` though you can
call it what you like, and a script which scans it every day and
deletes everything older than some epoch.  Whilst one could do this
directly with find, I threw together a python script which just globs
the tmpdir.  Thus subdirs can be handled the way (after a lot of
thinking) I think they should be: any tree below `~/volatile-tmp` has
the age of the _youngest member_ at any depth (and we only recurse by
one level, to avoid deleting bits of projects).  If need be the life
of a particular dir can be extended by dropping a file named
`.volatile-tmp` in it, or it can be preserved by touching `.preserve`.

When I was at school I put all the paperwork they give
you---worksheets, letters, etc---in a big box marked `volatile`, and
every month threw away the bottom half.  Thus the probability that I
could find a particular piece of work diminished logarithmically as
time went on.  If you use a backup system like
[backintime](https://github.com/bit-team/backintime) then files have a
similar half-life: as older backups are purged (and I don’t exclude
`~/volatile-tmp` from backup) the chance of finding a file dwindles to
nothing.  So if it goes today and you need it tomorrow it should be
findable, but in two years...  which fits the original picture quite
nicely.

I call the script from a `systemd` unit, but cron would work just as
well.  Code (and an installation script) is on
[gitlab](https://gitlab.com/2e0byo/volatile-tmp) and it’s been running
for a year or so now: my `~/volatile-tmp` is at time of writing only
46M in size---and I use it a lot.
