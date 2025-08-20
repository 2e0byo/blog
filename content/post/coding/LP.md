---
title: "Measuring a turntable speed with FFMPEG (mostly)"
date: 2025-08-20T12:16:54+02:00
draft: false
categories: ["Coding"]
---

Here on holiday I have no internet most of the time. We also have a record
player, and it's annoying me: it's clearly flat by roughly a quarter tone, and
slow. The question is, *how* slow?

Apparently there are apps which can measure the rotation speed directly with the
phone's accelerometer, but none seemed to work for me, so I set the record
player up with nothing on the plateau except a scrap of paper as an indicator
and recorded an hour of footage at '33RPM'. In theory now all we need to do is
work out how many times the dot hits a given section of the image per minute and
we have measured the rotational speed. Unfortunately I have another problem: I'm
not a data scientist, I'm more of a systems programmer. This is the kind of
thing I'd normally do with a bit of googling, but that's out of the question.
Naturally, a real data scientist would do this with OpenCV or something in a
notebook, but let's see what we can do with just what I can figure out offline.

The video is of a scrap of white paper on a black turntable. How hard can it be
to turn that into a signal and count the peaks? First lets crop to the region of
interest:

```shell
ffmpeg -i raw.mp4 -an -vf crop=50:50:320:700 cropped.avi
```

The coordinates were chosen by trial and error. Then since I came across it in
the ffmpeg manpage I filtered to black and white:

```shell
ffmpeg -i cropped.avi -vf colorchannelmixer=.3:.4:.3:0:.3:.4:.3:0:.3:.4:.3 bw.avi
```

And then burst it into one bitmap per frame:

```shell
ffmpeg -i bw.avi bw-bmp/frame-%07d.bmp
```

Here's a sample with the scrap of paper in view:

{{<figure src="/img/LP/white.bmp">}}

And here's one without:

{{<figure src="/img/LP/black.bmp">}}

That gives us 750MB for 9.6k images. I chose bitmap because (if I understand
correctly) the underlying data is stored as integers with no encoding or
compression. A glance at one of the files in emacs showed something of a header
at the beginning and I wouldn't be surprised if there's a sequence to indicate
end-of-buffer. Normally one could find out very quickly online, but there's no
internet. Still even at 50x50px the vast majority of the data is data, so let's
just try taking the bytewise mean:

```python
from pathlib import Path
from tqdm import tqdm

def mean(p: Path) -> float:
    bytes = p.read_bytes()
    return sum(bytes) / len(bytes)

signal = [mean(p) for p in tqdm(list(Path("LP/bw-bmp").glob("*.bmp")))]
```

(`list` here gives `tqdm` a known length).

The video was shot at 30fps, so each frame is 1/30 S, and it's trivial to stick
that in a polars dataframe, dump it to csv, and plot it in libreoffice calc for
want of any other way to plot anything:

{{<figure src="/img/LP/signal.svg">}}

Of course, a real data scientist would know how to get a nice interactive plot,
but I don't.

Once can clearly see the black turntable here as the noise floor, with periodic
spikes well above the noise. Excellent. Unfortunately I also know very little
about signal processing, so let's just do a crude peak-finding algorithm:

```python
batches = []
timestamps = []

for row in tqdm(df.iter_rows(named=True), total=len(df)):
     if row["mean"] > 50:
         batch.append(row)
     elif batch:
         timestamps.append(max(batch, key=lambda b: b["mean"])["timestamp"])
         batch = []
```

Data is in `df` with the bytewise mean in the `mean` column.

The period is just the rolling difference between points. I've forgotten how to
do window functions in polars so we can just do it manually:

```python
diffs = [timestamps[i + 1] - timestamps[i] for i in range(len(timestamps) - 1)]
```

`60 / period` is the period in RPM and the data is not good:

```python
>>> (60 / pl.Series(diffs)).describe()
Out[101]:
shape: (9, 2)
┌────────────┬───────────┐
│ statistic  ┆ value     │
│ ---        ┆ ---       │
│ str        ┆ f64       │
╞════════════╪═══════════╡
│ count      ┆ 1715.0    │
│ null_count ┆ 0.0       │
│ mean       ┆ 32.176599 │
│ std        ┆ 0.34014   │
│ min        ┆ 31.034483 │
│ 25%        ┆ 32.142857 │
│ 50%        ┆ 32.142857 │
│ 75%        ┆ 32.142857 │
│ max        ┆ 33.333333 │
└────────────┴───────────┘
```

Well at least one sample has the correct rate, but the turntable is actually
turning at 32 RPM. Here's another ugly plot of computed RPM with a simple window
average, via the world's most popular functional programming environment, i.e. a
spreadsheet:

{{<figure src="/img/LP/speed.svg">}}

It's interesting to see the quantisation error which here comes from the video's
sample rate, rather than the usual ADC limitations.

There are a number of potential improvements here: the signal is periodic with
minimal cycle-on-cycle variation, so we can overlay multiple peaks to get a
better effective sample depth (like a DSO does). We could probably track the dot
directly and build up a rotational model without needing to convert to a
periodic signal. And doubtless you can do this all directly in opencv or the
like.

Since things have changed a lot in this field in the last few years I fed
this blog post to Mr. GPT with the following prompt (which I made up: I won't
stoop to 'prompt engineering'):

> Read this blog post (below) and comment on other ways of achieving the same
> goal. Pay attention to the last paragraph, but feel free to adopt any other
> means of measuring rotational speed. Assume I can program competently in
> whatever language you choose, but have little formal background in computer
> vision or signals processing.

The model suggested some quite interesting things, the key to which was moving
to the frequency domain.[^0] The supplied FFT estimation code came up with

```python
Estimated rotational speed: 32.1959 RPM (resolution floor ~±0.019 RPM)
```

Which agrees pretty closely with the naive average above.

You can read the whole chat
[here](https://chatgpt.com/share/68a32595-c4f0-8004-8b24-c7473c13e0e8). LLMs are
a pain when they fill codebases with poorly sliced boundaries and copypasta
APIs, but this one has convinced me I really need to get a decent signal
processing textbook.

Oh and no, there's nothing I can do to fix the speed of this turntable without
taking it apart, so we're just going to have to listen to slightly flat
music. Bonus marks if someone can tell me *how* flat it ought to be: can we just
scale proportionally and say 3% under?

[^0]: There are also CV solutions, of course, but I really don't want to mess
    with denoising and thresholding images for something as simple as this: my
    experience is that there's always a few errant pixels which break
    everything---probably because I'm not good enough at denoising.) 
