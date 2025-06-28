import requests
import sys
import time
import random
from pymailtm import MailTm, Account
from pymailtm.pymailtm import generate_username


class Main:
    async def checkPassword(self, password):
        if len(password) >= 8:
            return "\nPassword is valid."
        else:
            if len(password) < 8:
                return "\nPassword does not meet the requirements. Please use at least 8 characters."

    async def checkUpdate(self):
        try:
            resp = requests.get(
                "https://api.github.com/repos/qing762/mega-auto-signup/releases/latest"
            )
            latestVer = resp.json()["tag_name"]

            if getattr(sys, 'frozen', False):
                import version
                currentVer = version.__version__
            else:
                with open("version.txt", "r") as file:
                    currentVer = file.read().strip()

            if currentVer < latestVer:
                print(f"Update available: {latestVer} (Current version: {currentVer})\nYou can download the latest version from: https://github.com/qing762/mega-auto-signup/releases/latest")
            else:
                print(f"You are running the latest version: {currentVer}")
                pass
        except Exception as e:
            print(f"An error occurred: {e}")
            pass

    def testProxy(self, proxy):
        try:
            response = requests.get("http://www.google.com", proxies={"http": proxy, "https": proxy}, timeout=5)
            return True, response.status_code
        except Exception:
            return False, "Proxy test failed! Please ensure that the proxy is working correctly. Skipping proxy usage..."

    def generateEmail(self, password="Qing762.chy"):
        if not hasattr(self, 'mailtm'):
            self.mailtm = MailTm()
        domainList = self.mailtm._get_domains_list()
        domain = random.choice(domainList)
        username = generate_username(1)[0].lower()
        address = f"{username}@{domain}"
        while True:
            try:
                emailID = requests.post("https://api.mail.tm/accounts", json={"address": address, "password": password})
                if emailID.status_code == 201 and "id" in emailID.json():
                    break
                else:
                    print(f"Failed to create email with address {address}. Sleeping for 5 seconds then will retry...")
                    time.sleep(5)
                    username = generate_username(1)[0].lower()
                    address = f"{username}@{domain}"
            except Exception as e:
                print(f"Error creating email: {e}. Sleeping for 5 seconds then will retry...")
                time.sleep(5)
                username = generate_username(1)[0].lower()
                address = f"{username}@{domain}"
        token = requests.post(
            "https://api.mail.tm/token",
            json={"address": address, "password": password}
        ).json()["token"]
        return address, password, token, emailID

    def fetchVerification(self, address=None, password=None, emailID=None):
        if not address or not password or not emailID:
            raise ValueError("Address, password, and emailID must be provided.")
        if not hasattr(self, 'mailtm'):
            self.mailtm = MailTm()
        if not hasattr(self, 'account'):
            self.account = Account(emailID, address, password)
        messages = self.account.get_messages()
        return messages


if __name__ == "__main__":
    print("This is a library file. Please run main.py instead.")
