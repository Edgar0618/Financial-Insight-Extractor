import hashlib

def hash_password(password):
    """Hash the password using SHA-256."""
    sha256 = hashlib.sha256()
    sha256.update(password.encode("utf-8"))
    return sha256.hexdigest()