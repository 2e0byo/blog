---
title: Too Many Directories
date: 2023-03-04T18:05:26Z
draft: false
categories: ["Coding"]
---
My PhD has too many directories in it.

I have---currently---three parts, and each of those has several chapters.  All
the chapters have been written independently, so I have a structure which more
or less looks like this:

```
titlepage.tex
thesis.tex
-- 1.part1
  |
  +- 1.chapter1
    |
    +-- standalone.tex
    +-- title.tex
    +-- chapter1.tex
  +- 2.chapter2
```
etc, only with three parts and sensible names.  Each of the chapters builds to
a separate pdf with `standalone.tex`, but now the Final Thing is upon me and I
needed to write `thesis.tex`.

First, I thought of using a `jinja2` template to generate it after scanning the
whole directory.  This was the right solution, but it was boring, so I abandoned
it.

Then I thought of just `\input`ting the files in `thesis.tex`.  And indeed I
started doing so, but after copy-pasting three or four times my sense of
neatness revolted.  "What would Knuth think?" I asked myself.  "Why did he give
you a turing-complete language?  It wasn't so you could do all the work with
emacs macros."

Thus I decided to do the work in Tex.  When I have to write Tex I prefer raw
Tex.  There's nothing *nice* about programming in a macro language, but it is
curious, in the sense that museums are full of curiosities.  The only thing
worse than museums is museums with guided tours, which is what LaTeX is.  On the
other hand, `\newcommand` gets nice syntax highlighting, so we should use it for
the API. So I wrote:
```tex
\newcommand{\includeChapter}[1]{%
    \inputTitle[#1]
    \chapter{\title}
    \inputChapter[#1]
}
```
So far, so clear.  `\inputTitle` has to exist because the title is a *chapter*
title in `thesis.tex`, but a *section* title in `standalone.tex`.  So it
consists of a single definition:

```tex
\ifdef{\title}{\let\title\relax}{}
\newcommand{\title}{Spiritual Tradition and Theological Tradition}
```

Alright.  I should probably just come clean and admit that I can remember some
things in LaTeX and others in Tex, and I just mix them freely.  Anyhow.  This
gives us a macro `\title`,  but how do we load it programmatically?

`\includeChapter` is called with a relative path, like
`0.frontmatter/0.acknowledgements` (yes, this is over-engineered).  So loading
the title is easy: we can just append:

```tex
\def\inputTitle[#1]{\input{#1/title}}
```

Now all we need is to load the content.  But---and I have home-rolled CI and all
kinds of other fragile things hanging on this convention---the name of each
chapter is meaningful.  Thus the chapter on the controversy over Nature and
Grace is called `nature-grace.tex` and lives at
`1.part1/1.nature-grace/nature-grace.tex`.  So we have to do some string
munging.  What we want is something like python's `str.split()`.  What we *get*
is another macro:

```tex
\def\splitstr #1.#2{#2}
\def\inputChapter[#1/#2]{\input{#1/#2/\expandafter\splitstr #2}}
```

This works because *there's actually nothing going on with `[]` in a TeX macro*.
Or rather, TeX macros are defined with `\def\name$ARGS$BODY`.  (And they look
as awful as that does.)  The `{}` of LaTeX are just group markers.  The `[]` are
just arbitrary (1-long groups of) characters between which the macro expander looks for
arguments.  And those arguments are separated by whatever you put in.
So this is perfectly valid:

```tex
\def\munge Hi#1!#2Ho{Generates: #2 (#1)}
\munge Hiread this!bet you can'tHo
```

(If you don't believe me, try it.)  Now you know why LaTeX errors are so
horrible and are never going to make sense.

Anyhow.  So `\def\splitstr #1.#2{#2}` is equivalent to
`lambda x: x.split(".", maxsplit=1)[1]` in python, and we can extract our title.
The same trick splits the
path on `/`, and now we can input the chapter.

At this point, mighty pleased with myself, I stuck `includeChapter{path}` calls
in the right place, fixed the inevitable typos with words like "acknowledgements"
(which I simply can't spell), and watched it compile.

Then a little later I wanted to see how close I was to the wordcount, so I ran
`texcount thesis.tex`.  Hang on: nothing.  Because of course, this unparseable
macro language is unparseable.  The only way to know what it will do is to run
it.[^1]  So `texcount` has implemented just enough TeX to follow `\input` calls,
but it hasn't (obviously) got any idea how to parse my macro.

Oh well, we can just count the chapters individually and sum the counts as we
input them, can't we.  So we get:

```tex
\newcounter{wordCount}

\newcommand{\includeChapter}[1]{%
  \inputTitle[#1]
  \chapter{\title}
  \inputChapter[#1]
  \addWordCount[#1]
}
```

Hang on.  If we do this, the counter will only be correct at the very end of the
file, when the final `includeChapter` is expanded.  But a wordcount on the back
page isn't much use.  So we need to call the macro *before* we output anything,
and defer actually including anything till later.  In other words, we need it to
define another macro (in a non macro language we'd have it *return* something,
but hey, global state is what a document is).  So we want a variadic macro:

```tex
\newcommand{\includeChapter}[2]{%
  \expandafter\def\csname input#2\endcsname{%
    \inputTitle[#1]
    \chapter{\title}
    \inputChapter[#1]
  }
  \addWordCount[#1]
}
```

Yes!  If you want key-value pairs in TeX, you use macros.  At any rate I think
it's clearer than some "hashmap" package which is just going to do this under
the hood.  `\csname` and `\endcsname` make macro names,[^3] and then we pass the
name in (I originally used a counter to generate `\chapterOne`, `chapterTwo`,
etc, but that just gets silly).  But how do we write `addWordCount`?

My first attempts is what everyone tries:

```tex
\def\addWordCount[#1]{\addtocounter{\input[#1/words.txt]}}
```

My second attempt was copy-pasted from the Tex.SE question everyone then lands on:

```tex
\usepackage{readarray}
\def\addWordCount[#1]{%
  \readdef{#1/words.txt}\theReadCount
  \addtocounter{wordCount}{\theReadCount}
}
```

Right.  Now how do we get `words.txt`?  We *could* use an external shell call.
But actually I was simultaneously developing a proper build system, so we might
as well use that.

To start with, every chapter had its own makefile, generated by cookiecutter.
But recursive make is bad, and anyhow we have top-level dependencies on lower
files, so it makes no sense.  Really we should have *one* makefile.  But
building it by hand is the same, *mutatis mutandis*, as before, except that RMS
is probably not as polite as Knuth.

One option would be build systems.  I consdered Meson for about ten seconds, and
cmake for fifteen.  (Autotools isn't a build system, it's a preventable
disaster.)  So we have a python script:

```python
#!/usr/bin/python

from pathlib import Path

header = """\
.PHONY: all standalones thesis thesis-clean
LATEXMK ?= latexmk --pdf --synctex=1
"""

footer = """
thesis-clean:
	${LATEXMK} -C

thesis: standalones titlepage.tex
	${LATEXMK} thesis.tex
"""

pdf_template = """{deps}
	cd {dir} && ${{LATEXMK}} standalone.tex
"""

skip = {"papers", "template"}
standalones = [
    x for x in Path(".").glob("**/standalone.tex") if x.parent.parent.name not in skip
]
outf = Path("Makefile")

pdf_entries = {
    str(s.with_suffix(".pdf")): pdf_template.format(
        deps=" ".join(
            str(x)
            for x in (
                s,
                s.with_stem(s.parent.name.split(".")[1]),
                s.with_name("title.tex"),
            )
        ),
        dir=s.parent,
    )
    for s in standalones
}

parts = [
    header,
    "all: standalones thesis",
    "\n",
    "standalones:" + " ".join(pdf_entries.keys()),
    "\n",
    "\n".join([":".join([k, v]) for k, v in pdf_entries.items()]),
    footer,
]

outf.write_text("\n".join(parts))
```

There.  We get a makefile, and however naughty it is to use a *modern*
scripting language to generate a Makefile, and however horribly readable python
is, it's a makefile in the end.  And best of all it took less time to write than
it would take me to remember exactly how the whole thing with $ and { and } and
@ works for arrays in bash.

Now all we need to do is to add `s.with_name("words.txt")` to the dependencies
for `pdf_entries` and add a rule to generate `words.txt` by calling `texcount`.
I actually have a bona fide shell script for this, although my eyes hurt slightly
when I look at it:

```sh
#!/usr/bin/env sh
cd $1 && texcount -brief -merge -sum=1,0,1,0,1,1,1 2>/dev/null "$2" | cut -d ':' -f1 | awk '{print $1}' > words.txt
```

I always forget about `cut`.  These days I'd probably use `sed` for the whole
thing.  (Those days I mostly used google.)  Anyhow, it gets us the word count,
which is what we want, and then we concatenate it.  Slightly to my surprise
LaTeX has no built-in ability to print numbers with separators, but
`\usepackage{comma}` puts paid to that.

Now how many words do I have?  94,477.  Drat.  The limit 100,00 and I have two
chapters still to go.  I'd better get cutting.



[^1]: Techically this is true[^2] of any turing complete language, but you can get
    actually do a pretty good job of parsing most *sane* languages without
    executing them, assuming the programmer hasn't done anything stupid.
    `texcount` is a Perl script, so yes, it's just one big regex and we're
    parsing with a regex.

[^2]: I think.  I'm only a poor PhD student in theology.

[^3]: That will do for here.
