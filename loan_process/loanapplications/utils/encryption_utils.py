"""
Utility functions for encrypting and decrypting files.

This module provides functions to encrypt files before they are stored
and decrypt them when they are accessed.
"""

import os
import tempfile
from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage, FileSystemStorage
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import logging

logger = logging.getLogger(__name__)

# Use Django's SECRET_KEY to derive an encryption key
def get_encryption_key():
    """
    Derive an encryption key from Django's SECRET_KEY.

    Returns:
        bytes: A 32-byte key suitable for Fernet encryption.
    """
    # Use PBKDF2 to derive a key from Django's SECRET_KEY
    salt = b'django_file_encryption'  # A constant salt
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
    )
    key = base64.urlsafe_b64encode(kdf.derive(settings.SECRET_KEY.encode()))
    return key

def encrypt_file(file):
    """
    Encrypt a file using Fernet symmetric encryption.

    Args:
        file: A Django File object to encrypt.

    Returns:
        django.core.files.File: An encrypted file object.
    """
    # Read the file content
    file_content = file.read()

    # If the file is empty, return it as is
    if not file_content:
        file.seek(0)
        return file

    # Get the encryption key
    key = get_encryption_key()

    # Create a Fernet cipher
    cipher = Fernet(key)

    # Encrypt the file content
    encrypted_content = cipher.encrypt(file_content)

    # Create a new file with the encrypted content
    encrypted_file = ContentFile(encrypted_content)
    encrypted_file.name = file.name

    return encrypted_file

def decrypt_file(file):
    """
    Decrypt a file that was encrypted using encrypt_file.

    Args:
        file: A Django File object containing encrypted content.

    Returns:
        django.core.files.File: A decrypted file object.
    """
    # Read the encrypted content
    encrypted_content = file.read()

    # If the file is empty, return it as is
    if not encrypted_content:
        file.seek(0)
        return file

    # Get the encryption key
    key = get_encryption_key()

    # Create a Fernet cipher
    cipher = Fernet(key)

    try:
        # Decrypt the content
        decrypted_content = cipher.decrypt(encrypted_content)

        # Create a new file with the decrypted content
        decrypted_file = ContentFile(decrypted_content)
        decrypted_file.name = file.name

        return decrypted_file
    except Exception as e:
        # If decryption fails, the file might not be encrypted
        # Return the original file
        file.seek(0)
        return file

def save_encrypted_file(file, path):
    """
    Encrypt and save a file to the specified path.

    Args:
        file: A Django File object to encrypt and save.
        path: The path where the encrypted file should be saved.

    Returns:
        str: The path where the encrypted file was saved.
    """
    # Encrypt the file
    encrypted_file = encrypt_file(file)

    # Save the encrypted file
    path = default_storage.save(path, encrypted_file)

    return path

def read_decrypted_file(path):
    """
    Read and decrypt a file from the specified path.

    Args:
        path: The path to the encrypted file.

    Returns:
        django.core.files.File: A decrypted file object.
    """
    # Open the encrypted file
    with default_storage.open(path) as f:
        # Decrypt the file
        decrypted_file = decrypt_file(f)

    return decrypted_file


class EncryptedFileStorage(FileSystemStorage):
    """
    A custom storage class that automatically encrypts files when they're saved
    and decrypts them when they're accessed.
    """

    def _save(self, name, content):
        """
        Encrypt the file before saving it.

        Args:
            name: The name of the file.
            content: The file content to save.

        Returns:
            str: The name of the saved file.
        """
        # Log that we're encrypting a file
        logger.info(f"Encrypting file: {name}")

        try:
            # Encrypt the file
            encrypted_content = encrypt_file(content)

            # Save the encrypted file using the parent class's _save method
            return super()._save(name, encrypted_content)
        except Exception as e:
            logger.error(f"Error encrypting file {name}: {str(e)}")
            # If encryption fails, save the file unencrypted
            return super()._save(name, content)

    def _open(self, name, mode='rb'):
        """
        Decrypt the file when it's opened.

        Args:
            name: The name of the file to open.
            mode: The mode to open the file in.

        Returns:
            django.core.files.File: The decrypted file.
        """
        # Log that we're decrypting a file
        logger.info(f"Decrypting file: {name}")

        try:
            # Open the file using the parent class's _open method
            encrypted_file = super()._open(name, mode)

            # Decrypt the file
            decrypted_file = decrypt_file(encrypted_file)

            return decrypted_file
        except Exception as e:
            logger.error(f"Error decrypting file {name}: {str(e)}")
            # If decryption fails, return the file as is
            return super()._open(name, mode)
