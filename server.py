from socket import socket
from cryptography import x509
from cryptography.hazmat.backends import default_backend
from os import urandom
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.padding import PKCS7
from OpenSSL import crypto
from getpass import getpass

ipaddress = 'ipServer'
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


def unpad(message):
    unpadder = PKCS7(algorithms.AES.block_size).unpadder()

    unpaddedMessage = unpadder.update(message) + unpadder.finalize()

    return unpaddedMessage


def recvAndDecrypt(socket, key):
    iv = socket.recv(16)
    msg = socket.recv(2018)

    cipher = Cipher(algorithms.AES(key), modes.CBC(iv))

    decryptor = cipher.decryptor()
    text = decryptor.update(msg) + decryptor.finalize()
    return unpad(text)


def main():
    pswd = getpass('Enter pass phrase for keyStore: ')

    sock = socket()
    sock.bind((ipaddress, port))
    sock.listen()
    print(f'\nServer listening on port {port}...')

    try:
        keep_alive = True
        while keep_alive:

            (clientConn, clientAdd) = sock.accept()

            certificate = clientConn.recv(1220)
            certs = x509.load_pem_x509_certificate(certificate, default_backend())

            try:
                verifica(certificate)
                print('\nCertificate is secure')
            except:
                print('\nCertificate is not secure')
                sock.close()
                quit(0)

            with open("keystore.p12", "rb") as f:
                key, cert = extract_certificate_and_key(f.read(), password=pswd.encode())
            clientConn.send(cert)

            sessionKey = urandom(16)
            cypher_msg = certs.public_key().encrypt(plaintext=sessionKey,
                                                    padding=padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()),
                                                                         algorithm=hashes.SHA256(), label=None))
            clientConn.send(cypher_msg)
            privateKey = serialization.load_pem_private_key(key, password=None)

            try:
                signature = privateKey.sign(cypher_msg, padding=padding.PSS(mgf=padding.MGF1(algorithm=hashes.SHA256()),
                                                                            salt_length=padding.PSS.MAX_LENGTH),
                                            algorithm=hashes.SHA256())
                clientConn.send(signature)
            except Exception as e:
                print(e)

            print(f'\n{clientAdd[0]} is connected')

            print(recvAndDecrypt(socket=clientConn, key=sessionKey))

    except KeyboardInterrupt:
        print('Quit')
        sock.close()
        quit(1)


if __name__ == '__main__':
    main()
