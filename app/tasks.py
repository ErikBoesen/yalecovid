from app import app, redis, celery

import requests
from bs4 import BeautifulSoup
import json
import time


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
    return base


def clean_number(string: str):
    """
    Return maximally simplified numerical value.
    i.e. remove percent signs and convert to int/float.
    """
    if val.endswith('%'):
        return float(val.rstrip('%'))
    if val.isnumeric():
        return int(val)
    return val

def to_dicts(table):
    keys = table[0]
    return [
        {
            # Convert to int if possible
            key: clean_number(val)
            for key, val in zip(keys, row)
        }
        for row in table[1:]
    ]

@celery.task
def scrape():
    STATISTICS_URL = 'https://covid19.yale.edu/yale-covid-19-statistics'

    r = requests.get(STATISTICS_URL)
    soup = BeautifulSoup(r.text, 'html.parser')
    body = soup.find('div', {'class': 'field-item even'})

    # TODO: find a better way to target the first div
    # Unfortunately it doesn't have identifying information other than a class .alert-[color]
    alert_level = body.find('div')['class'][0].split('-')[1]
    redis.set('alert_level', alert_level)

    TABLES_URL = 'https://covid19.yale.edu/yale-statistics/yale-covid-19-statistics-data-tables'

    r = requests.get(TABLES_URL)
    soup = BeautifulSoup(r.text, 'html.parser')
    body = soup.find('div', {'class': 'field-item even'})

    tables = []
    for table in body.find_all('table'):
        caption = table.find('caption').text
        output_rows = []
        for table_row in table.find_all('tr'):
            columns = table_row.find_all(['th', 'td'])
            output_row = []
            for column in columns:
                output_row.append(column.text)
            output_rows.append(output_row)
        tables.append(output_rows)

    # Merge Yale tables into one
    yale_table = merge_tables(tables[:2])
    yale_table[0][0] = 'Population'
    # Merge Connecticut tables into one
    connecticut_table = merge_tables(tables[2:])
    connecticut_table[0][0] = 'County'

    yale_data = to_dicts(yale_table)
    connecticut_data = to_dicts(connecticut_table)

    redis.set('yale', json.dumps(yale_data))
    redis.set('connecticut', json.dumps(connecticut_data))
    print('Updated data.')

    redis.set('last_updated', int(time.time()))


@celery.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(
        100,
        scrape.s()
    )
    print('Set up periodic tasks.')
