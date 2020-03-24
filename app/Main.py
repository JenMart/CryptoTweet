from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from os import path
from cryptography.fernet import Fernet
import random
from app.db_mgmt import DatabaseManager

class main:

    def __init__(self):
        self.db_mgmt = DatabaseManager()

    def generate_key(self):
        #
        # Generates single pair of public & private keys if one or neither is not present.
        # Future builds will generate keys for every user.
        #
        if path.isfile('public_key.pem') == False or path.isfile('private_key.pem') == False:
            print("generating public key")
            public_key = ""
            key = public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            )
            f = open('public_key.pem','wb')
            f.write(key)
            f.close()

            print("generating private key")
            private_key = ""
            key = private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            )
            f = open('private_key.pem','wb')
            f.write(key)
            f.close()
        else:
            print("Keys already exists")
        return


    def signature(self, message): # Uses private key
        #
        # Signs messages.
        # Note: Currently not in use for this build
        #
        try:
            with open("private_key.pem", "rb") as key_file:
                private_key = serialization.load_pem_private_key(
                    key_file.read(),
                    password=None,
                    backend=default_backend()
                )
            #####################################################
            signed = private_key.sign(
                message,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            return signed
        except Exception as e:
            return "Signature is invalid"

    def verify(self, message, signature): # Uses public key
        #
        # verifies signed messages.
        # Note: Currently not in use for this build.
        #
        with open("public_key.pem", "rb") as key_file:
            public_key = serialization.load_pem_public_key(
                key_file.read(),
                backend=default_backend()
            )
        #####################################################
        try:
            public_key.verify(
                signature,
                message,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            return "Signature is valid"
        except Exception as e:
            return "Signature is invalid"

    def glyph_binder(self, message): # Uses public key
        #
        # Encrypts messages using public key
        #
        try:
            with open("public_key.pem", "rb") as key_file:
                public_key = serialization.load_pem_public_key(
                    key_file.read(),
                    backend=default_backend()
                )
            #####################################################
            encrypted = public_key.encrypt(
                message,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )
            return encrypted
        except Exception as e:
            return "Signature is invalid"

    def glyph_unbinder(self, message): #Uses private key
        #
        # Uses private key to decrypt
        #
        with open("private_key.pem", "rb") as key_file:
            private_key = serialization.load_pem_private_key(
                key_file.read(),
                password=None,
                backend=default_backend()
            )
        #####################################################
        try:
            original_message = private_key.decrypt(
                message,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )
            return original_message
        except:
            return False

    def forge_gylph(self):
        #
        # Creates random passcode for users to encrypt and decrypt messages.
        # Passwords/ glyphs are tied to accounts, so attempting to use anyone elses will not work.
        # In the future, glyphs will be created using random params from users twitter account & encryption keys
        #
        symbols = ["!","@","#","$","%","^","&","*","(",")","[","]","{","}","-","_","=","+","/","|"]
        glyph = ""
        x = 0
        while x < 7:
            randy = random.randint(0, len(symbols)-1)
            glyph += symbols[randy]
            x += 1
        return glyph


    # 15 characters for decypt request... Glyphs would have to be less than 7 characters.
    # 89 characters for encrypt request
    def handle_choices(self, txt, screenName, date, statID):
        self.generate_key() # Always checks to see if keys are in existance.
        txt = txt.lower()
        message = "Unknown"
        check_user = self.db_mgmt.checkUser(screenName)
        if check_user: # If account does not exist.
            if "forge" in txt and "glyph" in txt :
                private_glyph = self.forge_gylph()
                public_glyph = self.forge_gylph()
                self.db_mgmt.addUser(screenName, private_glyph, public_glyph)
                message = "Your Glyphs have been forged. Private: {} Public: {}".format(private_glyph, public_glyph)
            elif "unbind:" in txt or "bind:" in txt:
                message = "You you do not possess a glyph. Please type 'forge glyphs' to create a glyph"

        else: # If account exists.
            if "forge glyphs" in txt: # Creates glyphs for new users. Current uses cannot change glyphs.
                message = "You cannot forge more Glyphs"
            elif "unbind:" in txt: # Allows user to decrypt message.
                glyph_check = self.db_mgmt.unbindGlyph(screenName)
                if glyph_check in txt:
                    txt = txt.replace("bind:"+glyph_check,"")
                    message = self.glyph_unbinder(txt)
                else:
                    message = "You are using the wrong Glyph or do not possess one"
            elif "bind:" in txt: # Allows user to encrypt message.
                glyph_check = self.db_mgmt.bindGlyph(screenName)
                if glyph_check in txt:
                    txt = txt.replace("bind:"+glyph_check,"")
                    message = self.glyph_binder(txt)
                else:
                    message = "You are using the wrong Glyph"

        return message







# # Max tweet length will be 264 characters.
# # Messages cannot be more than 190 characters.
# # 190 characters or less makes encryption 256 or less characters.
# # One character higher and message breaks
# # Special characters are allowed.
# message = b'Encrypted message test thing. '
#####################################################


