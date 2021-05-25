### [Preface]
iptables is a firewall program for Linux. </br>
It will monitor traffic from and to your server using **tables**. </br>
These **tables** contain sets of rules, called **chains**, that will filter incoming and outgoing data packets. </br>
When a packet matches a rule, it is given a **target**, which can be another chain or one of these special values:
- ACCEPT – will allow the packet to pass through.
- DROP   – will not let the packet pass through.
- RETURN – stops the packet from traversing through a chain and tell it to go back to the previous chain.

In this iptables tutorial, we are going to work with *one* of the *[3 default tables]*, called **filter**. \(mangle, filter, nat\)</br>
The **filter** table consists of three chains:
- INPUT   – controls incoming packets to the server (Inbound).
- OUTPUT  – filter packets that are going out from your server (Outbound).
- FORWARD – filters incoming packets that will be forwarded somewhere else (ie packets that will be routed towards another NIC).

### Install iptables
```bash
sudo apt-get update
sudo apt-get install iptables
```
### Check current filter table, 
```bash
sudo iptables -L -v -t filter
# -t filter could be omitted and achieve same effect
sudo iptables -L -v
```
Here, the -L option is used to list all the rules, and -v is for showing the info in a more detailed format.

#### Defining Chain Rules
Defining a rule means appending it to the chain. </br>
To do this, you need to insert the -A option (Append) right after the iptables command, like so:
```bash
sudo iptables -A <chain> -i <interface> -p <protocol (tcp/udp)> -s <source> --dport <port> -j <target>
sudo iptables -t <table> -A <chain> -i <interface> -p <protocol (tcp/udp)> -s <source> --dport <port> -j <target>
```
**parameter order MUST be respected**
- **-t** (optional) — Specify table, could be omitted and if so will points to the **filter** table
- **-A** (required) — Append rule to chain
- **-i** (interface) — the network interface whose traffic you want to filter, such as eth0, lo, ppp0, etc.
- **-p** (protocol) — the network protocol where your filtering process takes place. It can be either tcp, udp, udplite, icmp, sctp, icmpv6, and so on. Alternatively, you can type all to choose every protocol.
- **-s** (source) — the address from which traffic comes from. You can add a hostname or IP address.
- **–dport** (destination port) — the destination port number of a protocol, such as 22 (SSH), 443 (https), etc.
- **-j** (target) — the target name (ACCEPT, DROP, RETURN). You need to insert this every time you make a new rule.

### Enabling Traffic on Loopback interface
```bash
sudo iptables -A INPUT -i lo -j ACCEPT
```
### Enabling Connections on HTTP, SSH, and SSL Port
Next, we want http (port 80), https (port 443), and ssh (port 22) connections to work as usual. </br>
To do this, we need to specify the protocol (-p) and the corresponding port (–dport). </br>
You can execute these commands one by one:
```bash
sudo iptables -A INPUT -p tcp --dport 22 -j ACCEPT
sudo iptables -A INPUT -p tcp --dport 80 -j ACCEPT
sudo iptables -A INPUT -p tcp --dport 443 -j ACCEPT
```
### Filtering Packets Based on Source
Iptables allows you to filter packets based on an IP address or a range of IP addresses. </br>
You need to specify it after the -s option. </br>
- For example, to accept packets from 192.168.1.3, the command would be:
  ```bash
  sudo iptables -A INPUT -s 192.168.1.3 -j ACCEPT
  ```
- You can also reject packets from a specific IP address by replacing the ACCEPT target with DROP.
  ```bash
  sudo iptables -A INPUT -s 192.168.1.3 -j DROP
  ```
- If you want to drop packets from a range of IP addresses, you have to use the -m option and iprange module. </br>
  Then, specify the IP address range with –src-range. </br>
  Remember, a hyphen should separate the range of ip addresses without space, like this:
  ```bash
  sudo iptables -A INPUT -m iprange --src-range 192.168.1.100-192.168.1.200 -j DROP
  ```
### Dropping all Other Traffic
It is crucial to use the DROP target for all other traffic after defining –dport rules. </br>
This will prevent an unauthorized connection from accessing the server via other open ports. </br>
To achieve this, simply type:
```bash
sudo iptables -A INPUT -j DROP
```
Now, the connection outside the specified port will be dropped.

#### Deleting Rules
If you want to remove all rules and start with a clean slate, you can use the -F option (flush):
```bash
sudo iptables -F
```
This command erases all current rules. </br>
However, to delete a specific rule, you must use the -D option. </br>
First, you need to see all the available rules by entering the following command:
```bash
sudo iptables -L -v --line-numbers
```
You will get a list of rules with numbers </br>
To delete a rule, insert the corresponding chain and the number from the list. </br>
Let’s say for this iptables tutorial, we want to get rid of rule number three of the INPUT chain. </br>
The command should be:
```bash
sudo iptables -D INPUT 3
```
#### Persisting Changes
The iptables rules that we have created are saved in memory. </br>
That means we have to redefine them on reboot. </br>
To make these changes persistent after restarting the server, you can use this command:
```bash
sudo /sbin/iptables-save
```
It will save the current rules on the system configuration file, which will be used to reconfigure the tables every time the server reboots. </br>
Note that you should always run this command every time you make changes to the rules. </br>
For example, if you want to disable iptables, you need to execute these two lines:
```bash
sudo iptables -F
sudo /sbin/iptables-save
```
### Extras
#### configure iptable to nat port 53
- Enable ip forwarding
  sysctl
  ```bash
  sudo sysctl -w net.ipv4.ip_forward=1
  sudo sysctl -p /etc/sysctl.conf 
  ```
  Manually
  ```bash
  sudo vim /etc/sysctl.d/98-forward.conf
  # required
  net.ipv4.ip_forward = 1
  # optional
  net.ipv4.conf.default.proxy_arp = 1
  net.ipv4.conf.all.send_redirects = 0
  net.ipv4.conf.default.send_redirects = 0
  net.ipv4.conf.lo.send_redirects = 0
  net.ipv4.conf.xenbr0.send_redirects = 0
  net.ipv4.conf.default.rp_filter = 1
  net.ipv4.icmp_echo_ignore_broadcasts = 1
  net.ipv4.conf.default.accept_source_route = 0
  net.ipv4.conf.all.accept_redirects = 0
  net.ipv4.conf.all.send_redirects = 0
  kernel.sysrq = 1
  kernel.core_uses_pid = 1
  net.ipv4.tcp_syncookies = 1
  kernel.msgmnb = 65536
  kernel.msgmax = 65536
  kernel.shmmax = 4294967295
  kernel.shmall = 268435456
  vm.dirty_ratio = 5
  kernel.printk = 4 4 1 4
  ```
- Check
  ```bash
  cat /proc/sys/net/ipv4/ip_forward
  ```
- iptables rules \[[redhat]\]</br>
  public_net → eth0 → forward → eth1 → private_net (classic nat, ip_forwarding)
  ```bash
  sudo iptables -A FORWARD -i eth1 -j ACCEPT
  sudo iptables -A FORWARD -o eth1 -j ACCEPT
  sudo iptables -t nat -A PREROUTING -i eth0 -p udp --dport 53 -j DNAT --to <local_ip>:53
  sudo iptables -A FORWARD -i eth0 -p udp --dport 53 -d <local_ip> -j ACCEPT
  sudo iptables -t nat -A PREROUTING -i eth0 -p tcp --dport 53 -j DNAT --to <local_ip>:53
  sudo iptables -A FORWARD -i eth0 -p tcp --dport 53 -d <local_ip> -j ACCEPT
  sudo iptables -t nat -A POSTROUTING -o eth0 -j SNAT --to-source <eth0_ip>
  # or iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE
  ```
  same_net → eth0 → same_net (single address nat which is basicly dst/src rewrite, dumb idea but doable)
  ```bash
  sudo iptables -t nat -A PREROUTING -i eth0 -p udp --dport 53 -j DNAT --to <local_ip>:53
  sudo iptables -t nat -A PREROUTING -i eth0 -p tcp --dport 53 -j DNAT --to <local_ip>:53
  sudo iptables -t nat -A POSTROUTING -o eth0 -j SNAT --to-source <eth0_ip>
  # or iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE
  ```
#### Delete iptable rules
- Flush all
  ```bash
  sudo iptables --flush
  sudo iptables --delete-chain
  sudo iptables --table nat --flush
  sudo iptables --table nat --delete-chain
  sudo iptables -F
  ```
- [Manual delete]
  ```bash
  sudo iptables -t nat -v -L POSTROUTING -n --line-number
  sudo iptables -t nat -D POSTROUTING 1
  sudo iptables -t nat -v -L PREROUTING -n --line-number
  sudo iptables -t nat -D PREROUTING 1
  sudo iptables -v -L FORWARD -n --line-number
  sudo iptables -D FORWARD 3
  ```

[Preface]: https://www.hostinger.com/tutorials/iptables-tutorial
[3 default tables]: https://www.thegeekstuff.com/2011/01/iptables-fundamentals/
[redhat]: https://access.redhat.com/documentation/en-us/red_hat_enterprise_linux/4/html/security_guide/s1-firewall-ipt-fwd
[Manual delete]: https://www.cyberciti.biz/faq/how-to-iptables-delete-postrouting-rule/
