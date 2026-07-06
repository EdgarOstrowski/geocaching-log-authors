import argparse
import os
import time
import getpass

from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException


AVAILABLE_LOG_TYPES = [
    "Will attend",
    "Write note",
    "Attended",
    "Announcement",
]


def get_username_and_password():

    load_dotenv()

    username = os.getenv('GC_USERNAME')
    password = os.getenv('GC_PASSWORD')

    if username is None:
        print("Enter your geocaching.com username: ")
        username = input()

    if password is None:
        password = getpass.getpass("Enter your geocaching.com password: ")


    return username, password


def geocaching_com_login(driver, username, password):
    driver.get("https://www.geocaching.com/account/signin")

    # Wait for sign-in page to be loaded before interacting with it.
    wait = WebDriverWait(driver, 15)
    wait.until(lambda d: d.execute_script("return document.readyState") == "complete")

    def click_necessary_only_button() -> bool:
        button_locators = [
            (By.ID, "CybotCookiebotDialogBodyButtonDecline"),
            (By.ID, "CybotCookiebotDialogBodyButtonNecessary"),
            (
                By.XPATH,
                "//button[contains(normalize-space(.), 'Necessary cookies only')]",
            ),
        ]

        for by, value in button_locators:
            for button in driver.find_elements(by, value):
                if button.is_displayed() and button.is_enabled():
                    button.click()
                    return True

        return False

    accepted = click_necessary_only_button()

    # Cookiebot can also be rendered inside an iframe.
    if not accepted:
        iframe_candidates = driver.find_elements(
            By.CSS_SELECTOR,
            "iframe#CybotCookiebotDialog, iframe[id*='CybotCookiebotDialog'], iframe[src*='cookiebot']",
        )

        for iframe in iframe_candidates:
            try:
                driver.switch_to.frame(iframe)
                if click_necessary_only_button():
                    accepted = True
                    break
            except TimeoutException:
                pass
            finally:
                driver.switch_to.default_content()

    username_field = wait.until(EC.visibility_of_element_located((By.ID, "UsernameOrEmail")))
    password_field = wait.until(EC.visibility_of_element_located((By.ID, "Password")))

    username_field.clear()
    username_field.send_keys(username)

    password_field.clear()
    password_field.send_keys(password)

    password_field.send_keys(Keys.RETURN)

    # Successful login should navigate away from the sign-in URL.
    wait.until(lambda d: "/account/signin" not in d.current_url.lower())


def open_cache_page(driver, gccode):
    driver.get(f"https://www.geocaching.com/geocache/{gccode}")
    time.sleep(2)

    prev_count = -1
    prev_scroll_top = -1
    stable_rounds = 0

    while True:
        elements = driver.find_elements(By.CSS_SELECTOR, ".log-row")
        count = len(elements)

        # `document.body` is not always the active scrolling element.
        # Use the page scrolling element so Firefox/Chromium behave consistently.
        driver.execute_script(
            """
            const scroller = document.scrollingElement || document.documentElement;
            scroller.scrollTo(0, scroller.scrollHeight);
            """
        )
        time.sleep(2)

        scroll_top = driver.execute_script(
            "return (document.scrollingElement || document.documentElement).scrollTop;"
        )

        # Stop when neither log count nor scroll position changes for a few rounds.
        if count == prev_count and scroll_top == prev_scroll_top:
            stable_rounds += 1
        else:
            stable_rounds = 0

        if stable_rounds >= 2:
            break

        prev_count = count
        prev_scroll_top = scroll_top


def get_list_of_usernames_from_cache_logs(driver, log_type=None):
    cache_logs_table = driver.find_element(By.ID, "cache_logs_table")
    logs = cache_logs_table.find_elements(By.CSS_SELECTOR, ".log-row")

    usernames = []
    selected_log_type = log_type.casefold() if log_type else None

    # Keep only logs that match the requested type when provided.
    for log in logs:
        left = log.find_element(By.CSS_SELECTOR, ".LogDisplayLeft")
        right = log.find_element(By.CSS_SELECTOR, ".LogDisplayRight")

        name = left.find_element(By.CSS_SELECTOR, ".h5").text
        current_log_type = right.find_element(By.CSS_SELECTOR, ".h4").text

        if selected_log_type and current_log_type.casefold() != selected_log_type:
            continue


        usernames.append(name)
        
        
    return usernames


def save_usernames_to_file(usernames, filename):
    with open(filename, encoding="utf-8", mode="w") as f:
        for username in usernames:
            f.write(username + "\n")


def build_parser():
    parser = argparse.ArgumentParser(description='Download list of geocachers that loga a specific cache.')
    parser.add_argument('--gccode', type=str, required=True, help='The GC code of the cache')
    parser.add_argument('--output', type=str, help='The output file to save the list of geocachers')
    parser.add_argument(
        '--log_type',
        type=str,
        default='Will attend',
        choices=AVAILABLE_LOG_TYPES,
        help='The log type to filter by',
    )
    return parser


if __name__ == "__main__":

    parser = build_parser()
    args = parser.parse_args()

    driver = webdriver.Firefox()

    username, password = get_username_and_password()
    gccode = args.gccode.strip().upper()
    output_file = args.output if args.output else f"{gccode}.txt"

    geocaching_com_login(driver, username, password)
    open_cache_page(driver, gccode)

    # "Write note", "will attend",
    usernames = get_list_of_usernames_from_cache_logs(driver, log_type=args.log_type)
    
    usernames = list(set(usernames))  # Remove duplicates
    usernames.sort(key=str.casefold)

    print(f"Found {len(usernames)} unique usernames for log type '{args.log_type}'.")
    print(f"Saving to file: {output_file}")
    
    save_usernames_to_file(usernames, output_file)

    driver.quit()
