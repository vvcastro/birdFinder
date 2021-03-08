from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import matplotlib.pyplot as plt
from selenium import webdriver
from io import BytesIO
from PIL import Image
import pandas as pd
import argparse
import shutil
import random
import time
import os

# parse account idx
parser = argparse.ArgumentParser()
parser.add_argument('--idx', type=int)
args = parser.parse_args()

# ebird to scrape
EBIRD_URL = "https://ebird.org/media"
EBIRD_USER = {0: "randomuser3", 1: "randomuser4", 2: "faxarel407", 3: "randomuser3", 4: "randomuser4", 5: "bc3b2aa0f0"}
EBIRD_PASS = "123123123"

# temporary directory to save files
temp_dir = os.path.join(os.getcwd(), 'temp{}'.format(args.idx))
done_dir = os.path.join(os.getcwd(), 'data', 'eBird')
os.makedirs(temp_dir, exist_ok=True)
os.makedirs(done_dir, exist_ok=True)

# driver profile options
profile = webdriver.FirefoxProfile()
agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.106 Safari/537.36'
profile.set_preference("general.useragent.override", agent)

# options: download automatically to custom directory
profile.set_preference("browser.download.dir", temp_dir)
profile.set_preference('browser.download.manager.showWhenStarting', False)
profile.set_preference('browser.download.folderList', 2)
profile.set_preference('browser.helperApps.neverAsk.saveToDisk', 'text/csv')

# initialize driver
options = Options()
options.headless = True
driver = webdriver.Firefox(profile, options=options)

# get to ebird page
driver.get(EBIRD_URL)

#  LOG IN INTO eBird
log_button = '/html/body/header/div[4]/div[3]/div[2]/ul/li[2]/a'
try:
    log_element = EC.presence_of_element_located((By.XPATH, log_button))
    WebDriverWait(driver, 10).until(log_element)
except TimeoutException:
    print('- Waiting for main to load!')
finally:
    driver.find_element_by_xpath(log_button).click()

# insert credentials and log in
uname = '//*[@id="input-user-name"]'
pword = '//*[@id="input-password"]'
form_button = '//*[@id="form-submit"]'
try:
    form_element = EC.presence_of_element_located((By.XPATH, form_button))
    WebDriverWait(driver, 10).until(form_element)
except TimeoutException:
    print('- Waiting for Sign Up page to load!')
finally:
    driver.find_element_by_xpath(uname).send_keys(EBIRD_USER[args.idx])
    driver.find_element_by_xpath(pword).send_keys(EBIRD_PASS)
    driver.find_element_by_xpath(form_button).click()

# SCRAPING: get names to search from birdNames.csv
bird_names = pd.read_csv(os.path.join('data', 'birdNames.csv'))
search_names = list(bird_names["English Name"].to_numpy())

# SCRAPING: for each name search and download all data
times = [3.25, 3.75, 4, 4.25, 4.75, 5]

# elements xpaths
search_box = '//*[@id="SearchBox-field"]'
download_text = '/html/body/main/form/div/div[1]/div/div[2]/a'

# iterate over all names
last_link = ''
for i, name in enumerate(search_names[(args.idx * 100):min((args.idx + 1) * 100, len(search_names))]):

    print('({}/{}) - {}'.format(i + 1, 100, name))
    if (name + '.csv' in os.listdir(done_dir)):
        print('   - Done')
        continue

    # put text in search box
    try:
        search_element = EC.presence_of_element_located((By.XPATH, search_box))
        WebDriverWait(driver, 10).until(search_element)
    finally:
        box = driver.find_element_by_xpath(search_box)
        box.send_keys(Keys.COMMAND, "a")
        box.send_keys(name)

    # wait until autocomplete and press enter to search
    time.sleep(2.5)
    box.send_keys(Keys.ENTER)

    # download raw bird data
    download_element = '/html/body/main/form/div/div[1]/div/div[2]/a'
    time.sleep(2.5)
    try:
        download_link = driver.find_element_by_xpath(download_element)
        current_link = download_link.get_attribute("href")
    except Exception:
        print('   - Problem 1 with .csv')
        continue

    if (last_link == current_link):
        print('   - Error: bird not found')
        continue
    else:
        last_link = current_link
    download_link.click()

    # wait until full download
    file = None
    while True:
        all_files = [f for f in os.listdir(temp_dir)]
        files = [f for f in os.listdir(temp_dir) if '.csv']

        # check condition
        if (len(files) == 1 and all_files == files):
            file = os.path.join(temp_dir, files[0])
            break
        time.sleep(1)

    # process data
    bird_df = pd.read_csv(file)
    bird_df = bird_df[bird_df["Format"] == 'Photo']

    # move file to preprocessed list
    bird_df.to_csv(os.path.join(done_dir, '{}.csv'.format(name)))
    os.remove(file)
    print('   - Done: {} images!'.format(len(bird_df)))

    time.sleep(random.choice(times))

driver.quit()

# eliminate temp files
shutil.rmtree(temp_dir, ignore_errors=True)
os.remove('geckodriver.log')
