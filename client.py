from socket import socket
from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.padding import PKCS7
from OpenSSL import crypto
from getpass import getpass
from os import urandom

host = 'ipClient'
port = 1234


def verifica(serverCert):
    server_cert = crypto.load_certificate(crypto.FILETYPE_PEM, serverCert)

    root_cert = crypto.load_certificate(crypto.FILETYPE_PEM, open(r'certificateCA.pem').read())

    store = crypto.X509Store()
    store.add_cert(root_cert)

    ctx = crypto.X509StoreContext(store, server_cert)
    ctx.verify_certificate()


def extract_certificate_and_key(pfx, password):
    pfx = crypto.load_pkcs12(pfx, password)

    key = crypto.dump_privatekey(crypto.FILETYPE_PEM, pfx.get_privatekey())

    cert = crypto.dump_certificate(crypto.FILETYPE_PEM, pfx.get_certificate())
    return key, cert


def pad(message):
    padder = PKCS7(algorithms.AES.block_size).padder()

    paddedData = padder.update(message.encode()) + padder.finalize()

    return paddedData


def cryptAndSend(socket, key, message):
    paddedMessage = pad(message=message)

    iv = urandom(16)

    chiper = Cipher(algorithms.AES(key), modes.CBC(iv))

    encryptor = chiper.encryptor()

    cypherText = encryptor.update(paddedMessage) + encryptor.finalize()

    socket.send(iv)
    socket.send(cypherText)


def main():
    pswd = getpass('Enter pass phrase for key.pem: ')

    sock = socket()
    sock.connect((host, port))
    print(f'\nClient conneted on port {port}')
    try:

        with open("keystoreCL.p12", "rb") as f:
            key, cert = extract_certificate_and_key(f.read(), password=pswd.encode())

        sock.send(cert)
        privateKey = serialization.load_pem_private_key(key, password=None)

        try:
            signature = privateKey.sign(cert, padding=padding.PSS(mgf=padding.MGF1(algorithm=hashes.SHA256()),
                                                                  salt_length=padding.PSS.MAX_LENGTH),
                                        algorithm=hashes.SHA256())
        except Exception as e:
            print(e)
            sock.close()
            quit(1)

        sock.send(signature)
        certificate = sock.recv(1220)
        signature2 = sock.recv(1220)
        certs = x509.load_pem_x509_certificate(certificate, default_backend())
        try:
            (certs.public_key().verify(signature=signature2, data=certificate, padding=padding.
                                       PSS(mgf=padding.MGF1(algorithm=hashes.SHA256()),
                                           salt_length=padding.PSS.MAX_LENGTH),
                                       algorithm=hashes.SHA256()))
        except:
            print('Messaggio corrotto')
            sock.close()
            quit(0)

        try:
            verifica(certificate)
            print('\nCertificate is secure')
        except Exception as e:
            print('\nCertificate is not secure')
            print(f'\n {e}')
            sock.close()
            quit(0)

        cypherMsg = sock.recv(256)
        signature = sock.recv(256)

        try:
            (certs.public_key().verify(signature=signature, data=cypherMsg, padding=padding.
                                       PSS(mgf=padding.MGF1(algorithm=hashes.SHA256()),
                                           salt_length=padding.PSS.MAX_LENGTH),
                                       algorithm=hashes.SHA256()))
        except:
            print('Messaggio corrotto')
            sock.close()
            quit(0)

        sessionKey = (
            privateKey.decrypt(ciphertext=cypherMsg, padding=padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()),
                                                                          algorithm=hashes.SHA256(), label=None)))

        text = input('Insert Secret Message: ')
        cryptAndSend(socket=sock, key=sessionKey, message=text)

    finally:
        sock.close()


if __name__ == '__main__':
    main()
