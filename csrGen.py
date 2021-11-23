from cryptography import x509
from cryptography.x509.oid import NameOID
from OpenSSL import crypto
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.backends import default_backend


subject = x509.Name([
    x509.NameAttribute(NameOID.COUNTRY_NAME, u"US"),
    x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, u"Server"),
    x509.NameAttribute(NameOID.LOCALITY_NAME, u"Server"),
    x509.NameAttribute(NameOID.ORGANIZATION_NAME, u"Server"),
    x509.NameAttribute(NameOID.COMMON_NAME, u"server.com")
])

with open('key.pem', "rb") as f:
    privateKey = serialization.load_pem_private_key(f.read(), password=b"passphrase")

builder = x509.CertificateSigningRequestBuilder().subject_name(subject)

csr = builder.sign(privateKey, hashes.SHA256(), default_backend())

with open('csr.pem', 'wb') as csrfile:
    csrfile.write(csr.public_bytes(serialization.Encoding.PEM))


