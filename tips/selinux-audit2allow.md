#### Reading material [[source]]
RHEL Official document: [Fedora SELinux User Guide] </br>
If you're considering SELinux, I recommend the book [SELinux by Example]. </br>
I worked for a company that had SELinux enabled, in enforcing mode, on every system. </br>
The key for us was understanding and using the audit2why for debugging and audit2allow to create new context rules. </br>
#### Usage
- First, we'd generate a template with audit2allow, and then use a script to build it, like this: </br>
  ```bash
  export NAME="my_serviced"
  sudo audit2allow -m "${NAME}" -i /var/log/audit/audit.log > ${NAME}.te
  sudo setup_semodule ${NAME}
  ```
- The setup_semodule script:
  ```bash
  #!/bin/sh

  # Where to store selinux related files
  SOURCE=/etc/selinux/local
  BUILD=/etc/selinux/local
  NAME=$1
  
  /usr/bin/checkmodule -M -m -o ${BUILD}/${NAME}.mod ${SOURCE}/${NAME}.te
  /usr/bin/semodule_package -o ${BUILD}/${NAME}.pp -m ${BUILD}/${NAME}.mod
  /usr/sbin/semodule -i ${BUILD}/${NAME}.pp
  /bin/rm ${BUILD}/${NAME}.mod ${BUILD}/${NAME}.pp
  ```
  This builds the module from the template (.te file), generates a package, and then loads the module.



[source]: https://serverfault.com/questions/30796/reasons-to-disable-enable-selinux
[SELinux by Example]: http://www.informit.com/store/product.aspx?isbn=0131963694
[Fedora SELinux User Guide]: https://docs.fedoraproject.org/en-US/Fedora/13/html/Security-Enhanced_Linux/chap-Security-Enhanced_Linux-Introduction.html#sect-Security-Enhanced_Linux-Introduction-Benefits_of_running_SELinux
