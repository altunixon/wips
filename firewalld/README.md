Firewalld stores its configuration in **"/etc/firewalld"** and within that directory you can find various configuration files:
  - File **./firewalld.conf** provides overall configuration.
  - Files in the **./zones/** directory provide your custom firewall rules for each zone.
  - Files in the **./services/** directory provide custom services you have defined.
  - Files in the **./icmptypes/** directory provide custom icmptypes you have defined.

There is a matching directory structure in **"/usr/lib/firewalld"** which provides the defaults for zones, services and icmptypes, in case you want to start customizing from a template, or simply see what the files look like. </br>
The firewall configuration of the main services (ftp, httpd, etc) comes in the **"/usr/lib/firewalld/services"** directory. </br>
But it is still possible to add new ones in the **"/etc/firewalld/services"** directory. </br>
Also, if files exist at both locations for the same service, the file in the **"/etc/firewalld/services"** directory takes precedence. </br>
