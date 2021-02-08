### Hostname
```bash
sudo apt-get update
sudo apt-get install -y vim screen
echo -e 'set mouse-=a\nset tabstop=4\nset shiftwidth=4\nset softtabstop=4\nset expandtab\n' > ~/.vimrc
nh="XXX"
sed -i 's/raspberrypi/'"$nh"'/g' /etc/hostname
sed -i 's/raspberrypi/'"$nh"'/g' /etc/hosts
```
### User add
```bash
passwd root
# PLACEHOLDER
```
### Setup NICs
- Disable IPv6
  ```bash
  dip6="net.ipv6.conf.all.disable_ipv6=1\nnet.ipv6.conf.default.disable_ipv6=1\nnet.ipv6.conf.lo.disable_ipv6=1\nnet.ipv6.conf.eth0.disable_ipv6=1\n"
  [ ! -f /etc/sysctl.d/96-disable-ipv6.conf ] && echo -e "$dip6" >> /etc/sysctl.d/96-disable-ipv6.conf || echo "IPv6 Already disabled?"
  ```
- Disable onboard wireless devices
  Hard disable (device tree)
  ```bash
  vim /boot/config.txt
  [All]
  dtoverlay=disable-wifi
  dtoverlay=disable-bt
  ```
  Soft disable (driver blacklist)
  ```bash
  echo -e 'blacklist brcmfmac\nblacklist brcmutil\n' >> /etc/modprobe.d/brcm-blacklist.conf
  ```
- Static addresses (optional, static ip setup via dhcp is preferred)
  ```bash
  vim /etc/dhcpcd.conf
  interface eth0
    static ip_address=192.168.11.61/24    
    static routers=192.168.11.1
    static domain_name_servers=192.168.11.53 1.1.1.1
  ```
### Setup environment
```bash
sudo apt-get update
sudo apt-get upgrade
sudo apt-get install -y nfs-common
sudo apt-get install -y PLACEHOLDER
```
