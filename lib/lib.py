import requests
import sys


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
                print(f"Update available: {latestVer} (Current version: {currentVer})\nYou can download the latest version from: https://github.com/qing762/mega-auto-signup/releases/latest\n")
            else:
                print(f"You are running the latest version: {currentVer}\n")
                pass
        except Exception as e:
            print(f"An error occurred: {e}")
            pass


if __name__ == "__main__":
    print("This is a library file. Please run main.py instead.")
