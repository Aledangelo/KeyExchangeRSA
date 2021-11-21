from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes
import datetime

# Genero le chiavi
private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
public_key = private_key.public_key()

# Salvo la chiave sul disco
with open('keyCA.pem', "wb") as key:
    key.write(private_key.private_bytes(encoding=serialization.Encoding.PEM,
                                        format=serialization.PrivateFormat.TraditionalOpenSSL,
                                        encryption_algorithm=serialization.BestAvailableEncryption(b"passCA")))

# Genero un certificato auto-firmato
subject = issuer = x509.Name([
    x509.NameAttribute(NameOID.COUNTRY_NAME, u"IT"),
    x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, u"Napoli"),
    x509.NameAttribute(NameOID.LOCALITY_NAME, u"Napoli"),
    x509.NameAttribute(NameOID.ORGANIZATION_NAME, u"Certification Authority"),
    x509.NameAttribute(NameOID.COMMON_NAME, u"certificationauthority.com")
])

certificate = (
    x509.CertificateBuilder().subject_name(subject).issuer_name(issuer).public_key(public_key).serial_number(x509.random_serial_number())
        .not_valid_before(datetime.datetime.utcnow()).not_valid_after(datetime.datetime.utcnow() + datetime.timedelta(days=15))
        .add_extension(x509.SubjectAlternativeName([x509.DNSName(u"localhost")]), critical=False)
        .add_extension(x509.BasicConstraints(ca=True, path_length=None), critical=True).sign(private_key, hashes.SHA256())
)

with open("certificateCA.pem", "wb") as cert:
    cert.write(certificate.public_bytes(encoding=serialization.Encoding.PEM))