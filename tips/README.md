### Screen auto attach ONLY if login from ssh and is the first connection /dev/pts/0
```bash
echo "if [ $STY = '' ] && [ $SSH_TTY != '' ] && [ $SSH_TTY = "/dev/pts/0" ]; then screen -xR; fi" >> ~/.bashrc
```
### Disable/Enable lightdm
```bash
alias lightdm-disable="sudo systemctl disable lightdm.service"
alias lightdm-enable="sudo dpkg-reconfigure lightdm"
```
Debian still uses SysVinit, but supports interoperability with systemd through a nifty little program called systemd-sysv-generator. </br>
Thus, after you removed lightdm service file, it can't be enable simply with "systemctl enable lightdm.service" </br>
but require "dpkg-reconfigure lightdm" to rebuild service file with lightdm post install instead.

### DYI Route 53 dynamic DNS \[[Lambda server-less dns update]\]
#### TL;DR Edition:
- Register a DNS name on Route53.
- Create AWS REST API Gateway.
- Client send REST to API Gateway with JSON data format {"ip": "xxx.yyy.zzz.nnn", "fqdn": "myfqdn.net", "hash": AES/Blowfish}
- Gateway forward JSON data to Lambda function.
- Lambda check if hash matches secret then make API call to Route53 and update address.
- Lambda return JSON reply to client.



[Lambda server-less dns update]: https://aws.amazon.com/jp/blogs/startups/building-a-serverless-dynamic-dns-system-with-aws/
