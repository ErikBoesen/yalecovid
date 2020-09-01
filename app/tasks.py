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
    if string.endswith('%'):
        return float(string.rstrip('%'))
    if string.isnumeric():
        return int(string)
    return string


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

def split_peak(table, split_on=', on'):
    """
    Split the last column of a table into numerical and rate columns.
    """
    for r in range(1, len(table)):
        whole = table[r].pop()
        table[r] += whole.split(split_on)
    return table

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

    # Split up "peak" columns into number and date
    tables = [split_peak(table) for table in tables]

    # Merge Yale tables into one
    yale_table = merge_tables(tables[:2])
    yale_table[0] = [
        'population',
        'total_cases',
        'weekly_cases',
        'new_case_peak',
        'new_case_peak_date',
        # Why do they include useless statistics like this??
        'most_recent_date_below_5_percent_positivity',
        # TODO I wish
        #'total_positivity_rate',
        'weekly_positivity_rate',
        'peak_positivity_rate',
        'peak_positivity_rate_date',
    ]

    yale_data = to_dicts(yale_table)

    yale_data[0]['populations'] = {
        population['population'].lower(): population
        for population in yale_data[1:]
    }
    yale_data = yale_data[0]
    del yale_data['population']
    for population in yale_data['populations']:
        del population['population']

    redis.set('yale', json.dumps(yale_data))

    # Merge Connecticut tables into one
    """
    connecticut_table = merge_tables(tables[2:])
    connecticut_table[0][0] = 'County'

    connecticut_data = to_dicts(connecticut_table)
    redis.set('connecticut', json.dumps(connecticut_data))
    """

    redis.set('last_updated', int(time.time()))
    print('Updated data.')


@celery.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(
        100,
        scrape.s()
    )
    print('Set up periodic tasks.')
