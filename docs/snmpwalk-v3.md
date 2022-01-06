## Install snmp client and mib-downloader
```bash
sudo apt-get install snmp snmp-mibs-downloader
```
Note: MIBs is just vendor defined wrappers for OID since each vendor define their own object i.e: Linux OIDs might differ from Microsh-
## Download Diskstaion MIB files and copy to mib location
```
wget https://global.download.synology.com/download/Document/Software/DeveloperGuide/Firmware/DSM/All/enu/Synology_MIB_File.zip
unzip Synology_MIB_File.zip
cd Synology_MIB_File
ls -1
SYNOLOGY-DISK-MIB.txt
SYNOLOGY-EBOX-MIB.txt
SYNOLOGY-FLASHCACHE-MIB.txt
SYNOLOGY-GPUINFO-MIB.txt
SYNOLOGY-ISCSILUN-MIB.txt
SYNOLOGY-ISCSITarget-MIB.txt
SYNOLOGY-NFS-MIB.txt
SYNOLOGY-PORT-MIB.txt
SYNOLOGY-RAID-MIB.txt
SYNOLOGY-SERVICES-MIB.txt
SYNOLOGY-SHA-MIB.txt
SYNOLOGY-SMART-MIB.txt
SYNOLOGY-SPACEIO-MIB.txt
SYNOLOGY-STORAGEIO-MIB.txt
SYNOLOGY-SYSTEM-MIB.txt
SYNOLOGY-UPS-MIB.txt
chmod 644 ./*.txt
cp ./*.txt /usr/share/snmp/mibs/
```

## snmpwall/snmpget example
```bash
snmp_user="alt"
snmp_passwd="WeakSauce"
snmpwalk -v3 -l authPriv -u "$snmp_user" -a SHA -A "$snmp_passwd" -x AES -X "$snmp_passwd" 192.168.11.2 SYNOLOGY-SYSTEM-MIB::temperature
snmpwalk -v3 -l authPriv -u "$snmp_user" -a SHA -A "$snmp_passwd" -x AES -X "$snmp_passwd" 192.168.11.2 UCD-SNMP-MIB::memTotalReal
snmpwalk -v3 -l authPriv -u "$snmp_user" -a SHA -A "$snmp_passwd" -x AES -X "$snmp_passwd" 192.168.11.2 UCD-SNMP-MIB::memAvailReal
snmpwalk -v3 -l authPriv -u "$snmp_user" -a SHA -A "$snmp_passwd" -x AES -X "$snmp_passwd" 192.168.11.2 SYNOLOGY-DISK-MIB::diskID
snmpwalk -v3 -l authPriv -u "$snmp_user" -a SHA -A "$snmp_passwd" -x AES -X "$snmp_passwd" 192.168.11.2 SYNOLOGY-DISK-MIB::diskModel
snmpwalk -v3 -l authPriv -u "$snmp_user" -a SHA -A "$snmp_passwd" -x AES -X "$snmp_passwd" 192.168.11.2 SYNOLOGY-DISK-MIB::diskType
snmpwalk -v3 -l authPriv -u "$snmp_user" -a SHA -A "$snmp_passwd" -x AES -X "$snmp_passwd" 192.168.11.2 SYNOLOGY-DISK-MIB::diskRole
snmpwalk -v3 -l authPriv -u "$snmp_user" -a SHA -A "$snmp_passwd" -x AES -X "$snmp_passwd" 192.168.11.2 SYNOLOGY-DISK-MIB::diskRemainLife
```
- -l: Level authPriv
- -u: User name
- -a: User's password hash algorithm
- -A: Password string
- -x: SNMP Privacy encryption algorithm
- -X: SNMP Privacy password string
- 192.168.11.2: SNMP server IP Address
- UCD-SNMP-MIB: Correlate to one of the MIB.txt files in `/usr/share/snmp/mibs/` or other mib search locations

```bash
snmpget -v3 -l authPriv -u "$snmp_user" -a SHA -A "$snmp_passwd" -x AES -X "$snmp_passwd" 192.168.11.2 \
    SYNOLOGY-SYSTEM-MIB::temperature.0 \
    UCD-SNMP-MIB::memTotalReal.0 \
    UCD-SNMP-MIB::memAvailReal.0
snmpget -v3 -l authPriv -u "$snmp_user" -a SHA -A "$snmp_passwd" -x AES -X "$snmp_passwd" 192.168.11.2 \
    SYNOLOGY-DISK-MIB::diskID.5 \
    SYNOLOGY-DISK-MIB::diskModel.5 \
    SYNOLOGY-DISK-MIB::diskType.5 \
    SYNOLOGY-DISK-MIB::diskRole.5
```
Note: snmpget does support multiple query string but it needs the exact OID/MIB code of the object \(Notice the .0 and .5 at the end\)
## Notes
- SNMP v3 Privacy password does not support special characters like `!` or `$`, so use ASCII accordingly
- MIB search path: /home/alt/.snmp/mibs:/usr/share/snmp/mibs:/usr/share/snmp/mibs/iana:/usr/share/snmp/mibs/ietf:/usr/share/mibs/site:/usr/share/snmp/mibs:/usr/share/mibs/iana:/usr/share/mibs/ietf:/usr/share/mibs/netsnmp
- For full list of Diskstation MIB Object Identifier, See: [Synology MIB documentation]


[Synology MIB documentation]: https://global.download.synology.com/download/Document/Software/DeveloperGuide/Firmware/DSM/All/enu/Synology_DiskStation_MIB_Guide.pdf 
