from datetime import datetime
from time import gmtime

from app.Main import main
from app.db_mgmt import DatabaseManager


class notMain:
    def __init__(self):
        self.db_mgmt = DatabaseManager()
        self.Main = main()
        userNameFake = "fakeAccount1"
        createDateFake = gmtime()
        statIDFake ="1155645641793687552"
        inptFake = ""
        ##########################################
        DT = datetime.now().strftime("%H:%M:%S.%f")
        print("Time Stamp: " + DT)
        while inptFake.lower() != "exit":
            inptFake = input("Enter text here \n")
            try:
                exFake = self.Main.handle_choices(inptFake, userNameFake, createDateFake, statIDFake)
                self.fakePrinter(userNameFake, exFake, statIDFake)
            except Exception as e:
                print("Error")
                print(e)
        print("Offline testing has concluded")


# gAAAAABejRPs-iOxTW2dxzz2p5pjMZFyr3RJAzIkltl882w0t46SJ-zabwQR8B08BDHDsOeqxpn-XvcS2DNGEMwmflekQbDOeA==
# Private: #)|^${% Public: ](=**#]
# ('](=**#]',)
    def fakePrinter(self, user, text, statID):
        # message = b"".join(["@" + user + " " + text])
        # print("Creating fake tweet: \n" + message + "\n")
        # print("character count: " + str(len(message)))
        print(text)
        if len(text) >= 280:
            print("*******")
            print("WARNING: message at or exceeded character limit")
            print("*******")
        ##########################################
        DT = datetime.now().strftime("%H:%M:%S.%f")
        print("Time Stamp: " + DT)
        #########################################
        return



if __name__ == '__main__':
    notMain()
