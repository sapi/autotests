#!/usr/bin/env python

import importlib
import sys
import unittest

from config import cfg
from results.result import TestResult
from shared.args import parse_args


def try_import_functions():
    """
    try_import_functions() -> None

    Try to import all of the functions defined in the config file.

    """
    for function in cfg.FUNCTIONS:
        try:
            exec 'from %s import %s'%(cfg.TEST_SCRIPT_NAME, function)
        except ImportError:
            pass
        except Exception as e:
            print str(e)


def run_tests(args):
    # Hacky code ahead
    #
    # We want to know whether this script represents a masters student when
    # we're setting up decorators for the test cases.
    # This means that we need to set a flag before the import of the tests.
    # The best way I've found so far to do this is really hacky: mess with
    # the config module to set the appropriate arg.
    setattr(cfg, 'masters', args.masters)

    # Now grab the appropriate test suite, based on the config setting
    tests = importlib.import_module('suites.%s'%cfg.SUITE_NAME)

    suite = tests.suite()

    runner = unittest.TextTestRunner(resultclass=TestResult)

    # The TextTestRunner will redirect stdout, but we want it later, so we
    # need to save and restore it
    stdout = sys.stdout
    results = runner.run(suite)
    sys.stdout = stdout

    return results


def print_results(results):
    print
    print '/--------------------\\'
    print '| Summary of Results |'
    print '\\--------------------/'

    fnnames = sorted(results.results.keys())
    for fnname in fnnames:
        tests = results.results[fnname]
        print
        print '%s: %d/%d'%(fnname, sum(s for n,s in tests), len(tests))

        for name,wasSuccess in sorted(tests, key=lambda (n,s): n):
            print ' '*4 + u'%s %s'%('+' if wasSuccess else '-', name)

    if results.messages:
        print
        print
        print '/--------------\\'
        print '| Failed Tests |'
        print '\\--------------/'
        print

        for fnname in fnnames:
            if fnname not in results.messages:
                continue

            failures = results.messages[fnname]

            for testName,errorMessage in sorted(failures, key=lambda (n,s): n):
                print '='*70
                print '%s: %s'%(fnname, testName)
                print '-'*70
                print errorMessage
                print


def main():
    args = parse_args()

    try_import_functions()

    results = run_tests(args)
    print_results(results)


if __name__ == '__main__':
    main()
