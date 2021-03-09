### Source: https://askubuntu.com/questions/1031709/ubuntu-18-04-switch-back-to-etc-network-interfaces
### I. Reinstall the ifupdown package:
```bash
sudo apt-get update -y
sudo apt-get install -y ifupdown
```
### II. Configure your /etc/network/interfaces or interfaces.d file with configuration stanzas such as:
```bash
# /etc/network/interfaces
# The loopback network interface
auto lo
iface lo inet loopback
source /etc/network/interfaces.d/*

# /etc/network/interfaces.d/eth{0,1,1-0}
# static interface, without dns
allow-hotplug eth0
auto eth0
iface eth0 inet static
    address 172.16.1.2
    netmask 255.255.255.0
    
# static, with dns
allow-hotplug eth1
auto eth1
iface eth1 inet static
    address 192.168.1.2
    netmask 255.255.255.0
    broadcast 192.168.1.255
    gateway 192.168.1.1
    # Only relevant if you make use of RESOLVCONF(8) or similar...
    dns-nameservers 9.9.9.9 1.1.1.1
    
# secondary interface, handy for replacing existing server
allow-hotplug eth1:0
auto eth1:0
iface eth1:0 inet static
    address 192.168.1.20
    netmask 255.255.255.0
```
### III. Make the configuration effective (no reboot needed):
```bash
sudo ifdown --force enp0s3 lo && ifup -a
sudo systemctl unmask networking
sudo systemctl enable networking
sudo systemctl restart networking
```
### IV. Disable and remove the unwanted services:
```bash
sudo systemctl stop systemd-networkd.socket systemd-networkd networkd-dispatcher systemd-networkd-wait-online
sudo systemctl disable systemd-networkd.socket systemd-networkd networkd-dispatcher systemd-networkd-wait-online
sudo systemctl mask systemd-networkd.socket systemd-networkd networkd-dispatcher systemd-networkd-wait-online
sudo apt-get --assume-yes purge nplan netplan.io
```
### V. DNS Resolver
Because Ubuntu Bionic Beaver (18.04) make use of the DNS stub resolver as provided by SYSTEMD-RESOLVED.SERVICE(8), 
you SHOULD also add the DNS to contact into the /etc/systemd/resolved.conf file. </br>
For instance:
```bash
# /etc/systemd/resolved.conf
DNS=9.9.9.9 1.1.1.1
```
and then restart the systemd-resolved service once done:
```bash
sudo systemctl restart systemd-resolved
```
The DNS entries in the ifupdown INTERFACES(5) file, as shown above, are only relevant if you make use of RESOLVCONF(8) or similar.

### Optional, Default route configure https://anova.be/blog/controlling-which-outbound-ip-use/
Using ip route to control outbound IP:
```bash
# route
Kernel IP routing table
Destination     Gateway         Genmask         Flags Metric Ref    Use Iface
192.168.0.0     *               255.255.255.0   U     0      0        0 em1
link-local      *               255.255.0.0     U     1002   0        0 em1
default         192.168.0.1     0.0.0.0         UG    0      0        0 em1
```
Next, we delete the default route
```bash
# ip route del default
```
Check if the default route is indeed gone :
```bash
# route
Kernel IP routing table
Destination     Gateway         Genmask         Flags Metric Ref    Use Iface
192.168.0.0     *               255.255.255.0   U     0      0        0 em1
link-local      *               255.255.0.0     U     1002   0        0 em1
```
Now we’re going to add the default route again. </br>
We give the device (dev), the default gateway (via) and an extra parameter with the desired IP of the interface to use four outbound connections :
```bash
#                         <nic>   <  gateway  >   < nic_addr  >
# ip route add default dev em1 via 192.168.0.1 src 192.168.0.5
```
Key here is the ‘src’ parameter. This specifies the ip to use for outbound traffic
