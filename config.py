import importlib

from model.namespaces import Namespace


_d = {
        # Functions to test
        'FUNCTIONS': [
                'load_data',
                'max_temperature',
                'total_energy',
                'max_power',
                'display_stats',
                'display_weekly_stats',
                'interact',
            ],

        'FUNCTIONS_TO_DIFF_OUTPUT': [
                'display_stats',
                'display_weekly_stats',
                'interact',
            ],

        # Modules which need to be replaced
        'TEST_SCRIPT_NAME': 'script_under_test',
        'SOLUTION_NAME': 'assign1_soln',
        'SUPPORT_NAME': 'assign1_support',

        # Name of test module
        'SUITE_NAME': 'assign1',
        'SUITE_SUPPORT_RELATIVE_DIR': 'suites/support',
}

cfg = Namespace(**_d)

_m = {
        'SCRIPT': cfg.TEST_SCRIPT_NAME,
        'SOLUTION': cfg.SOLUTION_NAME,
        'SUPPORT': cfg.SUPPORT_NAME,
}

# The test script will not be valid on the first run (but also not used)
for _attr,_n in _m.iteritems():
    try:
        _m[_attr] = importlib.import_module(_n)
    except ImportError:
        pass

modules = Namespace(**_m)

MODULES_TO_REPLACE = [
        modules.SCRIPT,
        modules.SOLUTION,
        modules.SUPPORT,
    ]
