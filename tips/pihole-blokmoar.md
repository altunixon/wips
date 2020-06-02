#### Pihole's [Commonly Whitelist Addr](https://discourse.pi-hole.net/t/commonly-whitelisted-domains/212) probly overkill for home uses
Ex: Google services
```bash
pihole -w clients4.google.com 
pihole -w clients2.google.com
pihole -w android.clients.google.com
pihole -w googleapis.l.google.com
```
#### [Blocklist Collection](https://firebog.net/)
```bash
curl https://s3.amazonaws.com/lists.disconnect.me/simple_malvertising.txt | xargs -I {} pihole -b "{}"
```
