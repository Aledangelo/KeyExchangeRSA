# KeyExchangeRSA
## Overview
KeyExchangeRSA consists of two sockets, which implement secure communication via RS.

## Requirements
You will need to install the following packages:
* cryptography
* OpenSSL
* Socket
* Datetime
* Getpass

## Installation
* pip3 install -r requirements.txt

## How to use
### Step 1
* The CA keys need to be generated using keyGen.py. You can change the passphrase and certificate data from the code.

### Step 2
Type the following command to create a keystore in pkcs12 format:
* openssl pkcs12 -export -in <CAcertificate> -inkey <CAkey> -out keystore.pkcs12
 
### Step 3 
* Using keyGen.py you can create the proven key for the two sockets. Then with the script csrGen.py you create the request to submit to the CA.
* Using the function present in signCSR.py, and specifying the CA certificate appropriately, we will sign the server (or client) certificate.
 
### Step 4
The last step is to configure the two sockets, specifying the ip address and port of both the client.
