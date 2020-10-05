#!/usr/bin/python3
"""
Convert caption strings from wordpress into hugo shortcode figure.

Designed to be called from emacs on region.
"""

import shutil
from pathlib import Path
from re import findall
from subprocess import CalledProcessError, run
from sys import stdin

import requests
from jinja2 import Template

template_figure = Template(
    '{{<figure src="/img/%% src %%" caption="%% caption %%">}}',
    variable_start_string="%%",
    variable_end_string="%%",
)

img_path = Path("~/code/2e0byo/static/img/").expanduser()


def download_image(url: str):
    """
    Download url and keep if need be.

    Parameters
    ----------
    url:str : url to download.  Everything else generated.


    Returns
    -------
    pathlib.Path() object pointing at downloaded image name
    """

    base_fn = Path(url.split("/")[-1])
    fn = base_fn
    target = img_path / fn

    i = 0
    while target.exists():
        fn = fn.with_name(f"{base_fn.stem}_dup{i}{base_fn.suffix}")
        target = img_path / fn
        i += 1

    r = requests.get(url, stream=True)
    with target.open("wb") as f:
        shutil.copyfileobj(r.raw, f)
    del r

    if base_fn != fn:
        p = run(["diff", target, img_path / base_fn])
        try:
            p.check_returncode()
            target.unlink()
            fn = base_fn
        except CalledProcessError:
            pass

    return fn


src = "".join([i.strip() for i in stdin.readlines()])

rgx = r"\\\[caption.*?\\\]!\[(.*)\]\((.*)\)(.*?)\\\[/caption\\\]"
results = findall(rgx, src)
if results:
    not_found, url, caption = results[0]
    fn = download_image(url)
    print(template_figure.render(src=fn, caption=caption))
else:
    rgx = r"!\[(.*)\]\((.*)\)"
    results = findall(rgx, src)
    if results:
        not_found, url = results[0]
        fn = download_image(url)
        print(template_figure.render(src=fn, caption=""))
