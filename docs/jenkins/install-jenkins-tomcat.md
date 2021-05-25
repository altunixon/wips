#### Install Java 8
```bash
sudo apt-get update -y
sudo apt-cache search openjdk
sudo apt-get install -y openjdk-8-jdk
```
#### Jenkins Requirement
For reference, as long as major version matches 1.8.x, minor could probly be safely ignored.
```bash
java -version
```
openjdk version "1.8.0_252" </br>
OpenJDK Runtime Environment (build 1.8.0_252-8u252-b09-1ubuntu1-b09) </br>
OpenJDK 64-Bit Server VM (build 25.252-b09, mixed mode) </br>
#### [Jenkins] on [Tomcat 9]
```bash
wget http://mirrors.jenkins.io/war-stable/latest/jenkins.war
wget https://ftp.tsukuba.wide.ad.jp/software/apache/tomcat/tomcat-9/v9.0.35/bin/apache-tomcat-9.0.35.tar.gz
tar -zxf apache-tomcat-9.0.35.tar.gz
mv ./jenkins.war ./tomcat/webapps/
vim ./tomcat/conf/server.xml
```
Edit following values in server.xml
```xml
<Connector port="9090" maxHttpHeaderSize="8192"
    maxThreads="150" minSpareThreads="25" maxSpareThreads="75"
    enableLookups="false" redirectPort="8443" acceptCount="100"
    connectionTimeout="20000" disableUploadTimeout="true" />
```
- port= Listening port
- redirectPort= Redirect for https:// connection scheme \(optional, needs in-depth [SSL configuration]\)
#### Firewalld configure
```bash
JENKPORT=9090
firewall-cmd --permanent --new-service=jenkins
firewall-cmd --permanent --service=jenkins --set-short="Jenkins ports"
firewall-cmd --permanent --service=jenkins --set-description="Jenkins Port Allow"
firewall-cmd --permanent --service=jenkins --add-port=$JENKPORT/tcp
firewall-cmd --permanent --add-service=jenkins --zone=home
firewall-cmd --reload
firewall-cmd --list-all-zones
```


[Jenkins]: https://www.jenkins.io/download/
[Tomcat 9]: https://tomcat.apache.org/download-90.cgi
[SSL Configuration]: https://tomcat.apache.org/tomcat-9.0-doc/ssl-howto.html
