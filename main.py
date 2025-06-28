import asyncio
import re
import warnings
import os
from datetime import datetime
from tqdm import TqdmExperimentalWarning
from tqdm.rich import tqdm
from DrissionPage import Chromium, ChromiumOptions
from lib.lib import Main


warnings.filterwarnings("ignore", category=TqdmExperimentalWarning)


async def main():
    lib = Main()
    co = ChromiumOptions()
    co.auto_port()
    co.incognito()

    print("Checking for updates...")
    await lib.checkUpdate()

    while True:
        browserPath = input(
            "\033[1m"
            "\n(RECOMMENDED) Press enter in order to use the default browser path (If you have Chrome installed)"
            "\033[0m"
            "\nIf you prefer to use other Chromium browser other than Chrome, please enter its executable path here. (e.g: C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe)"
            "\nHere are some supported browsers that are tested and able to use:"
            "\n- Chrome"
            "\n- Brave"
            "\nBrowser executable path: "
        ).replace('"', "").replace("'", "")
        if browserPath != "":
            if os.path.exists(browserPath):
                co.set_browser_path(browserPath)
                break
            else:
                print("Please enter a valid path.")
        else:
            break

    while True:
        passw = (
            input(
                "\033[1m"
                "\n(RECOMMENDED) Press enter in order to use the default password"
                "\033[0m"
                "\nIf you prefer to use your own password, do make sure that your password fulfill the below requirement:\n- Use at least 8 characters.\nPassword: "
            )
            or "Qing762.chy"
        )
        if passw != "Qing762.chy":
            result = await lib.checkPassword(passw)
            print(result)
            if "does not meet the requirements" not in result:
                break
        else:
            break

    proxyUsage = input(
        "\nWould you like to use a proxy?\nPlease enter the proxy IP and port in the format of IP:PORT (Example: http://localhost:1080). Press enter to skip.\nProxy: "
    )

    accounts = []

    while True:
        executionCount = input(
            "\nNumber of accounts to generate (Default: 1): "
        )
        try:
            executionCount = int(executionCount)
            break
        except ValueError:
            if executionCount == "":
                executionCount = 1
                break
            else:
                print("Please enter a valid number.")
    print()

    if proxyUsage != "":
        if lib.testProxy(proxyUsage)[0] is True:
            co.set_proxy(proxyUsage)
        else:
            print(lib.testProxy(proxyUsage)[1])

    for x in range(executionCount):
        bar = tqdm(total=100)
        bar.set_description(f"Initial setup completed [{x + 1}/{executionCount}]")
        bar.update(20)
        chrome = Chromium(addr_or_opts=co)
        page = chrome.latest_tab
        email, emailPassword, token, emailID = lib.generateEmail(passw)
        bar.set_description(f"Generated email [{x + 1}/{executionCount}]")
        bar.update(10)

        bar.set_description(f"Account generation process [{x + 1}/{executionCount}]")
        bar.update(20)

        page.get("https://mega.nz/register")
        page.ele("#register-firstname-registerpage2").input("qing")
        page.ele("#register-lastname-registerpage2").input("chy")
        page.ele("#register-email-registerpage2").input(email)
        page.run_js_loaded(f'document.getElementById("register-password-registerpage2").value = "{passw}";')
        page.run_js_loaded(f'document.getElementById("register-password-registerpage3").value = "{passw}";')
        page.listen.start("https://mails.org", method="POST")
        page.ele('xpath://*[@id="register_form"]/div[1]/div[8]/div[1]/input').click()
        page.ele('xpath://*[@id="register-check-registerpage2"]').click()
        page.ele('xpath://*[@id="register_form"]/div[1]/button').click()

        bar.set_description(f"Signup process [{x + 1}/{executionCount}]")
        bar.update(30)

        if page.ele('xpath://*[@id="bodyel"]/section[5]/div[14]/section/div/div[2]/div[1]', timeout=60):
            link = None
            while True:
                messages = lib.fetchVerification(email, emailPassword, emailID)
                if len(messages) > 0:
                    break
            msg = messages[0]
            body = getattr(msg, 'text', None)
            if not body and hasattr(msg, 'html') and msg.html:
                body = msg.html[0]
            if body:
                match = re.search(r'https://mega.nz/#confirm[^\s]+', body)
                if match:
                    link = match.group(0)
            if link:
                bar.set_description(
                    f"Verifying email address [{x + 1}/{executionCount}]"
                )
                bar.update(10)
                page.get(link.replace("#", "").replace('"', ""))
                page.ele("#login-password2").input(passw)
                page.ele('.mega-button positive login-button large right').click()
                if page.ele('xpath://*[@id="startholder"]/div[2]/div/div[2]/div[4]', timeout=60):
                    bar.set_description("Clearing cache and data")
                    bar.update(9)
                    page.set.cookies.clear()
                    page.clear_cache()
                    chrome.set.cookies.clear()
                    chrome.clear_cache()
                    chrome.quit()

                    accounts.append({"email": email, "password": passw, "emailPassword": emailPassword})

                    bar.set_description(f"Done [{x + 1}/{executionCount}]")
                    bar.update(1)
                    bar.close()
                    print()
                else:
                    print("Failed to verify email. Exiting...")
            else:
                print(
                    "Failed to find verification email. You may need to verify it manually. Skipping and continuing...\n"
                )
        else:
            print("Failed to register. Exiting...")

    with open("accounts.txt", "a") as f:
        for account in accounts:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            f.write(
                f"Email: {account['email']}, Password: {account['password']}, Email Password: {account['emailPassword']} (Created at {timestamp})\n"
            )
    print("\033[1m" "Credentials:")

    for account in accounts:
        print(f"Email: {account['email']}, Password: {account['password']}, Email Password: {account['emailPassword']}")
    print("\033[0m" "\nCredentials saved to accounts.txt\nHave fun using Mega!")

if __name__ == "__main__":
    asyncio.run(main())
