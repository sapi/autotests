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
CACHE = {}
ACTUAL_CACHED_DATA = {}

path = os.path.join(
        os.getcwd(),
        cfg.SUITE_SUPPORT_RELATIVE_DIR,
        'assign2_cache.json',
    )

with open(path, 'rU') as f:
    ACTUAL_CACHED_DATA.update(json.loads(f.read()))


def get_data_for_date(date):
    fmt = '%d-%m-%Y'
    date = datetime.strptime(date, fmt).strftime(fmt)

    numArrays = len(modules.SUPPORT.ARRAYS)

    if numArrays not in CACHE:
        CACHE[numArrays] = {}

    if date not in CACHE[numArrays]:
        if date in ACTUAL_CACHED_DATA and numArrays == 10:  # the actual number
            CACHE[numArrays][date] = ACTUAL_CACHED_DATA[date]
        else:
            entries = []

            for n in range(random.randint(1, 50)):
                data = ['01:%02d'%n, random.random()*40,
                        random.random()*1000] + [random.randint(0, 10e6)
                                for _ in modules.SUPPORT.ARRAYS]
                entries.append(','.join(map(str, data)))

            CACHE[numArrays][date] = '\n'.join(entries) + '\n'

    # Must return a COPY of the data, so that bad scripts can't mess up our
    # cache by mutating the original data
    return copy.deepcopy(CACHE[numArrays][date])
