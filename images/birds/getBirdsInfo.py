from bs4 import BeautifulSoup
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
print(f'{len(birds_info)} aves encontradas!')

# SCRAPING FOR EACH BIRD RECOLECTED
# time between requests
times = [5.8, 6.6, 7, 7.7, 8, 8.5, 9, 8.5, 3.6, 3.9, 6.2]

for i, bird in enumerate(list(birds_info.values())):
    print(f' - Iterating over {bird["SEO Name"]} ({i + 1}/{len(birds_info)})')

    # requests bird page
    bird_page = requests.get(bird["URL"])
    bird_soup = BeautifulSoup(bird_page.content, "lxml")

    # scrape important information
    order = bird_soup.find("b", string=lambda text: 'orden' in text.lower() if text is not None else False)
    family = bird_soup.find("b", string=lambda text: 'familia' in text.lower() if text is not None else False)

    # get common name, scientific name and english name
    names = bird_soup.findAll("td", attrs={"background": 'fond3.gif'})

    # process information obtained
    birds_info[i]["Order"] = order.text.split(':')[1].strip()
    birds_info[i]["Family"] = family.text.split(':')[1].strip()
    birds_info[i]["Common Name"] = names[0].text.lower().capitalize().strip()
    birds_info[i]["Scientific Name"] = names[1].text.lower().capitalize().strip()
    birds_info[i]["English Name"] = names[2].text.lower().capitalize().strip()

    # wait to avoid overload on server
    sleep_time = random.choice(times)
    time.sleep(sleep_time)


# save as csv
columns = ["Common Name", "SEO Name", "Scientific Name", "English Name", "Order", "Family", "URL"]
with open('images/birds/species.csv', 'w') as birdsCSV:
    writer = csv.DictWriter(birdsCSV, fieldnames=columns)
    writer.writeheader()
    for idx, bird in birds_info.items():
        writer.writerow(bird)
