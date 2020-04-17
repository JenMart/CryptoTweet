from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from os import path
import random
from app.db_mgmt import DatabaseManager
import re

# print(original_message)
# # Max tweet length will be 264 characters.
# # Messages cannot be more than 190 characters.
# # 190 characters or less makes encryption 256 or less characters.
# # One character higher and message breaks
# # Special characters are allowed.
# message = b'Encrypted message test thing. '
#####################################################

class main:

    def __init__(self):
        self.db_mgmt = DatabaseManager()

    def generate_key(self):
        #
        # Generates single pair of public & private keys if one or neither is not present.
        # Future builds will generate keys for every user.
        #

        if path.isfile('public_key.pem') == False or path.isfile('private_key.pem') == False:
        # Generating Keys
            private_key = rsa.generate_private_key(
                    public_exponent=65537,
                    key_size=2048,
                    backend=default_backend()
                )
            public_key = private_key.public_key()

            # Storing the keys
            pem = private_key.private_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PrivateFormat.PKCS8,
                    encryption_algorithm=serialization.NoEncryption()
                )
            with open('private_key.pem', 'wb') as f:
                f.write(pem)

            pem = public_key.public_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PublicFormat.SubjectPublicKeyInfo
                )
            with open('public_key.pem', 'wb') as f:
                f.write(pem)

        if path.isfile("fernet_key.pem") == False:
            key = Fernet.generate_key()
            with open('fernet_key.pem', 'wb') as x:
                x.write(key)
        return

    def glyph_binder_f(self, message):
        with open("fernet_key.pem", "rb") as key_file:
            key = key_file.readline()
        f = Fernet(key)

        if len(message) != 120:
            whitespaces = 120 - len(message)
            message = ' ' * whitespaces + message

        encrypted = f.encrypt(message)
        return encrypted

    def glyph_unbinder_f(self, message):
        try:
            with open("fernet_key.pem", "rb") as key_file:
                key = key_file.readline()
            f = Fernet(key)
            print(message)
            decrypted = f.decrypt(message)
            return decrypted.lstrip() # added whitespace is removed here.
        except Exception as e:
            print("errorrr")
            return e

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
        self.generate_key() # Always checks to see if keys exist.

        message = "Unknown"
        check_user = self.db_mgmt.checkUser(screenName)
        if check_user: # If account does not exist.
            if "forge" in txt and "glyph" in txt :
                private_glyph = self.forge_gylph()
                public_glyph = self.forge_gylph()
                self.db_mgmt.addUser(screenName, private_glyph, public_glyph)
                message = "Your Glyphs have been forged. Unbinding Glyph: {} Binding Glyph: {}".format(private_glyph, public_glyph)
            elif "unbind:" in txt or "bind:" in txt:
                message = "You you do not possess a glyph. Please type 'forge glyphs' to create a glyph"
            else:
                message = "You have selected an invalid option. Please type 'forge glyphs' to create a glyph"

        else: # If account exists.
            if "forge" in txt and "glyph" in txt: # Creates glyphs for new users. Current uses cannot change glyphs.
                message = "You cannot forge more Glyphs"
            elif "unbind:" in txt: # Allows user to decrypt message.
                glyph_check = self.db_mgmt.unbindGlyph(screenName)
                if glyph_check in txt:
                    # txt = txt.replace("bind:"+glyph_check,"")
                    # xx = "gAAAAABejRPs-iOxTW2dxzz2p5pjMZFyr3RJAzIkltl882w0t46SJ-zabwQR8B08BDHDsOeqxpn-XvcS2DNGEMwmflekQbDOeA==".encode('utf-8')
                    # message = self.glyph_unbinder_f(xx)
                    replacer = re.compile("unbind:", re.IGNORECASE)
                    txt = replacer.sub("", txt,1)
                    message = self.glyph_unbinder_f(txt.replace(glyph_check,"").encode('utf-8').lstrip())
                else:
                    message = "You are using the wrong Glyph or do not possess one"
            elif "bind:" in txt: # Allows user to encrypt message.
                glyph_check = self.db_mgmt.bindGlyph(screenName)
                print(glyph_check[0])
                if glyph_check in txt:
                    if len(txt) > 120: # Will not allow a message over 120 characters
                        message = "You message must be 120 characters or smaller"
                    else:
                        whitespaces = 120 - len(txt) # Any message below 120 characters will have padded w/ whitespace.
                        txt = " " * whitespaces + txt
                        replacer = re.compile("bind:", re.IGNORECASE)
                        txt = replacer.sub("", txt,1)
                        message = self.glyph_binder_f(txt.replace(glyph_check,"",1).replace(" ","").encode('utf-8'))
                else:
                    message = "You are using the wrong Glyph"
            else:
                message = "You have selected an invalid option."

        return message

##############################UNUSED##############################

    def glyph_binder(self, message): # Uses public key
        #
        # Encrypts messages using public key
        #
        # message = message.encode('utf-8')
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
        # message = message.encode('utf-8')
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
            return original_message.lstrip() # added whitespace is removed here.
        except:
            return False

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



