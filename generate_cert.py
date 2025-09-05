from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import rsa
import datetime

password = b"mysecretpassword"  # סיסמה למפתח הפרטי

# יצירת מפתח פרטי
key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=2048,
)

# שמירת המפתח הפרטי ל-key.pem עם סיסמה
with open("key.pem", "wb") as f:
    f.write(key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,  # PKCS#1
        encryption_algorithm=serialization.BestAvailableEncryption(password)
    ))

# פרטים לתעודה
subject = issuer = x509.Name([
    x509.NameAttribute(NameOID.COUNTRY_NAME, u"IL"),
    x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, u"Tel Aviv"),
    x509.NameAttribute(NameOID.LOCALITY_NAME, u"Tel Aviv"),
    x509.NameAttribute(NameOID.ORGANIZATION_NAME, u"MyOrg"),
    x509.NameAttribute(NameOID.COMMON_NAME, u"localhost"),
])

# יצירת תעודת X.509
cert = x509.CertificateBuilder().subject_name(
    subject
).issuer_name(
    issuer
).public_key(
    key.public_key()
).serial_number(
    x509.random_serial_number()
).not_valid_before(
    datetime.datetime.utcnow()
).not_valid_after(
    datetime.datetime.utcnow() + datetime.timedelta(days=365)
).sign(key, hashes.SHA256())

# שמירת התעודה ל-cert.pem
with open("cert.pem", "wb") as f:
    f.write(cert.public_bytes(serialization.Encoding.PEM))

print("key.pem ו-cert.pem נוצרו בהצלחה עם סיסמה!")
