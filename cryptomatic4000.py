from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
import os
from facialVaultifier import verifier, capture_image, enroller
import cv2
import evaluator

# Base path anchored to this file's location
path = os.path.dirname(__file__)
userName = "john cena"


class PasswordFileEncryptor:
    def __init__(self, password):
        self.password = password.encode()

    def _derive_key(self, salt):
        """Derive an AES-256 encryption key from the password + salt."""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=480000,
        )
        return kdf.derive(self.password)

    def encrypt_file(self, input_path, output_path):
        """Encrypt a file with the password-derived key and write to output_path."""
        salt = os.urandom(16)
        key = self._derive_key(salt)

        with open(input_path, 'rb') as f:
            plaintext = f.read()

        cipher = AESGCM(key)
        nonce = os.urandom(12)
        ciphertext = cipher.encrypt(nonce, plaintext, None)

        # Layout: [16-byte salt][12-byte nonce][ciphertext]
        with open(output_path, 'wb') as f:
            f.write(salt + nonce + ciphertext)

        print(f"Encrypted: {input_path} -> {output_path}")

    def decrypt_file(self, input_path, output_path):
        """Decrypt a file that was encrypted with encrypt_file."""
        with open(input_path, 'rb') as f:
            encrypted_data = f.read()

        salt = encrypted_data[:16]
        nonce = encrypted_data[16:28]
        ciphertext = encrypted_data[28:]

        key = self._derive_key(salt)
        cipher = AESGCM(key)
        plaintext = cipher.decrypt(nonce, ciphertext, None)

        with open(output_path, 'wb') as f:
            f.write(plaintext)

        print(f"Decrypted: {input_path} -> {output_path}")


def enroll_vault(image, username):
    """Enroll a new biometric vault for username. Returns True on success."""
    the_key = evaluator.keyGiver(username)
    return enroller(image, the_key)


def verify_vault(image, username):
    """Verify the biometric vault for username. Returns secret key string or None."""
    the_key = evaluator.keyGiver(username)
    password = verifier(image, the_key)
    if password is not None:
        return str(password)
    return None


if __name__ == "__main__":
    mode = input("Enter mode (enroll/verify): ").strip().lower()
    if input("Is this a test? (y/n): ").strip().lower() == "y":
        path_test = input("Enter the test image file name: ")
        if not path_test:
            path_test = "athul.png"
        image = cv2.imread(path_test)
    else:
        image = capture_image()

    if mode in ["enroll", "e"]:
        enroll_vault(image, userName)
    else:
        password = verify_vault(image, userName)
        if password:
            encryptor = PasswordFileEncryptor(password)
            encOrDec = input("Encrypt or decrypt? (e/d): ").strip().lower()
            if encOrDec in ['e', 'encrypt']:
                encryptor.encrypt_file(
                    os.path.join(path, 'vacation.png'),
                    os.path.join(path, 'vacation.png.enc')
                )
                encryptor.encrypt_file(
                    os.path.join(path, 'family_video.mp4'),
                    os.path.join(path, 'family_video.mp4.enc')
                )
            else:
                encryptor.decrypt_file(
                    os.path.join(path, 'vacation.png.enc'),
                    os.path.join(path, 'vacation_restored.png')
                )
                encryptor.decrypt_file(
                    os.path.join(path, 'family_video.mp4.enc'),
                    os.path.join(path, 'family_video_restored.mp4')
                )
        else:
            print("Verification failed.")
