---
title: "Cleaning Scanned Pdfs"
date: 2020-10-24T18:01:04+01:00
draft: false
categories: ["Coding"]
---

> This post is largely a log so I remember how to do it next time, but
> if anyone else has a bunch of scans to convert, read on...

## Background


Frequently in academia---and probably in much of the modern
world---one has to handle things which began life as books, hit the
glass of a scanner, and became pdfs.  Scanning is hard, and unless one
has a lot of patience, the resulting pdfs are generally pretty all
over the place: sometimes pages are upside down, frequently the book
(which was not made to lie flat) does not want to flatten on the
glass, and often the scanner has simply picked a nearby standard page
size.

{{<figure	src="https://linearbookscanner.org/designs/p1/proto1.png"	caption="Unfortunately nobody seems to have one of these." >}}
	
(That's a [linear book scanner](https://linearbookscanner.org/) by the
way.  Some day...)

Fortunately converting scans to decent images isn’t that hard with
[scantailor](https://github.com/4lex4/scantailor-advanced).  Most of
the processing can be done automagically, but one can keep an eye on
it and correct the inevetable odd slip.  (Again and again I’ve tried
to write fully automated scan converters, but it just doesn’t work.)

What was missing---up to now---was some way of automating the process
of taking a pdf, splitting it up into individual images, dumping those
images in a sensible directory, running scantailor on that directory,
and then, when it was all done, converting back to pdf, running ocr on
the pdfs and then zipping them all back together into a single,
processed pdf (and ideally putting it somewhere sensible).  All of
this can be _done_, quite easily, with a mix of `find`, `parallel`,
`imagemagick` and `tesseract` but I don’t do it often enough to
remember the comands.

## Automating it

A few days ago I encountered [cookiecutter](https://github.com/cookiecutter/cookiecutter) which makes
pre-populating directories very easy: even easier than just putting a
bunch of `mkdirs` in a script: so easy I actually _use_ it.  I also
had occasion to convert a bunch of scanned pdfs into processed files.
Ideally one should be able to drop all the pdfs in a dir and run some
script on it which will set everything up for scantailor: come back
with a cup of tea and work through the scantailor projects, and then
run some other script and leave the computer OCRing overnight, to wake
up to a neat bunch of pdfs in some easy-to-find directory.  So I
decided to _write_ the scripts and put them up somewhere.

First off was a [cookiecutter
template](https://gitlab.com/2e0byo/cookiecutter-process-scan) to make
the right dirs, which spits out something looking like this:

```
project_name
	/ src / tmp
	/ final
	/ templates / minimal_template.ScanTailor
	/ prepare.py
	/ finish.py
```

The key to this is the minimal ScanTailor template.  It seems
ScanTailor will accept a _very_ minimal template indeed:

```xml
<project layoutDirection="LTR" outputDirectory="{{ outdir }}" version="3">
  <directories>
    <directory id="1" path="{{ outdir|replace('/final', '/source/tmp') }}"/>
  </directories>
  <files>
    {% for inf in input_filenames %}
    <file name="{{inf.name}}" id="{{inf.id}}" dirId="1"/>
    {% endfor %}
  </files>
  <images>
    {% for inf in input_filenames %}
    <image fileId="{{inf.id}}" subPages="2" id="{{inf.id + 1}}" fileImage="0">
      <dpi horizontal="600" vertical="600"/>
    </image>
    {% endfor %}
  </images>
</project>
```

That’s a jinja2 template, but you can easily see the xml in it.  It
generates a valid, but bad looking project whose thumbnails are all
off, but once we run ‘split pages’ it all gets sorted out. 

We generate this in `prepare.py`, once we’ve split the original pdf
(using `pdftk burst`) and then generated an image for each
page---ideally just taking the output with `pdfimages`, but if that
doesn’t work (some ‘clever’ scanning packages actually output multiple
layers) then we just pass it through `convert` i.e. ImageMagick, with
`-density=300`.

Parallelism is done with `gnu parallel`: indeed, the python scripts
mainly just call `run(cmd, shell=True)` so you definitely should _not_
run this willy-nilly. But it’s no worse than the shell script you
otherwise would use (and I used before).

These scripts are customised by cookiecutter when they are made, which
is neat.  So we can just put:

```python
cmd = "pdftk *-ocr.pdf output {{cookiecutter.directory_name}}.pdf"
```
and the resulting script will contain the right filename.  Of course,
we could have worked it out from within the script, but this is
neater.

A few other things to note with this kind of work:

* tesseract will try to parallel, so you have to call it as `env
  OMP_THREAD_LIMIT=1 tesseract <args>`.  Generally speaking it’s
  better to single-thread and run multiple instances in parallel when
  doing this kind of work.
* If it runs out of ram, editing the script and putting `-j $(echo
  $(nproc)-2 | bc)` (without the `$`s if you, like me, run fish), will
  generally calm things down. Or make more swap space temporarily
  i.e. a swapfile.
* We use a local tmpdir for parallel, as `/tmp` here is a ramdisk.

Now, how do you batch process everything?  In the root of the
repository is a script
```bash
auto_process_pdfs.py [-h] [--outdir OUTDIR] [--finish] [--process] INDIR
```
which expects to be
run from a dir containing pdfs to process.  It will call
`cookiecutter` for each pdf, using the slugified (i.e. `like-this`)
form of the filename to name the repository (you need
python-slugify).  Then it will drop the relevant pdf into `/source` of
the target dir and run `prepare.py`.

After that you can run the script again, but with `--process` and it
will call scantailor for every file.

When everything is done, you can call the script _again_, this time
with `--finish`, and walk away.  If everything goes well you should
find a bunch of symlinks in the output directory, ready to call `cd
OUTDIR; zip -r ../archive .`.  By default zip dereferences symbolic
links, so you get a bunch of pdfs in a zip file, which poor users of
the Windoze (almost)Operating System can probably handle.

## Statistics

I’ve not timed the pre- and post-processing as they relate to the
particular computer in use and not much else.  But how long does it
take to process scans in scantailor this way?

With 8 pdfs totalling 120 pages (some doubles), of which three needed serious
dewarping, it took me 36 minutes to produce 183 pages of output.  That
works out at 36*60/183 = 11.8 seconds a page.  Not bad, eh?  

Add to that however long it takes you to get all the pdfs in one
directory (which would need doing anyhow), and thirty seconds---I'm
being generous---to run the script and walk away.  Then think how long
it would take to make all the dirs and populate them by hand...

Most of that is down to scantailor-advanced, whose automatic defaults
are _extremely_ good.
