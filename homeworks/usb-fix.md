[etcher](https://www.balena.io/blog/did-etcher-break-my-usb-sd-card/)
### Windows diskpart.exe
```cmd
diskpart.exe
DISKPART> list disk
DISKPART> select disk N
DISKPART> clean
DISKPART> create partition primary
DISKPART> select partition 1
DISKPART> format quick
```
### Linux dd
```bash
sudo umount /dev/xxx
sudo dd if=/dev/zero of=/dev/xxx bs=512 count=1 conv=notrunc
```
