#!/bin/bash

# Extract data from nandroid backup of Google Authenticator 2
# From: https://gist.github.com/f9d82ca631df0d4d32a0.git
# > /data/data/com.google.android.apps.authenticator2/databases/databases
# require: sqlite3 + qrencode
sqlite3 databases << EOT
.headers off
.mode csv
.output codes.csv
select printf("otpauth://totp/%s?secret=%s&issuer=%s",email,secret,issuer) from accounts;
EOT
# Unquote lines
sed -i 's/\"//g' codes.csv

# Display as QR CODE
i=0;
while read p; do
   qrencode -t ANSIUTF8 -8 -o - "${p}" 
   echo "${p}"
   echo -e "\n\n"
done < codes.csv
rm codes.csv

# Or just run
# qrencode -t ANSIUTF8 -8 -o - 'otpauth://totp/<ur_email>?secret=<ur_secret>&issuer=<ur_issuer>'
