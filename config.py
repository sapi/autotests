import importlib


# Functions to test
FUNCTIONS = [
        'load_data',
        'max_temperature',
        'total_energy',
        'max_power',
        'display_stats',
        'display_weekly_stats',
        'interact',
    ]

FUNCTIONS_TO_DIFF_OUTPUT = [
        'display_stats',
        'display_weekly_stats',
        'interact',
    ]

# Modules which need to be replaced
TEST_SCRIPT_NAME = 'script_under_test'
SOLUTION_NAME = 'assign1_soln'

NAMES_TO_IMPORT = [
        TEST_SCRIPT_NAME,
        SOLUTION_NAME,
    ]

MODULES_TO_REPLACE = map(importlib.import_module, NAMES_TO_IMPORT)

SCRIPT_MODULE = MODULES_TO_REPLACE[0]
SOLUTION_MODULE = MODULES_TO_REPLACE[1]

# Test suite name
SUITE_NAME = 'assign1'
SUPPORT_FILE_NAME = 'assign1_support'
