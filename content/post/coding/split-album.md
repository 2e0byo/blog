---
title: "Split Album"
subtitle: Split album into multiple tracks intelligently
date: 2020-09-29T13:33:11+01:00
draft: true
categories: ["Coding"]
---
There are plenty of cases where you end up with one great big audio
file for an album and an _approximate_ idea where all the tracks are.
Perhaps you’re digitising a tape or LP; perhaps you’re trying a new
album from youtube before shelling out for the CD.

In the latter case in particular you have a lossy file you don’t want
to re-encode, and generally a bunch of shortcuts which _nearly_ tell
you where every track boundary is.  They tend to get worse as you go
through the album, no doubt because the compiler got more and more
bored.

Thus we need to be able to do two things: find out where each track
_really_ starts and ends, and split the original audio file up without
transcoding.  The end product should be a bunch of tracks with
metadata ‘good enough’ for further processing: at the very least, we
should tag and name each track according to the list we got at the
beginning.

In the past I’ve tried just splitting on silence, with
[Sox](http://sox.sourceforge.net/) or using Audacity’s ‘sound finder’
plugin to add labels, exporting the label set, editing in a text
editor, re-importing, and then exporting the lot.  That’s as much of a
hassle as it sounds like; and Sox doesn’t really work for this---you
have to play with the paramaters a lot, and sooner or later you end up
with false splits (getting the right number of splits is no gaurantee
they’re in the right place).  But sox is great, and there’s no reason
we can’t do something like its splitting plugin _in the approximate
region of each split_.

Enter [split-album](https://gitlab.com/2e0byo/split-album).  This tool
will take an audio file, take a tracklist (either in a provided .csv
or from the description if originally a youtube video), use ffmpeg to
generate little snippets `bounds` seconds either side of the label
location, use [pydub](http://pydub.com/) on each of those segments to
find the beginning and end of each track, and then use ffmpeg again to
split the original file up before applying metadata with taglib---all
without transcoding.  It runs pretty quickly, even though pydub is not
the fastest (which is why we split the audio into temporary chunks
first, to avoid manipulating huge objects in ram): albums take about
20s or the like.  Use `youtube-dl --add-metadata -x <URL>` to get an
album off youtube, run `split-album.py` on the resulting video, then
run `beet import` or whatever you use to manage music on the tracks.

Oh, and don’t go stealing music.  But if you care enough about music
to be trying albums before buying them, you almost certainly won’t put
up with youtube quality for very long.  I have more infrastructure to
help me manage music and work out what to buy, but that will be
another post.
