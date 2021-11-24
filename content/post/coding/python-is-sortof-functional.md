---
title: "Python Is (sort-of) Functional"
date: 2021-11-24T12:56:45Z
draft: false
categories: ["Coding"]
---
I recently had to parse a csv file which looks like this:

```csv
"key","val"
"key","val"
"key","val"

"col1","col2","col3","col4"
... row data here
```

The obvious, imperative solution would be:

```python
from csv import DictReader

def parse(f):
    props = {}
    
    for line in  f:
        if not line.strip():
            break
        k, v = line.strip().replace('"', "").split(",")
        props[k] = v

    reader = DictReader(f)
    data = list(reader)

    return props, data
```

With the walrus operator we can save a few lines at the cost of non-obvious
syntax:

```python
def parse(f):
    props = {}
    while line := next(f).strip():
        ...
```

I suppose there might be people who think that is neat.

What _I_ did was instead:

```python
from itertools import takewhile

def parse(f):
    props = {
        k: v
        for l in takewhile(str.strip, csvf)
        for k, v in [l.strip().replace('"').split()]
    }
    ...
```

`itertools.takewhile`, predictably enough, takes values from an iterable while
they satisfy some condition.

Strangely, this dictcomp is neater to my eyes.  It's obvious what it does, where
the values come from: in fact, I can read it a good deal easier than the
previous version.  After a moment I realised this would be even easier:

```python
def parse(f):
    reader = csv.reader(f)
    props = {k:v for k, v in takewhile(bool, reader)}
    reader = csv.DictReader(f)
    data = list(reader)
    return props, data
```

That, I think, is pleasingly declarative, functional _and_ neat.  Had I not been
waiting for something else to finish I would likely have written the first
option and gone with it.  Sometimes, perhaps, it pays to think about obvious
tasks like reading csv files.



