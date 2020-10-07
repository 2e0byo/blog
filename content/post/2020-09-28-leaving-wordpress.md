---
title: Leaving Wordpress
subtitle: "“...and all we raise aloft must soon decline”"
tags: []
draft: false
date: 2020-09-28
---
Wordpress is a glorious conglomeration of PHP which works very well,
PHP which works poorly and PHP which doesn’t work at all.  The former
is generally written by the Wordpress developers, the next by me, and
the latter by me after around 11pm.

This website existed for a while on wordpress.com.  It was the natural
choice: everyone uses wordpress to manage blogs, and this is little
more than a blog.  On the other hand, writing in a web browser is
irritating (writing is what text editors are for) and does one really
need the whole wordpress architecture to serve a lot of static pages
and images?  Wordpress.com won’t even let you install plugins on the
free tier, so it’s not like I was doing anything with all that dynamic
ability anyhow.

Enter [gitlab pages](https://docs.gitlab.com/ee/user/project/pages/)
and [Hugo](https://gohugo.io/).  Gitlab, not Github, simply because
all my repositories are already there (back in the day gitlab offered
unlimited private repositories, which was very attractive).  Hugo
because 1. it’s shockingly fast and 2. it’s written in Go, and I know
nothing about Go; how better to find out?

Thus, this site is now written very largely in markdown, in Emacs or
Vim as the fancy takes me, pushed to a git repository, and appears
magically here online.  And it now uses no cookies, no bloat, and no
server-side code at all.  Which might encourage me actually to write
for it, since writing is as easy as running `hugo new
post/date-title.md`, opening said file in an editor, committing and
pushing.
