# KeyExchangeRSA
## Overview
KeyExchangeRSA consists of two sockets, which implement secure communication via RS.

## Requirements
You will need to install the following packages:
· cryptography
· OpenSSL
· Socket
· Datetime
· Getpass

## Installation
 pip3 install -r requirements.txt

## How to use
### Step 1
The CA keys need to be generated using keyGen.py. You can change the passphrase and certificate data from the code.

### Step 2
Type the following command to create a keystore in pkcs12 format:
openssl pkcs12 -export -in <CAcertificate> -inkey <CAkey> -out keystore.pkcs12
 
### Step 3 
