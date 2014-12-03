import copy
from datetime import datetime
import json
import os
import random

from config import cfg, modules


# Global to keep track of returned data
# As long as we never give out a reference to this, it should be reliable
#
# NB: This is not thread-safe
#
# Data format: { number of arrays: { date: data } }
#
# Need to keep a separate cache for each number of arrays as this may change
# over the course of testing
#
# The cache of actual data is assumed to have the actual number of arrays
# (ie, 10 arrays)
GDFD_CACHE = {}
GMD_CACHE = {}


def get_data_for_date(date):
    fmt = '%d-%m-%Y'
    date = datetime.strptime(date, fmt).strftime(fmt)

    numArrays = len(modules.SUPPORT.ARRAYS)

    if numArrays not in GDFD_CACHE:
        GDFD_CACHE[numArrays] = {}

    if date not in GDFD_CACHE[numArrays]:
        _create_data(date, numArrays)

    # Must return a COPY of the data, so that bad scripts can't mess up our
    # cache by mutating the original data
    return copy.deepcopy(GDFD_CACHE[numArrays][date])


def get_max_data(date):
    numArrays = len(modules.SUPPORT.ARRAYS)

    if numArrays not in GMD_CACHE:
        GMD_CACHE[numArrays] = {}

    if date not in GMD_CACHE[numArrays]:
        _create_data(date, numArrays)

    return copy.deepcopy(GMD_CACHE[numArrays][date])


def _create_data(date, numArrays):
    entries = []
    values = []

    for n in range(random.randint(1, 50)):
        data = ['01:%02d'%n, random.random()*40,
                random.random()*1000] + [random.randint(0, 10e6)
                        for _ in modules.SUPPORT.ARRAYS]

        values.append(data[1:])
        entries.append(','.join(map(str, data)))

    GDFD_CACHE[numArrays][date] = '\n'.join(entries) + '\n'

    maximums = [date] + [max(row[i] for row in values)
            for i,_ in enumerate(values[0])]

    GMD_CACHE[numArrays][date] = ','.join(map(str, maximums)) + '\n'
