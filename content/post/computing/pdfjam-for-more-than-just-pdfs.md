---
title: 'PdfJam: for more than just pdfs'
date: Sun, 25 Nov 2018 15:48:37 +0000
draft: false
categories: ['Computing']
---

Can we take a moment to remark on how wonderfully useful
[PdfJam](http://freshmeat.sourceforge.net/projects/pdfjam/) is? Behind
the scenes it's just LaTeX.  Thus you might be surprised to notice
that 

```bash
pdfnup --nup 1x1 --paper a5paper --no-landscape image.png 
```

 Is an excellent way to turn an image—say, a bunch of screenshots of a
page which you concatenated with
```bash
convert image1.png image2.png image3.png -append image.png
```

Into (say) an a5 pdf, ready to be turned into a full-length pdf with

```bash
pdftk *.pdf cat output out.pdf
```

And then laid up into a booklet with

```bash
pdfbook2 out.pdf
```

I've used pdfbook2 over pdfbook as it adds margins—which normally I
don't want, but here it is useful as the nup-d pages probably don't
have very large margins. Of course there are various ways of
customising it. An even _better_ way of converting pngs of a text
document (say, a scan—though beware copyright: you're probably alright
for personal use but IANAL) into pdfs is
```bash
 tesseract image.png image-ocr -l fra+lat+grc pdf 
```

With languages set accordingly, initially in order of provenance. This
produces a pdf with 'invisble' ocr-d text you can select and
copy-paste, and it's _really good_. But Tesseract and Scantailor (an
excellent program for extracting, sharpening, monotoning and generally
adjusting scans) are for another post and another day.
