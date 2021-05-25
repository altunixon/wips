### [stackexchange] on remote tunnel
Think of your SSH connections as tubes. Big tubes. </br>
Normally, you'll reach through these tubes to run a shell on a remote computer. </br>
The shell runs in a virtual terminal (tty). But you know this part already.
</br>
Think of your tunnel as a tube within a tube. </br>
You still have the big SSH connection, but the -L or -R option lets you set up a smaller tube inside it.</br>
</br>
Every tube has a beginning and an end. </br>
The big tube, your SSH connection, started with your SSH client and ends up at the SSH server you connected to. </br>
All the smaller tubes have the same endpoints, except that the role of "start" or "end" is determined by whether you used -L or -R (respectively) to create them. </br>
</br>
(You haven't said, but I'm going to assume that the "remote" machine you've mentioned, the one behind the firewall, can access the Internet using Network Address Translation (NAT). This is kind of important, so please correct this assumption if it is false.)
</br>
When you create a tunnel, you specify an address and port on which it will answer, and an address and port to which it will be delivered. </br>
The -L option tells the tunnel to answer on the local side of the tunnel (the host running your client). </br>
The -R option tells the tunnel to answer on the remote side (the SSH server). </br>
</br>
![image tunnel]
</br>
So... To be able to SSH from the Internet into a machine behind a firewall, you need the machine in question to open an SSH connection to the outside world and include a -R tunnel whose "entry" point is the "remote" side of his connection. </br>
Of the two models shown above, you want the one on the right. </br>
From the firewalled host:
```bash
ssh -f -N -T -R22222:localhost:22 yourpublichost.example.com
```
This tells your client to establish a tunnel with a -Remote entry point. </br>
Anything that attaches to port 22222 on the far end of the tunnel will actually reach "localhost port 22", where "localhost" is from the perspective of the exit point of the tunnel (i.e. your ssh client). </br>
The other options are:
  - -f: tells ssh to background itself after it authenticates, so you don't have to sit around running something on the remote server for the tunnel to remain alive. </br>
  - -N: says that you want an SSH connection, but you don't actually want to run any remote commands. If all you're creating is a tunnel, then including this option saves resources. </br>
  - -T: disables pseudo-tty allocation, which is appropriate because you're not trying to create an interactive shell. </br>
There will be a password challenge unless you have set up DSA or RSA keys for a passwordless login. </br>
Note that it is STRONGLY recommended that you use a throw-away account (not your own login) that you set up for just this tunnel/customer/server. </br>
Now, from your shell on yourpublichost, establish a connection to the firewalled host through the tunnel:
```bash
ssh -p 22222 username@localhost
```
You'll get a host key challenge, as you've probably never hit this host before. </br>
Then you'll get a password challenge for the username account (unless you've set up keys for passwordless login). </br>
If you're going to be accessing this host on a regular basis, you can also simplify access by adding a few lines to your ~/.ssh/config file:
```bash
host remotehostname
    User remoteusername
    Hostname localhost
    Port 22222
```
Adjust remotehostname and remoteusername to suit. </br>
The remoteusername field must match your username on the remote server, but remotehostname can be any hostname that suits you, it doesn't have to match anything resolvable. </br>

### Extra tunception
#### Tunnel type L (local)
![image tunL] </br>
-L Specifies that the given port on the local (client) host is to be forwarded to the given host and port on the remote side. </br>
```bash
ssh -L sourcePort:forwardToHost:onPort connectToHost
```
means: connect with ssh to connectToHost, and forward all connection attempts to the local sourcePort to port onPort on the machine called forwardToHost, which can be reached from the connectToHost machine. </br>
</br>
#### Tunnel type R (local)
![image tunR] </br>
-R Specifies that the given port on the remote (server) host is to be forwarded to the given host and port on the local side. </br>
```bash
ssh -R sourcePort:forwardToHost:onPort connectToHost
```
means: connect with ssh to connectToHost, and forward all connection attempts to the remote sourcePort to port onPort on the machine called forwardToHost, which can be reached from your local machine. </br>
</br>
#### Additional options
  - -f: tells ssh to background itself after it authenticates, so you don't have to sit around running something on the remote server for the tunnel to remain alive.
  - -N: says that you want an SSH connection, but you don't actually want to run any remote commands. If all you're creating is a tunnel, then including this option saves resources.
  - -T: disables pseudo-tty allocation, which is appropriate because you're not trying to create an interactive shell.


[stackexchange]: https://unix.stackexchange.com/questions/46235/how-does-reverse-ssh-tunneling-work
[image tunnel]: https://i.stack.imgur.com/HbSEM.png
[image tunL]: https://i.stack.imgur.com/a28N8.png
[image tunR]: https://i.stack.imgur.com/4iK3b.png
