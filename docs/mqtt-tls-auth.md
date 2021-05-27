## Install MQTT
```bash
sudo apt-get update
sudo apt-get install -y mosquitto mosquitto-clients mosquitto-dev
sudo systemctl status mosquitto
sudo systemctl stop mosquitto
```

## Generate self signed certificate for MQTT
- Step.1: Create a key pair for the CA
  ```bash
  cd /etc/mosquitto/certs/

  sudo openssl genrsa -des3 -out ca.key 2048

  ls -l ./
  -rw------- 1 root root 1.8K 2021/05/26 15:30:06 ca.key
  ```
  Note: it is OK to create a password protected key for the CA.
- Step.2: Create a certificate for the CA using the CA key that we created in step 1
  ```bash
  sudo openssl req -new -x509 -days 3650 -key ca.key -out ca.crt

  ls -l ./
  -rw-r--r-- 1 root root 1.3K 2021/05/26 15:31:17 ca.crt
  -rw------- 1 root root 1.8K 2021/05/26 15:30:06 ca.key
  ```
  **Note**: CA info could be whatever but the **Common Name must be DIFFERENT between CA and Server** for the self signed certificate to work
- Step.3: Create a key pair that will be used by MQTT server
  ```bash
  sudo openssl genrsa -out mqtt.key 2048

  ls -l ./
  -rw-r--r-- 1 root root 1.3K 2021/05/26 15:31:17 ca.crt
  -rw------- 1 root root 1.8K 2021/05/26 15:30:06 ca.key
  -rw------- 1 root root 1.7K 2021/05/26 15:32:27 mqtt.key
  ```
- Step.4: Create a certificate request .csr.
  ```bash
  sudo openssl req -new -out mqtt.csr -key mqtt.key

  ls -l ./
  -rw-r--r-- 1 root root 1.3K 2021/05/26 15:31:17 ca.crt
  -rw------- 1 root root 1.8K 2021/05/26 15:30:06 ca.key
  -rw-r--r-- 1 root root  976 2021/05/26 15:33:19 mqtt.csr
  -rw------- 1 root root 1.7K 2021/05/26 15:32:27 mqtt.key
  ```
  **Note**: When filling out the form the common name is important and is usually the domain name of the server.
- Step.5: Use the CA key to verify and sign the server certificate. This creates the server.crt file
  ```bash
  sudo openssl x509 -req -in mqtt.csr -CA ca.crt -CAkey ca.key -CAcreateserial -out mqtt.crt -days 3650

  ls -l ./
  -rw-r--r-- 1 root root 1.3K 2021/05/26 15:31:17 ca.crt
  -rw------- 1 root root 1.8K 2021/05/26 15:30:06 ca.key
  -rw-r--r-- 1 root root   41 2021/05/26 15:33:56 ca.srl
  -rw-r--r-- 1 root root 1.2K 2021/05/26 15:33:56 mqtt.crt
  -rw-r--r-- 1 root root  976 2021/05/26 15:33:19 mqtt.csr
  -rw------- 1 root root 1.7K 2021/05/26 15:32:27 mqtt.key
  ```
- Step.6: Verify the certificate with signed ca cert
  ```bash
  sudo openssl verify -CAfile ca.crt mqtt.crt

  mv ./ca.* /etc/mosquitto/ca_certificates/
  ```
- Problems and Notes:</br>
  While creating and working through these procedures you might encounter these following problems:
  1. Error when connecting due to the common name on the server certificate not matching (name resolve error).
  2. Password protected the server key and the broker couldn’t read it.</br>
     I found this command which will remove the passphrase from the key `openssl rsa -in server.key -out server-nopass.key`.
  3. Client not using the correct name for the broker\(server\).</br>
     Client connects using the IP address and not the common name defined in the certificate.</br>
     You can use the tls_insecure_set(True) option to override name checking as a temporary measure.
  4. Authentication errors as I had previously configured my broker to require passwords.</br>
     Therefore try to start with a clean conf file and beware that the errors you are getting may not be SSL related.

## Configure MQTT server to use TLS
```bash
cat << EOT >> /etc/mosquitto/conf.d/00.tls.conf
# Default bind is 0.0.0.0
#bind_address
# Default port is 1883
port 8883
#capath <unused>
cafile /etc/mosquitto/ca_certificates/ca.crt
keyfile /etc/mosquitto/certs/mqtt.key
certfile /etc/mosquitto/certs/mqtt.crt
tls_version tlsv1
EOT
```

## Configure MQTT to require client authentication \(basic auth\)
```bash
mosquitto_passwd --help
Usage: mosquitto_passwd [-c | -D] passwordfile username
       mosquitto_passwd -b passwordfile username password
       mosquitto_passwd -U passwordfile

sudo mosquitto_passwd -c /etc/mosquitto/users.pwd username
sudo chmod 640 /etc/mosquitto/users.pwd

cat << EOT >> /etc/mosquitto/conf.d/01.auth.conf
password_file /etc/mosquitto/users.pwd
EOT
```

## MQTT Usage
- Restart MQTT after you make changes to configuration or the password file for them to take effect.
  ```bash
  sudo systemctl restart mosquitto.service
  ```
- Send message to a topic with cmdline client mosquitto_pub
  ```bash
  mosquitto_pub --cafile /etc/mosquitto/ca_certificates/ca.crt -h cert_common_name -t topic_name -m message_text -p 8883 -d -u user_name -P user_pass
  # Add -r : message should be retained until it is received by a Subscriber.
  ```
- Receive(subscribe) to a topic
  ```bash
  mosquitto_sub --cafile /etc/mosquitto/ca_certificates/ca.crt -h cert_common_name -t topic_name -p 8883 -d -u user_name -P user_pass
  # Add -C <msg_count> : To disconnect and exit after receiving the 'msg_count' messages.
  ```
- Add `--insecure`: do not check that the server certificate hostname matches the remote hostname if you encounted TLS error.
