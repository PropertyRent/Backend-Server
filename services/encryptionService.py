import os
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
from typing import Optional

class EncryptionService:
    def __init__(self):
        # Get encryption key from environment or generate one
        encryption_key = os.getenv("ENCRYPTION_KEY")
        if not encryption_key:
            # In production, this should be set as an environment variable
            # For development, we'll generate a key based on a password
            password = os.getenv("ENCRYPTION_PASSWORD", "property-rent-secure-key-2025").encode()
            salt = b'property_rent_salt_2025'  # In production, use a random salt
            
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
            )
            key = base64.urlsafe_b64encode(kdf.derive(password))
        else:
            key = encryption_key.encode()
        
        self.fernet = Fernet(key)
    
    def encrypt(self, data: str) -> Optional[str]:
        """Encrypt sensitive data"""
        if not data or data == "":
            return None
        try:
            encrypted_data = self.fernet.encrypt(data.encode())
            return base64.urlsafe_b64encode(encrypted_data).decode()
        except Exception as e:
            print(f"Encryption error: {e}")
            return data  # Return original data if encryption fails
    
    def decrypt(self, encrypted_data: str) -> Optional[str]:
        """Decrypt sensitive data"""
        if not encrypted_data or encrypted_data == "":
            return None
        try:
            decoded_data = base64.urlsafe_b64decode(encrypted_data.encode())
            decrypted_data = self.fernet.decrypt(decoded_data)
            return decrypted_data.decode()
        except Exception as e:
            print(f"Decryption error: {e}")
            return encrypted_data  # Return original data if decryption fails
    
    def encrypt_multiple(self, data_dict: dict, fields_to_encrypt: list) -> dict:
        """Encrypt multiple fields in a dictionary"""
        encrypted_dict = data_dict.copy()
        for field in fields_to_encrypt:
            if field in encrypted_dict and encrypted_dict[field]:
                encrypted_dict[field] = self.encrypt(str(encrypted_dict[field]))
        return encrypted_dict
    
    def decrypt_multiple(self, data_dict: dict, fields_to_decrypt: list) -> dict:
        """Decrypt multiple fields in a dictionary"""
        decrypted_dict = data_dict.copy()
        for field in fields_to_decrypt:
            if field in decrypted_dict and decrypted_dict[field]:
                decrypted_dict[field] = self.decrypt(decrypted_dict[field])
        return decrypted_dict

# Global encryption service instance
encryption_service = EncryptionService()

# List of sensitive fields that need encryption
SENSITIVE_FIELDS = [
    'social_security_number',
    'drivers_license_number', 
    'bank_name',
    'account_type',
    'routing_number',
    'account_number',
    'electronic_signature_name',
    'security_deposit_payment_method',
    'first_month_rent_payment_method'
]