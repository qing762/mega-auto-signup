import asyncio
import re
import warnings
import time
from tqdm import TqdmExperimentalWarning
from tqdm.rich import tqdm
from DrissionPage import Chromium, ChromiumOptions
from lib.lib import Main


warnings.filterwarnings("ignore", category=TqdmExperimentalWarning)


async def main():
    lib = Main()
    port = ChromiumOptions().auto_port()

    print("Checking for updates...")
    await lib.checkUpdate()

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

    for x in range(executionCount):
        bar = tqdm(total=100)
        bar.set_description(f"Initial setup completed [{x + 1}/{executionCount}]")
        bar.update(20)
        chrome = Chromium(addr_or_opts=port)
        page = chrome.get_tab(id_or_num=1)
        page.listen.start("https://mails.org", method="POST")
        page.get("https://mails.org")

        for _ in range(10):
            result = page.listen.wait()
            if result.url == "https://mails.org/api/email/generate":
                email = result.response.body["message"]
                break

        if not email:
            print("Failed to generate email. Exiting...")
            continue

        bar.set_description(f"Account generation process [{x + 1}/{executionCount}]")
        bar.update(20)

        tab = chrome.new_tab("https://mega.nz/register")

        tab.ele("#register-firstname-registerpage2").input("qing")
        tab.ele("#register-lastname-registerpage2").input("chy")
        tab.ele("#register-email-registerpage2").input(email)
        tab.run_js_loaded(f'document.getElementById("register-password-registerpage2").value = "{passw}";')
        tab.run_js_loaded(f'document.getElementById("register-password-registerpage3").value = "{passw}";')
        page.listen.start("https://mails.org", method="POST")
        tab.ele('xpath://*[@id="register_form"]/div[8]/div[1]/input').click()
        tab.ele('xpath://*[@id="register-check-registerpage2"]').click()
        tab.ele('xpath://*[@id="register_form"]/button').click()

        bar.set_description(f"Signup process [{x + 1}/{executionCount}]")
        bar.update(30)

        if tab.ele('xpath://*[@id="bodyel"]/section[5]/div[14]/section/div/div[2]/div[1]', timeout=60):
            link = None
            for _ in range(10):
                result = page.listen.wait()
                content = result.response.body["emails"]
                if not content:
                    continue
                for y in content.items():
                    if y[1]["subject"] == "MEGA email verification required":
                        links = re.findall(
                            r"https://mega.nz/#confirm[^\s]+", y[1]["body"]
                        )
                        if links:
                            link = links[0]
                            break
                    if link:
                        break
                if link:
                    break
            if link:
                bar.set_description(
                    f"Verifying email address [{x + 1}/{executionCount}]"
                )
                bar.update(20)
                tab.get(link.replace("#", "").replace('"', ""))
                tab.ele("#login-password2").input(passw)
                tab.ele('.mega-button positive login-button large right').click()
                if tab.ele('.pricing-pg pro-plans-cards-container tab-ctrl-ind card-container', timeout=60):
                    bar.set_description("Clearing cache and data")
                    bar.update(9)
                    tab.set.cookies.clear()
                    tab.clear_cache()
                    chrome.set.cookies.clear()
                    chrome.clear_cache()
                    chrome.quit()

                    accounts.append({"email": email, "password": passw})

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
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
            f.write(
                f"Email: {account['email']}, Password: {account['password']}, (Created at {timestamp})\n"
            )

    print("\033[1m" "Credentials:")

    for account in accounts:
        print(f"Email: {account['email']}, Password: {account['password']}")
    print("\033[0m" "\nCredentials saved to accounts.txt\nHave fun using Mega!")

if __name__ == "__main__":
    asyncio.run(main())
