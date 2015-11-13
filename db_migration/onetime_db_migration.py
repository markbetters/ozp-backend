"""
Script to migrate the existing data (in MySQL) into PostgreSQL

Prereqs:
* for each table in the old database, there is a corresponding file created
    via: mysqldump -u ozp -p ozp TABLENAME > TABLENAME.sql --complete-insert --hex-blob
* all images have been copied to a local directory

Usage:
    Assumes that the database referenced in settings.py is empty
"""
import datetime
import json
import os
import pytz
import re
import sys

sys.path.insert(0, os.path.realpath(os.path.join(os.path.dirname(__file__), '../')))

os.environ['DJANGO_SETTINGS_MODULE'] = 'ozp.settings'
from django.conf import settings

from ozpcenter import models as models
from ozpcenter import model_access
from ozpcenter import utils

# path to the SQL dump files
SQL_FILE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'sql_dumps') + '/'
# path to the images
IMAGE_FILE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'images') + '/'

def get_index_next_unescaped_quote(str):
    """
    Get the index of the next unescaped single quote in a given string
    """
    for i, c in enumerate(str):
        if c == "'" and str[i-1] != "\\":
            return i

def get_columns(table):
    """
    Get the columns of a table in an array

    Columns will be in the same order as the values appear in the data
    """
    with open('%s/%s.sql' % (SQL_FILE_PATH, table), 'r') as f:
        data = f.read().replace('\n', '')
    # extract a string like (`id`, `version`, `created_by_id`)
    columns = utils.find_between(data, "INSERT INTO `%s`" % table, " VALUES")
    # remove parenthesis, backticks, and spaces
    columns = re.sub('[`() ]', '', columns)
    columns = columns.split(',')
    return columns

def get_values(table, column_count):
    """
    Get the values of a table in an array of arrays

    Args:
        table: name of the database table
        column_count: number of columns in this table
    """
    values = []
    with open('%s/%s.sql' % (SQL_FILE_PATH, table), 'r') as f:
        data = f.read().replace('\n', '')
    # extract the data we want
    values_str = utils.find_between(data, "VALUES ", ");") + ')'

    # values can contain special chars like paranthesis and commas, so we
    # have to be smart about how we extract the data

    while values_str:
        if values_str[0] != '(':
            print('Error: each value must start with opening paranthesis')
            return None
        # remove leading '('
        values_str = values_str[1:]
        # create empty array that will hold all values for this entry
        entry_values = []
        current_entry_finished = False
        columns_processed = 0
        while not current_entry_finished:
            # check for hex value
            if values_str[:2] == '0x':
                val = re.findall(r'0x[0-9ABCDEF]*', values_str)[0]
                # val = '0x' + utils.find_between(values_str, '0x', ',')
                entry_values.append(val)
                # remove extracted data from the original string
                idx = len(val)
                values_str = values_str[idx:]
                columns_processed += 1
                print('got hex value: %s' % val)
                # remove comma
                if values_str[0] != ',' and columns_processed != column_count:
                    print('Error: comma not found after extracting hex value')
                    return None
                if columns_processed < column_count:
                    values_str = values_str[1:]
            # check for a string value
            elif values_str[0] == "'":
                # read all chars between this quote and next unescaped quote
                # remove the leading quote
                values_str = values_str[1:]
                # find the index of the next unescaped quote
                idx = get_index_next_unescaped_quote(values_str)
                val = values_str[:idx]
                entry_values.append(val)
                # remove extracted data from original string
                idx = len(val) + 1 # +1 for the trailing quote
                values_str = values_str[idx:]
                columns_processed += 1
                print('got string value: %s' % val)
                # remove comma
                if values_str[0] != ',' and columns_processed != column_count:
                    print('Error: comma not found after extracting string value. string[0]: %s' % values_str[0])
                    return None
                if columns_processed < column_count:
                    values_str = values_str[1:]
            # check for NULL value
            elif values_str[0:4] == 'NULL':
                val = None
                entry_values.append(val)
                values_str = values_str[4:]
                columns_processed += 1
                print('got NULL value: %s' % val)
                # remove comma
                if values_str[0] != ',' and columns_processed != column_count:
                    print('Error: comma not found after extracting NULL value')
                    return None
                if columns_processed < column_count:
                    values_str = values_str[1:]
            # check for integer value
            elif values_str[0] in ['0','1','2','3','4','5','6','7','8','9']:
                val = re.findall(r'\d+', values_str)[0]
                entry_values.append(val)
                # remove extracted data from original string
                idx = len(val)
                values_str = values_str[idx:]
                columns_processed += 1
                print('got integer value: %s' % val)
                # remove comma
                if values_str[0] != ',' and columns_processed != column_count:
                    print('Error: comma not found after extracting integer value')
                    return None
                if columns_processed < column_count:
                    values_str = values_str[1:]
            else:
                print('Error: found invalid character in data: %s' % values_str[0])
                return None

            if columns_processed == column_count:
                current_entry_finished = True
                print('completed processing of row')
                # remove closing parenthesis
                if values_str[0] != ')':
                    print('Error: closing parenthesis not found at end of row data')
                    return None
                values_str = values_str[1:]
                # remove the comma between entries, unless this is the last entry
                if values_str:
                    values_str = values_str[1:]

        values.append(entry_values)
    return values

def run():
    print('running db_migration!')
    migrate_category()
    migrate_listing()

def migrate_category():
    print('migrating categories')
    columns = get_columns('category')
    values = get_values('category', len(columns))
    print('category columns: %s' % columns)
    print('category values: %s' % values)

def migrate_listing():
    print('migrating listings')
    columns = get_columns('listing')
    values = get_values('listing', len(columns))
    print('listing columns: %s' % columns)
    print('listing values: %s' % values)

if __name__ == "__main__":
    run()


