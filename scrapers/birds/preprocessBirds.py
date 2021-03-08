import pandas as pd
import numpy as np
import re
import os

OBJ = 'birdNames'

if (OBJ == 'birdNames'):
    data = pd.read_csv('data/birdNames.csv')

    # edit columns
    data = data[['Scientific Name', 'English Name', 'Common Name', 'SEO Name', 'Order', 'Family']]
    data['Scientific Name'] = data['Scientific Name'].apply(lambda x: re.sub("[\(].*?[\)]", "", x).strip())
    data['English Name'] = data['English Name'].apply(lambda x: re.sub("[\(].*?[\)]", "", x).strip().capitalize())
    data = data.sort_values(by=['Scientific Name', 'English Name'])
    data.to_csv('data/birdNames.csv', index=False)

elif (OBJ == 'eBird'):
    DATA_DIR = os.path.join('data', 'eBird')

    # iterate over all eBird files
    files = [os.path.join(DATA_DIR, f) for f in os.listdir(DATA_DIR) if '.csv' in f]
    data = None

    # append relevant data
    for file in files:
        file_data = pd.read_csv(file)
        
