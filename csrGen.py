from cryptography import x509
from cryptography.x509.oid import NameOID
from OpenSSL import crypto
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.backends import default_backend


def extract_certificate_and_key(pfx, password):
    pfx = crypto.load_pkcs12(pfx, password)

    key = crypto.dump_privatekey(crypto.FILETYPE_PEM, pfx.get_privatekey())

    cert = crypto.dump_certificate(crypto.FILETYPE_PEM, pfx.get_certificate())
    return key, cert


subject = x509.Name([
    x509.NameAttribute(NameOID.COUNTRY_NAME, u"IT"),
    x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, u"Napoli"),
    x509.NameAttribute(NameOID.LOCALITY_NAME, u"Napoli"),
    x509.NameAttribute(NameOID.ORGANIZATION_NAME, u"Server"),
    x509.NameAttribute(NameOID.COMMON_NAME, u"server.com")
])

with open('serverKey.pem', "rb") as f:
    privateKey = serialization.load_pem_private_key(f.read(), password=b"serverPass")

builder = x509.CertificateSigningRequestBuilder().subject_name(subject)

csr = builder.sign(privateKey, hashes.SHA256(), default_backend())

with open('CSRserver.pem', 'wb') as csrfile:
    csrfile.write(csr.public_bytes(serialization.Encoding.PEM))


