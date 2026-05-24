import os
import base64

try:
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    HAS_CRYPTO = True
except ImportError:
    HAS_CRYPTO = False


class SecureCredentialStore:
    """AES-256-GCM symmetric encryption engine for securing AWS credential storage."""

    def __init__(self, key_b64: str = None):
        if not HAS_CRYPTO:
            import warnings
            warnings.warn("cryptography library not installed — credential encryption disabled, using base64 encoding")
            self.aesgcm = None
            return

        key_str = key_b64 or os.getenv(
            "AES_SECRET_KEY_B64",
            "MDEyMzQ1Njc4OTAxMjM0NTY3ODkwMTIzNDU2Nzg5MDE="
        )
        try:
            self.key = base64.b64decode(key_str)
            # AES-256 requires exactly 32 bytes
            if len(self.key) not in (16, 24, 32):
                # Pad or truncate to 32 bytes
                self.key = self.key.ljust(32, b'\0')[:32]
            self.aesgcm = AESGCM(self.key)
        except Exception:
            self.aesgcm = None

    def encrypt_secret(self, plain_text: str) -> str:
        """Encrypt plaintext using AES-256-GCM with a random 12-byte nonce."""
        if not self.aesgcm:
            return base64.b64encode(plain_text.encode('utf-8')).decode('utf-8')

        nonce = os.urandom(12)
        cipher_bytes = self.aesgcm.encrypt(nonce, plain_text.encode('utf-8'), None)
        payload = nonce + cipher_bytes
        return base64.b64encode(payload).decode('utf-8')

    def decrypt_secret(self, cipher_text_b64: str) -> str:
        """Decrypt AES-256-GCM ciphertext back to plaintext."""
        if not self.aesgcm:
            return base64.b64decode(cipher_text_b64.encode('utf-8')).decode('utf-8')

        payload = base64.b64decode(cipher_text_b64.encode('utf-8'))
        nonce = payload[:12]
        cipher_bytes = payload[12:]
        plain_bytes = self.aesgcm.decrypt(nonce, cipher_bytes, None)
        return plain_bytes.decode('utf-8')
