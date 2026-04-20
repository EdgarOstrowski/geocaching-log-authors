import argparse
import os
import time

from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys


def geocaching_com_login(driver, username, password):
    driver.get("https://www.geocaching.com/account/signin")
    time.sleep(2)

    username_field = driver.find_element(By.ID, "UsernameOrEmail")
    username_field.clear()
    username_field.send_keys(username)

    password_field = driver.find_element(By.ID, "Password")
    password_field.clear()
    password_field.send_keys(password)

    password_field.send_keys(Keys.RETURN)

    time.sleep(2)


def open_cache_page(driver, gccode):
    driver.get(f"https://www.geocaching.com/geocache/{gccode}")
    time.sleep(2)

    prev_count = 0

    while True:
        elements = driver.find_elements(By.CSS_SELECTOR, ".log-row")
        count = len(elements)

        # If no new items appeared, stop scrolling
        if count == prev_count:
            break

        prev_count = count

        # Scroll to bottom
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)


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

        if log_type is None:
            usernames.append(name)
        elif log_type.lower() == log_type.lower():
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

    load_dotenv()

    username = os.getenv('GC_USERNAME')
    password = os.getenv('GC_PASSWORD')

    geocaching_com_login(driver, username, password)
    open_cache_page(driver, "GCAT0RT")

    # "Write note", "will attend",
    usernames = get_list_of_usernames_from_cache_logs(driver, log_type="will attend")
    
    username = list(set(username))  # Remove duplicates
    usernames.sort()

    save_usernames_to_file(usernames, "GCAT0RT.txt")

    driver.quit()
