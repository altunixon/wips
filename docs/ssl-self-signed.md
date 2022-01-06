It's easy to create a self-signed certificate. You just use the openssl req command. It can be tricky to create one that can be consumed by the largest selection of clients, like browsers and command line tools.

It's difficult because the browsers have their own set of requirements, and they are more restrictive than the IETF. The requirements used by browsers are documented at the CA/Browser Forums (see references below). The restrictions arise in two key areas: (1) trust anchors, and (2) DNS names.

Modern browsers (like the warez we're using in 2014/2015) want a certificate that chains back to a trust anchor, and they want DNS names to be presented in particular ways in the certificate. And browsers are actively moving against self-signed server certificates.

Some browsers don't exactly make it easy to import a self-signed server certificate. In fact, you can't with some browsers, like Android's browser. So the complete solution is to become your own authority.

In the absence of becoming your own authority, you have to get the DNS names right to give the certificate the greatest chance of success. But I would encourage you to become your own authority. It's easy to become your own authority, and it will sidestep all the trust issues (who better to trust than yourself?).

This is probably not the site you are looking for!
The site's security certificate is not trusted!

This is because browsers use a predefined list of trust anchors to validate server certificates. A self-signed certificate does not chain back to a trusted anchor.

The best way to avoid this is:
- 1: Create your own authority (i.e., become a CA)
- 2: Create a certificate signing request (CSR) for the server
- 3: Sign the server's CSR with your CA key
- 4: Install the server certificate on the server
- 5: Install the CA certificate on the client

Step 1 - Create your own authority just means to create a self-signed certificate with CA: true and proper key usage. That means the Subject and Issuer are the same entity, CA is set to true in Basic Constraints (it should also be marked as critical), key usage is keyCertSign and crlSign (if you are using CRLs), and the Subject Key Identifier (SKI) is the same as the Authority Key Identifier (AKI).

To become your own certificate authority, see: How do you sign a certificate signing request with your certification authority? on Stack Overflow. Then, import your CA into the Trust Store used by the browser.

Steps 2 - 4 are roughly what you do now for a public facing server when you enlist the services of a CA like Startcom or CAcert. Steps 1 and 5 allows you to avoid the third-party authority, and act as your own authority (who better to trust than yourself?).

The next best way to avoid the browser warning is to trust the server's certificate. But some browsers, like Android's default browser, do not let you do it. So it will never work on the platform.

The issue of browsers (and other similar user agents) not trusting self-signed certificates is going to be a big problem in the Internet of Things (IoT). For example, what is going to happen when you connect to your thermostat or refrigerator to program it? The answer is, nothing good as far as the user experience is concerned.

The W3C's WebAppSec Working Group is starting to look at the issue. See, for example, Proposal: Marking HTTP As Non-Secure.

How to create a self-signed certificate with OpenSSL

The commands below and the configuration file create a self-signed certificate (it also shows you how to create a signing request). They differ from other answers in one respect: the DNS names used for the self signed certificate are in the Subject Alternate Name (SAN), and not the Common Name (CN).

The DNS names are placed in the SAN through the configuration file with the line subjectAltName = @alternate_names (there's no way to do it through the command line). Then there's an alternate_names section in the configuration file (you should tune this to suit your taste):
```ini
[ alternate_names ]

DNS.1       = example.com
DNS.2       = www.example.com
DNS.3       = mail.example.com
DNS.4       = ftp.example.com

# Add these if you need them. But usually you don't want them or
#   need them in production. You may need them for development.
# DNS.5       = localhost
# DNS.6       = localhost.localdomain
# IP.1        = 127.0.0.1
# IP.2        = ::1
```
It's important to put DNS name in the SAN and not the CN, because both the IETF and the CA/Browser Forums specify the practice. They also specify that DNS names in the CN are deprecated (but not prohibited). If you put a DNS name in the CN, then it must be included in the SAN under the CA/B policies. So you can't avoid using the Subject Alternate Name.

If you don't do put DNS names in the SAN, then the certificate will fail to validate under a browser and other user agents which follow the CA/Browser Forum guidelines.

Related: browsers follow the CA/Browser Forum policies; and not the IETF policies. That's one of the reasons a certificate created with OpenSSL (which generally follows the IETF) sometimes does not validate under a browser (browsers follow the CA/B). They are different standards, they have different issuing policies and different validation requirements.

Create a self signed certificate (notice the addition of -x509 option):
```bash
openssl req -config example-com.conf -new -x509 -sha256 -newkey rsa:2048 -nodes \
    -keyout example-com.key.pem -days 365 -out example-com.cert.pem
```
Create a signing request (notice the lack of -x509 option):
```bash
openssl req -config example-com.conf -new -sha256 -newkey rsa:2048 -nodes \
    -keyout example-com.key.pem -days 365 -out example-com.req.pem
```
Print a self-signe certificate:
```bash
openssl x509 -in example-com.cert.pem -text -noout
```
Print a signing request:
```bash
openssl req -in example-com.req.pem -text -noout
```
Configuration file (passed via -config option)
```ini
[ req ]
default_bits        = 2048
default_keyfile     = server-key.pem
distinguished_name  = subject
req_extensions      = req_ext
x509_extensions     = x509_ext
string_mask         = utf8only

# The Subject DN can be formed using X501 or RFC 4514 (see RFC 4519 for a description).
#   Its sort of a mashup. For example, RFC 4514 does not provide emailAddress.
[ subject ]
countryName         = Country Name (2 letter code)
countryName_default     = US

stateOrProvinceName     = State or Province Name (full name)
stateOrProvinceName_default = NY

localityName            = Locality Name (eg, city)
localityName_default        = New York

organizationName         = Organization Name (eg, company)
organizationName_default    = Example, LLC

# Use a friendly name here because it's presented to the user. The server's DNS
#   names are placed in Subject Alternate Names. Plus, DNS names here is deprecated
#   by both IETF and CA/Browser Forums. If you place a DNS name here, then you
#   must include the DNS name in the SAN too (otherwise, Chrome and others that
#   strictly follow the CA/Browser Baseline Requirements will fail).
commonName          = Common Name (e.g. server FQDN or YOUR name)
commonName_default      = Example Company

emailAddress            = Email Address
emailAddress_default        = test@example.com

# Section x509_ext is used when generating a self-signed certificate. I.e., openssl req -x509 ...
[ x509_ext ]

subjectKeyIdentifier        = hash
authorityKeyIdentifier    = keyid,issuer

# You only need digitalSignature below. *If* you don't allow
#   RSA Key transport (i.e., you use ephemeral cipher suites), then
#   omit keyEncipherment because that's key transport.
basicConstraints        = CA:FALSE
keyUsage            = digitalSignature, keyEncipherment
subjectAltName          = @alternate_names
nsComment           = "OpenSSL Generated Certificate"

# RFC 5280, Section 4.2.1.12 makes EKU optional
#   CA/Browser Baseline Requirements, Appendix (B)(3)(G) makes me confused
#   In either case, you probably only need serverAuth.
# extendedKeyUsage    = serverAuth, clientAuth

# Section req_ext is used when generating a certificate signing request. I.e., openssl req ...
[ req_ext ]

subjectKeyIdentifier        = hash

basicConstraints        = CA:FALSE
keyUsage            = digitalSignature, keyEncipherment
subjectAltName          = @alternate_names
nsComment           = "OpenSSL Generated Certificate"

# RFC 5280, Section 4.2.1.12 makes EKU optional
#   CA/Browser Baseline Requirements, Appendix (B)(3)(G) makes me confused
#   In either case, you probably only need serverAuth.
# extendedKeyUsage    = serverAuth, clientAuth

[ alternate_names ]

DNS.1       = example.com
DNS.2       = www.example.com
DNS.3       = mail.example.com
DNS.4       = ftp.example.com

# Add these if you need them. But usually you don't want them or
#   need them in production. You may need them for development.
# DNS.5       = localhost
# DNS.6       = localhost.localdomain
# DNS.7       = 127.0.0.1

# IPv6 localhost
# DNS.8     = ::1
```
You may need to do the following for Chrome. Otherwise Chrome may complain a Common Name is invalid (ERR_CERT_COMMON_NAME_INVALID). I'm not sure what the relationship is between an IP address in the SAN and a CN in this instance.
```ini
# IPv4 localhost
# IP.1       = 127.0.0.1

# IPv6 localhost
# IP.2     = ::1
```
There are other rules concerning the handling of DNS names in X.509/PKIX certificates. Refer to these documents for the rules:

RFC 5280, Internet X.509 Public Key Infrastructure Certificate and Certificate Revocation List (CRL) Profile
RFC 6125, Representation and Verification of Domain-Based Application Service Identity within Internet Public Key Infrastructure Using X.509 (PKIX) Certificates in the Context of Transport Layer Security (TLS)
RFC 6797, Appendix A, HTTP Strict Transport Security (HSTS)
RFC 7469, Public Key Pinning Extension for HTTP
CA/Browser Forum Baseline Requirements
CA/Browser Forum Extended Validation Guidelines
RFC 6797 and RFC 7469 are listed, because they are more restrictive than the other RFCs and CA/B documents. RFCs 6797 and 7469 do not allow an IP address, either.
