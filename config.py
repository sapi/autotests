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
}

cfg = Namespace(**_d)

_m = {
        'SCRIPT': cfg.TEST_SCRIPT_NAME,
        'SOLUTION': cfg.SOLUTION_NAME,
        'SUPPORT': cfg.SUPPORT_NAME,
}
_m = {k: importlib.import_module(v) for k,v in _m.iteritems()}

modules = Namespace(**_m)

MODULES_TO_REPLACE = [
        modules.SCRIPT,
        modules.SOLUTION,
    ]
