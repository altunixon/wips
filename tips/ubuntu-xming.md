#### Ubuntu side: Set X11 display
```bash
export DISPLAY=localhost:0.0
```
#### Windows side: 
- Install Xming [(Centos)](https://wiki.centos.org/HowTos/Xming) <br/>
  The Xming Installer is suitable for Windows 10/8/7/Vista/XP Desktops as well as Windows Server 2012/2008/2003. <br/>
  Steps: 
    - Use the link below to download the latest Xming installer from Sourceforge. 
      http://sourceforge.net/projects/xming/files/latest/download
    - Once the installer is downloaded to your desktop, double-click the Xming icon to start the installation process
    - On the "Welcome to the Xming Setup Wizard" screen click **Next**
    - Accept the C:\Program Files\Xming or browse a different folder for installation destination. To continue click **Next** 
    - When prompted for which components to install, accept the defaults and click Next 
    - On the "Select Additional Tasks" screen, select the additional tasks such as desktop icons then click Next 
    - The next screen shows all installation settings. If everything correct click Install 
    - Click Finish on the "Completing the Xming Setup Wizard" window. 
  Your Windows desktop is now equipped to display X11-based graphical applications remotely. 
- Cygwin .ssh/config
```
Host x
    Hostname 192.168.1.1
    ForwardX11 yes
```
