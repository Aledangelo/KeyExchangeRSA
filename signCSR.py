import datetime
from cryptography import x509
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization


def sign_csr(csr, ca_public_key, ca_private_key, filename):

    with open(csr, "rb") as c:
        csr = c.read()

    with open(ca_private_key, "rb") as pr:
        ca_private_key = pr.read()

    with open(ca_public_key, "rb") as pb:
        ca_public_key = pb.read()

    valid_from = datetime.datetime(year=2021, month=11, day=15).utcnow()
    valid_until = valid_from + datetime.timedelta(days=365)
    csr = x509.load_pem_x509_csr(csr, backend=default_backend())
    ca_private_key = serialization.load_pem_private_key(ca_private_key, password=b"passCA", backend=default_backend())
    ca_public_key = x509.load_pem_x509_certificate(ca_public_key, backend=default_backend())

    builder = (
        x509.CertificateBuilder().subject_name(csr.subject).issuer_name(ca_public_key.subject).public_key(csr.public_key())
            .serial_number(x509.random_serial_number()).not_valid_before(valid_from).not_valid_after(valid_until)
    )

    for extension in csr.extensions:
        builder = builder.add_extension(extension.value, extension.critical)

    public_key = builder.sign(private_key=ca_private_key, algorithm=hashes.SHA256(), backend=default_backend())

    with open(filename, "wb") as keyfile:
        keyfile.write(public_key.public_bytes(serialization.Encoding.PEM))


