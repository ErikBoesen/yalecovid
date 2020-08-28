import requests
import os
import pathlib
from bs4 import BeautifulSoup


OUTPUT_PATH = os.getcwd() + '/data'
GRAPH_NAME = 'graphs'
GRAPH_PATH = OUTPUT_PATH + '/' + GRAPH_NAME

IMAGE_ROOT = 'https://covid19.yale.edu/sites/default/files/images'

for directory in (OUTPUT_PATH, GRAPH_PATH):
    pathlib.Path(directory).mkdir(parents=True, exist_ok=True)

def download(name: str):
    filename = name + '.png'
    url = IMAGE_ROOT + '/' + filename
    path = GRAPH_PATH + '/' + filename
    r = requests.get(url, allow_redirects=True)
    with open(path, 'wb') as f:
        f.write(r.content)


STATISTICS_URL = 'https://covid19.yale.edu/yale-covid-19-statistics'
TABLES_URL = 'https://covid19.yale.edu/yale-statistics/yale-covid-19-statistics-data-tables'

r = requests.get(STATISTICS_URL)
soup = BeautifulSoup(r, 'html.parser')
body = soup.find('div', {'class': 'field-item even'})
print(body)
