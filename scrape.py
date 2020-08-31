import requests
import os
import pathlib
from bs4 import BeautifulSoup
import csv


OUTPUT_PATH = os.getcwd() + '/data'
GRAPH_NAME = 'graphs'
GRAPH_PATH = OUTPUT_PATH + '/' + GRAPH_NAME
TABLE_NAME = 'tables'
TABLE_PATH = OUTPUT_PATH + '/' + TABLE_NAME

IMAGE_ROOT = 'https://covid19.yale.edu/sites/default/files/images'

def mkdirp(directory):
    pathlib.Path(directory).mkdir(parents=True, exist_ok=True)

for directory in (OUTPUT_PATH, GRAPH_PATH, TABLE_PATH):
    mkdirp(directory)

def categorize(filename: str):
    first, stripped = filename.split('-', 1)
    if first in ('yale', 'connecticut'):
        mkdirp(GRAPH_PATH + '/' + first)
        return stripped, first + '/'
    return filename, ''

def download(filename: str):
    filename, category = categorize(filename)
    url = IMAGE_ROOT + '/' + filename
    path = GRAPH_PATH + '/' + category + filename
    if os.path.exists(path):
        print('%s already exists, skipping download.' % filename)
    else:
        print('Downloading %s.' % image)
        r = requests.get(url, allow_redirects=True)
        with open(path, 'wb') as f:
            f.write(r.content)


STATISTICS_URL = 'https://covid19.yale.edu/yale-covid-19-statistics'

r = requests.get(STATISTICS_URL)
soup = BeautifulSoup(r.text, 'html.parser')
body = soup.find('div', {'class': 'field-item even'})
imgs = body.find_all('img')
print('Found %d graphs.' % len(imgs))

images = [img['src'].split('/')[-1] for img in imgs]
for image in images:
    download(image)

TABLES_URL = 'https://covid19.yale.edu/yale-statistics'

r = requests.get(TABLES_URL)
soup = BeautifulSoup(r.text, 'html.parser')
body = soup.find('div', {'class': 'field-item even'})

tables = []
for table in body.find_all('table'):
    caption = table.find('caption').text
    print('Parsing table %s.' % caption)
    output_rows = []
    for table_row in table.find_all('tr'):
        columns = table_row.find_all(['th', 'td'])
        output_row = []
        for column in columns:
            output_row.append(column.text)
        output_rows.append(output_row)
    tables.append(output_rows)

def merge_tables(tables):
    """
    Merge a list of tables with the same rows into one containing all the data.
    :param tables: list of lists of data rows
    """
    base = tables[0]
    for table in tables[1:]:
        for row_index, row in enumerate(table):
            # Chop off duplicate leftmost column
            base[row_index] += row[1:]

# Merge Yale tables into one
yale_table = merge_tables(tables[2:4])
# Merge Connecticut tables into one
connecticut_table = merge_tables(tables[4:6])

tables = [yale_table, connecticut_table]

print(tables)

"""
for table in tables:
    with open(TABLE_PATH + '/' + caption + '.csv', 'w') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerows(output_rows)
"""
