import argparse
import os
import time
import getpass

from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys


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

    time.sleep(5)

    username_field = driver.find_element(By.ID, "UsernameOrEmail")
    username_field.clear()
    username_field.send_keys(username)

    password_field = driver.find_element(By.ID, "Password")
    password_field.clear()
    password_field.send_keys(password)

    time.sleep(5)

    password_field.send_keys(Keys.RETURN)

    time.sleep(20)


def open_cache_page(driver, gccode):
    driver.get(f"https://www.geocaching.com/geocache/{gccode}")
    time.sleep(2)

    prev_count = -1
    prev_scroll_top = -1
    stable_rounds = 0

    while True:
        elements = driver.find_elements(By.CSS_SELECTOR, ".log-row")
        count = len(elements)

        print(elements)

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

    # Get all logs despite the log type
    for log in logs:
        left = log.find_element(By.CSS_SELECTOR, ".LogDisplayLeft")
        right = log.find_element(By.CSS_SELECTOR, ".LogDisplayRight")

        name = left.find_element(By.CSS_SELECTOR, ".h5").text
        log_type = right.find_element(By.CSS_SELECTOR, ".h4").text


        usernames.append(name)
        
        
    return usernames


def save_usernames_to_file(usernames, filename):
    with open(filename, encoding="utf-8", mode="w") as f:
        for username in usernames:
            f.write(username + "\n")


def build_parser():
    parser = argparse.ArgumentParser(description='Download list of geocachers that loga a specific cache.')
    parser.add_argument('--gccode', type=str, help='The GC code of the cache')
    parser.add_argument('--output', type=str, help='The output file to save the list of geocachers')

    return parser


if __name__ == "__main__":

    parser = build_parser()
    args = parser.parse_args()

    driver = webdriver.Firefox()

    username, password = get_username_and_password()

    geocaching_com_login(driver, username, password)
    open_cache_page(driver, "GCAT0RT")

    # "Write note", "will attend",
    usernames = get_list_of_usernames_from_cache_logs(driver, log_type="will attend")
    
    usernames = list(set(usernames))  # Remove duplicates
    usernames.sort(key=str.casefold)

    save_usernames_to_file(usernames, "GCAT0RT.txt")

    driver.quit()
