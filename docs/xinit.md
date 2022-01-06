## startx
startx runs xinit which starts an X server and a client session.</br>
The client session is `~/.xinitrc` if present, and otherwise `/etc/X11/xinit/xinitrc` \(the location may vary between distributions\).</br>
What this script does varies between distributions.</br>
On Debian (including derivatives such as Raspbian), /etc/X11/xinit/xinitrc runs /etc/X11/Xsession which in turn runs scripts in /etc/X11/Xsession.d.</br>
The Debian scripts look for a user session in other files \(`~/.xsession`, `~/.xsessionrc`, `~/.Xsession`\) and, if no user setting is applicable, runs `x-session-manager` \(falling back to `x-window-manager` if no \[session manager\] is installed, falling back to `x-terminal-emulator` in the unlikely case that no window manager is installed\).</br>

## dot files
If you want control over what gets executed, you can create one of the user files, either `~/.xsession` or `~/.xinitrc.`</br>
The file `~/.xsession` is also used if you log in on a display manager \(i.e. if you type your password in a GUI window\).</br>
The file `~/.xinitrc` is specific to `xinit` and `startx`.</br>
Using `~/.xsession` goes through `/etc/X11/Xsession` so it sets up things like input methods, resources, password agents, etc.</br>
If you use `.xinitrc`, you'll have to do all of these manually.</br>
Once again, I'm describing Debian here, other Unix variants might set things up differently.</br>
The use of `~/.xinitrc` to specify what gets executed when you run `startx` or `xinit` is universal.</br>
</br>
Whether you use `~/.xinitrc` or `~/.xsession`, this file \(usually a shell script, but it doesn't have to be if you really want to use something else\) must prepare whatever needs to be prepared \(e.g. keyboard settings, resources, applets that aren't started by the window manager, etc.\), and then at the end run the program that manages the session.</br>
When the script ends, the session terminates.</br>
Typically, you would use exec at the end of the script, to replace the script by the session manager or window manager.</br>
</br>

## session managers
Your system presumably has `/usr/bin/startlxde` as the system-wide default session manager.</br>
On Debian and derivatives, you can check the available session managers with
```bash
update-alternatives --list x-session-manager
```
or get a more verbose description indicating which one is current with
```bash
update-alternatives --display x-session-manager
```
If LXDE wasn't the system-wide default and you wanted to make it the default for your account, you could use the following `~/.xsession` file:
```bash
#!/bin/sh
exec startlxde
```
On some Unix variants, that would only run for graphical logins, not for startx, so you'd also need to create an identical `~/.xinitrc`.</br>
\(Or not identical: in `~/.xsession`, you might want to do other things, because that's the first file that's executed in a graphical session; for example you might put `source ~/.profile` near the top, to set some environment variables.\)</br>

## alternative sessions
If you want to try out other environments as a one-off, you can specify a different program to run on the command line of startx itself.</br>
The startx program has a quirk: you need to use the full path to the program.</br>
```bash
startx /usr/bin/startkde
```
The startx command also lets you specify arguments to pass to the server.</br>
For example, if you want to run multiple GUI sessions at the same time, you can pass a different display number each time.</br>
Pass server arguments after `--` on the command line of `startx`.
```bash
export MY_DISPLAY=:50
startx /usr/bin/startkde -- $MY_DISPLAY
```
