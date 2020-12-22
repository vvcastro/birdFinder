from bs4 import BeautifulSoup
import numpy as np
import requests
import random
import time
import csv

# page with index for all birds on Chile
BASE_URL = 'https://www.avesdechile.cl/'

# request index site
page = requests.get(BASE_URL + 'aves03.htm')
soup = BeautifulSoup(page.content, "lxml")

# get urls for every bird in Chile
index_names = soup.find("blockquote")
birds_links = index_names.findAll("a", attrs={"name": None})

# prune links
birds_info = {}
for i, bird_link in enumerate(birds_links):
    birds_info[i] = {"URL": BASE_URL + bird_link["href"], "SEO Name": bird_link.text.strip()}

print("#" * 20)
print(f'{len(birds_info)} aves encontradas!')
print("#" * 20)

# SCRAPING EACH BIRD RECOLECTED

# time between requests
times = [5.8, 6.6, 7, 7.7, 8, 8.5, 9, 8.5, 3.6, 3.9, 6.2]

birds_data = {}
for i, bird in enumerate(list(birds_info.values())):
    print(f'({i + 1}/{len(birds_info)}) Iterating over {bird["SEO Name"]}')

    # requests bird page
    bird_page = requests.get(bird["URL"])
    bird_soup = BeautifulSoup(bird_page.content, "lxml")

    # scrape important information
    centers = bird_soup.findAll("center")
    order, family = np.nan, np.nan
    for center in centers:
        if 'orden' in center.text.lower():
            order = center.text.split(':')[1].strip()
        elif 'familia' in center.text.lower():
            family = center.text.split(':')[1].strip()

    # get common name, scientific name and english name
    names = bird_soup.findAll("td", attrs={"background": 'fond3.gif'})

    # process information obtained
    birds_data[i] = {}
    birds_data[i]["SEO Name"] = birds_info[i]["SEO Name"]

    # run with try/except loops and then manually prune information
    birds_data[i]["Order"] = order
    birds_data[i]["Family"] = family
    for idx, (attr, name) in enumerate(zip(["Common Name", "Scientific Name", "English Name"], names)):
        birds_data[i][attr] = names[idx].text.lower().capitalize().strip()

    # wait to avoid overload on server
    sleep_time = random.choice(times)
    time.sleep(sleep_time)

# save as csv
columns = ["Common Name", "SEO Name", "Scientific Name", "English Name", "Order", "Family"]
with open('data/chileanBirds.csv', 'w') as birdsCSV:
    writer = csv.DictWriter(birdsCSV, fieldnames=columns)
    writer.writeheader()
    for idx, bird in birds_data.items():
        writer.writerow(bird)
