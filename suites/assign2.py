#!/usr/bin/env python

import unittest

from config import cfg, modules
from decorators.classes import apply_to_test_case_methods
from decorators.definition import fail_if_undefined
from decorators.functions import raise_if_called, UnexpectedCallError
from decorators.output import fail_if_print
from decorators.replacement import replace
from decorators.timeout import fail_if_timeout
from decorators.utility import simple_description, tests_function
from suites.support.assign2 import get_data_for_date as mocked_gdfd


## Some globals
# Should be limited purely to preserve sanity
ARRAYS_SHORTER = ['a', 'b', 'c']
ARRAYS_LONGER = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l']


@apply_to_test_case_methods(fail_if_print)
@apply_to_test_case_methods(fail_if_timeout(1))
@apply_to_test_case_methods(fail_if_undefined(modules.SCRIPT, 'PVData'))
@apply_to_test_case_methods(replace('get_data_for_date', mocked_gdfd))
@tests_function('PVData (task sheet examples)')
class PVDataTaskSheetTests(unittest.TestCase):
    def setUp(self):
        self.pvd = modules.SCRIPT.PVData()
        self.pvd.change_date('13-09-2014')

    @simple_description('change date')
    def testChangeDate(self):
        date = self.pvd.get_date()
        self.assertEqual(date, '13-09-2014')

    @simple_description('get time')
    def testGetTime(self):
        time = self.pvd.get_time(300)
        self.assertEqual(time, '10:00')

    @simple_description('get sunlight')
    def testGetSunlight(self):
        sunlight = self.pvd.get_sunlight()
        expected = [252.7, 252.7, 216.3, 216.3]

        self.assertEqual(sunlight[300:304], expected)

    @simple_description('get temperature')
    def testGetTemperature(self):
        temperature = self.pvd.get_temperature()
        expected = [22.0, 22.0, 21.5, 21.5]

        self.assertEqual(temperature[300:304], expected)

    @simple_description('get power, UQ Centre')
    def testGetPowerUQCentre(self):
        power = self.pvd.get_power('UQ Centre, St Lucia')
        expected = [80495, 74765, 68285, 65250]

        self.assertEqual(power[300:304], expected)

    @simple_description('get power, All Arrays Combined')
    def testGetPowerAllArraysCombined(self):
        power = self.pvd.get_power('All Arrays Combined')
        expected = [288155, 270165, 248465, 239472]

        self.assertEqual(power[300:304], expected)

    @simple_description('no exception handling')
    def testNoExceptionHandling(self):
        with self.assertRaises(ValueError):
            self.pvd.change_date('banana')


class PVDataTestSetup(unittest.TestCase):
    def setUp(self):
        self.scriptPVD = scriptPVD = modules.SCRIPT.PVData()
        self.solutionPVD = solutionPVD = modules.SOLUTION.PVData()

        def applyToPVDs(f):
            f(scriptPVD)
            f(solutionPVD)

        self.applyToPVDs = applyToPVDs

        def check(f):
            self.assertEqual(f(solutionPVD), f(scriptPVD))

        self.check = check



@apply_to_test_case_methods(fail_if_print)
@apply_to_test_case_methods(fail_if_timeout(1))
@apply_to_test_case_methods(fail_if_undefined(modules.SCRIPT, 'PVData'))
@apply_to_test_case_methods(replace('get_data_for_date', mocked_gdfd))
@tests_function('PVData')
class PVDataAdvancedTests(PVDataTestSetup):
    @simple_description('change date twice')
    def testChangeDateTwice(self):
        self.applyToPVDs(lambda pvd: pvd.change_date('01-01-2014'))
        self.check(lambda pvd: pvd.get_date())

        self.applyToPVDs(lambda pvd: pvd.change_date('02-02-2014'))
        self.check(lambda pvd: pvd.get_date())

    @simple_description('initialises to yesterday')
    def testYesterday(self):
        # will have initialised in setUp; just check they have the same date
        self.check(lambda pvd: pvd.get_date())

    def _checkDateIsCached(self, initialDate, newDate):
        self.scriptPVD.change_date(initialDate)

        @replace('get_data_for_date', raise_if_called)
        def f():
            self.scriptPVD.change_date(newDate)

        try:
            f()
        except UnexpectedCallError:
            self.fail('Reloaded data for identical date pair (%s, %s)'%(
                initialDate, newDate))

    @simple_description('caches identical date')
    def testCachesIdenticalDate(self):
        date = '03-04-2014'
        self._checkDateIsCached(date, date)

    @simple_description('caches d-m-yyyy, dd-mm-yyyy')
    def testCachesSimilarDate(self):
        self._checkDateIsCached('03-04-2014', '3-4-2014')

    @simple_description('caches dd-m-yyyy, d-mm-yyyy')
    def testCachesAnnoyingDate(self):
        self._checkDateIsCached('03-4-2014', '3-04-2014')


@apply_to_test_case_methods(fail_if_print)
@apply_to_test_case_methods(fail_if_timeout(1))
@apply_to_test_case_methods(fail_if_undefined(modules.SCRIPT, 'PVData'))
@apply_to_test_case_methods(replace('get_data_for_date', mocked_gdfd))
@tests_function('PVData')
class PVDataArraySizeTests(PVDataTestSetup):
    @simple_description('change date once')
    def testChangeDateOnce(self):
        self.applyToPVDs(lambda pvd: pvd.change_date('01-01-2014'))
        self.check(lambda pvd: pvd.get_date())


def suite():
    loader = unittest.TestLoader()

    staticTestClasses = [
            PVDataTaskSheetTests,
            PVDataAdvancedTests,
        ]

    arraySizeTestClasses = [
            PVDataArraySizeTests,
        ]

    if cfg.masters:
        pass

    # Apply tests with shorter and longer arrays
    def copy_class(cls):
        class AhemThisIsACopy(cls):
            pass
        return AhemThisIsACopy

    def add_annotation(annotation):
        def f(cls):
            cls.FUNCTION_TESTED += ' (%s)'%annotation
            return cls

        return f

    fShorter = apply_to_test_case_methods(replace('ARRAYS', ARRAYS_SHORTER))
    shorterTestClasses = map(fShorter, map(copy_class, arraySizeTestClasses))
    shorterTestClasses = map(add_annotation('less arrays'), shorterTestClasses)

    fLonger = apply_to_test_case_methods(replace('ARRAYS', ARRAYS_LONGER))
    longerTestClasses = map(fLonger, map(copy_class, arraySizeTestClasses))
    longerTestClasses = map(add_annotation('more arrays'), longerTestClasses)

    # Add
    testClasses = staticTestClasses + shorterTestClasses + longerTestClasses

    testsToRun = map(loader.loadTestsFromTestCase, testClasses)
    suite = unittest.TestSuite(testsToRun)

    return suite
