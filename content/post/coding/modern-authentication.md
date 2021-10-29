---
title: "“Modern Authentication”: Outlook365 in Emacs"
date: 2021-10-29T16:37:35+01:00
draft: false
categories: ["Coding"]
---
A few weeks ago I received an email from the university stating:

> Further to our previous communication advising about a change to basic
> authentication for Durham mailboxes, on 28th October 2021 we will be removing
> the ability to connect to University email via IMAP and our records indicate
> that you currently access email in this way.

This, apparently, is down to the fact that

> Basic authentication is no longer secure enough to support modern working as
> it does not support security features such as Multi-Factor Authentication
> (MFA). Using modern authentication will mean we can protect our mailboxes from
> unauthorised access, however, this does mean that email clients configured to
> use legacy authentication will stop working.

There is a contradiction here, of course: the allegedly more secure 'modern
authentication' has nothing whatsoever to do with IMAP.  I went to sleep very
cross at the idea that I might have to give up on IMAP, a protocol which works
extremely well at fetching mail from a server, and replace it with something
horrible like a [davmail](https://start.duckduckgo.com/) bridge.  And all this
because, apparently, my inbox is in enormous danger of being hacked.  Given that
email is sent in plaintext and is famously easy to MITM (hence all those spam
emails coming from reputable servers) this is an interesting claim at the least.
Last week a professor forwarded me an email from a student in one of my seminars
which went:

> Dear Prof. X,
>
> ... my username is <> and my password is <> ....
>
> Yours,
>
> Y

Not even oauth2 with multifactor authentication and tokens expiring every
sixteen seconds making you type in codes which ping on the phone you
inconveniently left at home can fix that security breach. But apparently that,
and not teaching people that email is inherently public, and anything sent by
email should be considered published, is the real security breach. Oh well.

## Modern Authentication

When I had a closer look, it turned out Durham were not 'retiring IMAP' at all.
They were retiring password authentication, which is completely different.  In
order to find this you have to log in (with MFA!) to a special website, which
hosts... a word document which one can't download for some reason, explaining
that you can use thunderbird.  So I duly installed and fired up thunderbird, and
it does indeed redirect me to a login page, take a code from the authenticator
app, and then off we go.  Thunderbird can do this, because it is registered as
an app with microsoft, so they have a client id and 'secret' in plaintext [in
their source
code](https://hg.mozilla.org/comm-central/file/tip/mailnews/base/src/OAuth2Providers.jsm#l129).
Thus anyone can pretend to be thunderbird, and get a refresh token.  Someone has
already done the hard work of writing [a script to do the original
login](https://github.com/UvA-FNWI/M365-IMAP) and extract the refresh token from
a redirect.  After that 'modern authentication' is just (X)OAUTH2.  The basic
idea is:

* you get a refresh token by logging in to some auth page.  The token is
  urlencoded into the page we redirect to.  In this case, we just redirect to
  localhost and extract from the url (the browser shows an error, but the url is
  what we want).
  
* the refresh token lets you get an access token by making a post request to the
  right authentication endpoint with the refresh token, and the client secret
  and id, which returns an access token valid until it expires.
  
* you can then authenticate, by including the token, encoded [in
  base64](https://docs.microsoft.com/en-us/exchange/client-developer/legacy-protocols/how-to-authenticate-an-imap-pop-smtp-application-by-using-oauth#sasl-xoauth2),
  specifically as
  
```python
base64("user=" + user + "^Aauth=Bearer " + token + "^A^A" )
```

## IMAP

I use [offlineimap](https://github.com/OfflineIMAP) to download email.  Once I
figured out that the `offlineimaprc` file is not *quite* a python
file---specifically, it quotes by default, so adding quotes breaks
things---offlineimap started working again.  Credit to the author of `M365` for
making it so easy.

## SMTP

This was more interesting.  I use `mu4e` inside emacs, so I send email with
`smtpmail`.  A [long
thread](https://mail.gnu.org/archive/html/emacs-devel/2021-08/msg00036.html)
reveals that others have got oauth2 working with `sendmail`, and the patch has
even made it upstream, and is already in my emacs:

```lisp
(cl-defmethod smtpmail-try-auth-method
  (process (_mech (eql xoauth2)) user password)
  (smtpmail-command-or-throw
   process
   (concat "AUTH XOAUTH2 "
           (base64-encode-string
            (concat "user=" user "\1auth=Bearer " password "\1\1") t))))
```

This is documented:

> The process by which the SMTP library authenticates you to the server is known
as “Simple Authentication and Security Layer” (SASL). There are various SASL
mechanisms, and this library supports three of them: `cram-md5`, `plain`,
`login` and `xoauth2`, where the first uses a form of encryption to obscure your
password, while the other two do not. It tries each of them, in that order,
until one succeeds. (`xoauth2` requires using the `oauth2.el` library. You can
override this by assigning a specific authentication mechanism to a server by
including a key `smtp-auth` with the value of your preferred mechanism in the
appropriate `~/.authinfo` entry.

This is it.  Examining `smtpmail-auth-supported` shows that for some reason this
isn't enabled by default.  Thus we have to

```lisp
(add-to-list 'smtpmail-auth-supported 'xoauth2)
```

Now `smtpmail` tries to retrieve the the access token from `auth-store`, which
in turn looks it up in `.authinfo.gpg`, which looks something like:

```lisp
machine outlook.office365.com login EMAIL port 587 smtp-auth xoauth2 password PASS
```

Now, how do we get the access token?  Somewhere in that thread a horrible hack
was mentioned, and I decided to use it.  We can get an access token from the
refresh token like this (this took me far too long to figure out, but was
apparently so trivial to the original poster it wasn't even mentioned):

```lisp

(oauth2-token-access-token
 (oauth2-refresh-access
  (make-oauth2-token
   :refresh-token "<TOKEN>"
   :token-url "https://login.microsoftonline.com/common/oauth2/v2.0/token"
   :client-id "<THUNDERBIRD CLIENT ID>"
   :client-secret "<THUNDERBIRD CLIENT SECRET>"
   )))
```
Where the refresh token is the one we obtained earlier.  I simply placed this
code (without line breaks) in the password field of the authinfo line.  Since
emacs *evaluates* the field you can put arbitrary code in it, and in effect
perform code injection for a good purpose.  A better solution might be to store
the refresh token in one place and read it from there, so if we ever have to
change it it's easier.  Reading file contents is surprisingly [odd in emacs](https://stackoverflow.com/questions/34432246/):

```lisp
(with-temp-buffer
  (insert-file-contents "path/to/file")
  (buffer-string)
  )
```

## Legality

So with the aid of Thunderbird's not-so-secret application secret and a glorious
hack in `.authinfo.gpg` we can send and receive email.  Is this legal?
According to some claims in that thread, possibly not: apparently developers are
not supposed to share their app secret, although how they are supposed to avoid
doing so---since after all the application does need to *use* it, and it runs on
the user's machine, so intercepting it will be very easy---is unclear.
Thunderbird apparently got round this by registering the app with the Legal
Person of the organisation.  Whether that was to avoid being sued individually,
or to claim that they only shared it with themselves, I don't know.  In any case
Micro$oft apparently don't directly forbid 'embedding the application secret in
an opensource application' unlike Google.

In the longer run, the obvious solution is to host one's own email server and
stop worrying about all this.
