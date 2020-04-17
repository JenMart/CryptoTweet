import sqlite3
import os


class DatabaseManager:
    #
    #   Should call self.setup() if the DB isn't found in the same folder as g_manager.py.
    #   To rebuild the DB, delete the file and run g_manager.py again.
    #
    def __init__(self):
        if not os.path.isfile('TheForge.sqlite'):
            self.setup()

    def setup(self):
        cur = sqlite3.connect('TheForge.sqlite')
        u = cur.cursor()

        print("Creating database")
        users = """ CREATE TABLE USERS (
                ID INTEGER PRIMARY KEY AUTOINCREMENT,
                USERNAME VARCHAR(255) NOT NULL,
                PRIVATEGLYPH VARCHAR(255) NOT NULL,
                PUBLICGLYPH VARCHAR(255) NOT NULL
                )"""
        u.execute(users)
        cur.commit()
        cur.close()

    def addUser(self, name, privateGlyph, publicGlyph):
        cursor = sqlite3.connect('TheForge.sqlite')
        c = cursor.cursor()
        # print("""Adding user data to Database""")
        c.execute("INSERT INTO USERS(USERNAME, PRIVATEGLYPH, PUBLICGLYPH) VALUES (?, ?, ?)", (name, privateGlyph, publicGlyph))
        cursor.commit()
        cursor.close()
        return

    def bindGlyph(self, name):
        cursor = sqlite3.connect('TheForge.sqlite')
        c = cursor.cursor()
        c.execute("""SELECT PUBLICGLYPH FROM USERS WHERE USERNAME = ? """,(name,))
        public_glyph = c.fetchall()
        cursor.commit()
        cursor.close()
        public_glyph = public_glyph[0]
        # print(public_glyph[0])
        return public_glyph[0]

    def unbindGlyph(self, name):
        cursor = sqlite3.connect('TheForge.sqlite')
        c = cursor.cursor()
        c.execute("""SELECT PRIVATEGLYPH FROM USERS WHERE USERNAME = ? """,(name,))
        private_glyph = c.fetchall()
        cursor.commit()
        cursor.close()
        private_glyph = private_glyph[0]
        return private_glyph[0]

    def checkUser(self, name):
        cursor = sqlite3.connect('TheForge.sqlite')
        c = cursor.cursor()
        c.execute("""SELECT * FROM USERS WHERE USERNAME = ? """, (name,))
        tweets = c.fetchall()
        cursor.commit()
        cursor.close()
        # print(tweets)
        if len(tweets) == 0:
            return True
        else:
            return False

