import requests
import os
import pathlib
from bs4 import BeautifulSoup


OUTPUT_PATH = os.getcwd() + '/data'
GRAPH_NAME = 'graphs'
GRAPH_PATH = OUTPUT_PATH + '/' + GRAPH_NAME
TABLE_NAME = 'tables'
TABLE_PATH = OUTPUT_PATH + '/' + TABLE_NAME

IMAGE_ROOT = 'https://covid19.yale.edu/sites/default/files/images'

for directory in (OUTPUT_PATH, GRAPH_PATH):
    pathlib.Path(directory).mkdir(parents=True, exist_ok=True)

def get_category(filename: str):
    first, stripped = filename.split('-', 1)
    if first in ('yale', 'connecticut'):
        return rest + '/', stripped
    return filename, ''

def download(filename: str):
    filename, category = categorize(filename)
    url = IMAGE_ROOT + '/' + filename
    path = GRAPH_PATH + '/' + category + filename
    r = requests.get(url, allow_redirects=True)
    with open(path, 'wb') as f:
        f.write(r.content)


STATISTICS_URL = 'https://covid19.yale.edu/yale-covid-19-statistics'

r = requests.get(STATISTICS_URL)
soup = BeautifulSoup(r.text, 'html.parser')
body = soup.find('div', {'class': 'field-item even'})
imgs = body.find_all('img')
print('Found %d elements.' % len(imgs))

images = [img['src'].split('/')[-1] for img in imgs]
for image in images:
    download(image)

TABLES_URL = 'https://covid19.yale.edu/yale-statistics/yale-covid-19-statistics-data-tables'

r = requests.get(TABLES_URL)
soup = BeautifulSoup(r.text, 'html.parser')
body = soup.find('div', {'class': 'field-item even'})
tables = body.find_all('table')
for table in tables:
    caption = table.find('caption').text
    output_rows = []
    for table_row in table.find_all('tr'):
        columns = table_row.findAll('td')
        output_row = []
        for column in columns:
            output_row.append(column.text)
        output_rows.append(output_row)

    with open(caption + '.csv', 'wb') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerows(output_rows)
