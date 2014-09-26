import random
import unittest

from cases.output import IdenticalOutputTests, StreamReplacingTestCase
from config import cfg, modules
from decorators.definition import fail_if_undefined
from decorators.functions import raise_if_called
from decorators.output import fail_if_print
from decorators.replacement import replace
from decorators.timeout import fail_if_timeout, TimeoutError
from decorators.utility import simple_description, tests_function

# Pre-define some useful data sets
# These are used with the basic functions (we use randomised ones where
# interaction is required)
trim = lambda data: [(ti,te,s,arr[-4:]) for (ti,te,s,arr) in data]
ARRAYS_TRIMMED = modules.SUPPORT.ARRAYS[-4:]

DATA_EMPTY = []
ARRAYS_EMPTY = []

DATA_SINGLE = [('05:00', 11.9, 0., (0, 0, 0, 0, 0, 0, 0, 21, 30))]
DATA_SINGLE_TRIMMED = trim(DATA_SINGLE)

DATA_SINGLE_NEGATIVE_TEMP = [('05:00', -15., 0., (0, 0, 0, 0, 0, 0, 0, 21, 30))]

DATA_MULTIPLE = [
        ('11:40', 14.4, 580.5, 
            (247760, 6760, 196850, 193300, 44760, 10404, 61100, 18748, 62155)),
        ('11:41', 14.4, 580.5,
            (247905, 6760, 196450, 193650, 44640, 10416, 62800, 18764, 61887)),
        ('11:42', 13.9, 581.0,
            (248165, 6720, 196600, 194050, 44640, 10440, 62900, 18820, 62440)),
        ('11:43', 13.9, 581.0,
            (246360, 6720, 196750, 194250, 44700, 10464, 62700, 18750, 62506)),
        ('11:44', 13.9, 581.0,
            (248115, 6680, 196700, 193850, 44820, 10476, 62750, 18725, 62464)),
    ]
DATA_MULTIPLE_TRIMMED = trim(DATA_MULTIPLE)

DATA_MULTIPLE_SINGLE_HOTTEST = DATA_MULTIPLE[1:]
DATA_MULTIPLE_NON_CONSECUTIVE_HOTTEST = DATA_MULTIPLE[1:] + [DATA_MULTIPLE[0]]

DATA_MAX_TEMP_IN_OTHER_POS = [
        ('11:40', 30, 580.5, 
            (247760, 6760, 196850, 193300, 44760, 10404, 61100, 18748, 62155)),
        ('11:41', 14.4, 30,
            (247905, 6760, 196450, 193650, 44640, 10416, 62800, 18764, 61887)),
    ]

RESULT_STRING_SINGLE_LINE = '05:00,9.0,0.0,0,0,0,0,0,0,0,19,33\n'
RESULT_STRING_TWO_LINES = '05:00,9.0,0.0,0,0,0,0,0,0,0,19,33\n' \
        '05:01,9.0,0.0,0,0,0,0,0,0,0,19,30\n'

RESULT_STRING_SINGLE_LINE_TRIMMED = '05:00,9.0,0.0,0,0,19,33\n'
RESULT_STRING_TWO_LINES_TRIMMED = '05:00,9.0,0.0,0,0,19,33\n' \
        '05:01,9.0,0.0,0,0,19,30\n'

POSSIBLE_MAX_RESULTS = [
        '1,2\n3,4\n',
        '1,2\n',
        '1,2\n3,4\n5,6\n',
        '7,8\n9,10\n',
    ]


# Define actual test cases
# Should probably have these in another file, but eh
@tests_function('load_data')
class LoadDataTests(unittest.TestCase):
    @simple_description('does not handle ValueError')
    @fail_if_print
    @fail_if_timeout(1)
    @fail_if_undefined(modules.SCRIPT, 'load_data')
    def testRaisesValueError(self):
        with self.assertRaises(ValueError):
            modules.SCRIPT.load_data('hello')

    @fail_if_print
    @fail_if_timeout(1)
    @fail_if_undefined(modules.SCRIPT, 'load_data')
    @replace('get_max_data', raise_if_called)
    def _check(self, s, expected):
        # Easier to create a local function to reuse the decorator
        @replace('get_data_for_date', lambda date: s)
        def fn(s):
            return modules.SCRIPT.load_data(s)

        try:
            result = fn(s)
        except TimeoutError:
            raise
        except Exception as e:
            self.fail('Encountered exception: %r'%e)

        self.assertEqual(result, expected)

    @simple_description('single line')
    def testSingleLine(self):
        expected = [('05:00', 9.0, 0.0, (0, 0, 0, 0, 0, 0, 0, 19, 33))]

        self._check(RESULT_STRING_SINGLE_LINE, expected)

    @simple_description('multiple lines')
    def testMultipleLines(self):
        expected = [
                ('05:00', 9.0, 0.0, (0, 0, 0, 0, 0, 0, 0, 19, 33)),
                ('05:01', 9.0, 0.0, (0, 0, 0, 0, 0, 0, 0, 19, 30)),
            ]

        self._check(RESULT_STRING_TWO_LINES, expected)

    @simple_description('single line, different number of arrays')
    @replace('ARRAYS', ARRAYS_TRIMMED)
    def testSingleLineTrimmed(self):
        expected = [('05:00', 9.0, 0.0, (0, 0, 19, 33))]

        self._check(RESULT_STRING_SINGLE_LINE_TRIMMED, expected)

    @simple_description('multiple lines, different number of arrays')
    @replace('ARRAYS', ARRAYS_TRIMMED)
    def testMultipleLinesDifferentNumberOfArrays(self):
        expected = [
                ('05:00', 9.0, 0.0, (0, 0, 19, 33)),
                ('05:01', 9.0, 0.0, (0, 0, 19, 30)),
            ]

        self._check(RESULT_STRING_TWO_LINES_TRIMMED, expected)

    @simple_description('doesn\'t assume trailing newline')
    def testWithTrailingNewline(self):
        expected = [
                ('05:00', 9.0, 0.0, (0, 0, 0, 0, 0, 0, 0, 19, 33)),
                ('05:01', 9.0, 0.0, (0, 0, 0, 0, 0, 0, 0, 19, 30)),
            ]

        self._check(RESULT_STRING_TWO_LINES.strip(), expected)


@tests_function('max_temperature')
class MaxTemperatureTests(unittest.TestCase):
    @fail_if_print
    @fail_if_timeout(1)
    @fail_if_undefined(modules.SCRIPT, 'max_temperature')
    @replace('get_max_data', raise_if_called)
    @replace('get_data_for_date', raise_if_called)
    def _check(self, data, expected):
        try:
            result = modules.SCRIPT.max_temperature(data)
        except TimeoutError:
            raise
        except Exception as e:
            self.fail('Encountered exception: %r'%e)

        self.assertEqual(result, expected)

    @simple_description('single row')
    def testSingleRow(self):
        expected = (11.9, ['05:00'])
        self._check(DATA_SINGLE, expected)

    @simple_description('multiple rows, single time')
    def testMultipleRowsWithSingleTimeAtMaxTemperature(self):
        expected = (14.4, ['11:41'])
        self._check(DATA_MULTIPLE_SINGLE_HOTTEST, expected)

    @simple_description('multiple rows, multiple times, consecutive')
    def testMultipleRowsWithMultipleConsecutiveTimesAtMaxTemperature(self):
        expected = (14.4, ['11:40', '11:41'])
        self._check(DATA_MULTIPLE, expected)

    @simple_description('multiple rows, multiple times, not consecutive')
    def testMultipleRowsWithMultipleNonConsecutiveTimesAtMaxTemperature(self):
        expected = (14.4, ['11:41', '11:40'])  # NB: assuming order
        self._check(DATA_MULTIPLE_NON_CONSECUTIVE_HOTTEST, expected)

    @simple_description('negative temperature')
    def testWithNegativeTemperature(self):
        expected = (-15., ['05:00'])
        self._check(DATA_SINGLE_NEGATIVE_TEMP, expected)

    @simple_description('correctly identify times at max temperature')
    def testWithMaxInIntensityPosition(self):
        expected = (30, ['11:40'])
        self._check(DATA_MAX_TEMP_IN_OTHER_POS, expected)


@tests_function('total_energy')
class TotalEnergyTests(unittest.TestCase):
    @fail_if_print
    @fail_if_timeout(1)
    @fail_if_undefined(modules.SCRIPT, 'total_energy')
    @replace('get_max_data', raise_if_called)
    @replace('get_data_for_date', raise_if_called)
    def _check(self, data, expected):
        try:
            result = modules.SCRIPT.total_energy(data)
        except TimeoutError:
            raise
        except Exception as e:
            self.fail('Encountered exception: %r'%e)

        self.assertEqual(result, expected)

    @simple_description('empty data')
    def testEmpty(self):
        expected = 0.
        self._check(DATA_EMPTY, expected)

    @simple_description('single row')
    def testSingleRow(self):
        expected = 51/60e3
        self._check(DATA_SINGLE, expected)

    @simple_description('single row, different number of arrays')
    @replace('ARRAYS', ARRAYS_TRIMMED)
    def testSingleRowTrimmed(self):
        expected = 51/60e3
        self._check(DATA_SINGLE_TRIMMED, expected)

    @simple_description('multiple rows')
    def testMultipleRows(self):
        expected = 4217664/60e3
        self._check(DATA_MULTIPLE, expected)

    @simple_description('multiple rows, different number of arrays')
    @replace('ARRAYS', ARRAYS_TRIMMED)
    def testMultipleRowsTrimmed(self):
        expected = 769709/60e3
        self._check(DATA_MULTIPLE_TRIMMED, expected)


@tests_function('max_power')
class MaxPowerTests(unittest.TestCase):
    @fail_if_print
    @fail_if_timeout(1)
    @fail_if_undefined(modules.SCRIPT, 'max_power')
    @replace('get_max_data', raise_if_called)
    @replace('get_data_for_date', raise_if_called)
    def _check(self, data, expected):
        try:
            result = modules.SCRIPT.max_power(data)
        except TimeoutError:
            raise
        except Exception as e:
            self.fail('Encountered exception: %r'%e)

        self.assertEqual(result, expected)

    @simple_description('empty data')
    @replace('ARRAYS', ARRAYS_EMPTY)
    def testEmpty(self):
        expected = []
        self._check(DATA_EMPTY, expected)

    @simple_description('single row')
    def testSingleRow(self):
        expected = [
                ('UQ Centre, St Lucia', 0.0),
                ('Concentrating Array', 0.0),
                ('Multi Level Car Park #1', 0.0),
                ('Multi Level Car Park #2', 0.0),
                ('Sir Llew Edwards Bld.', 0.0),
                ('Prentice Building', 0.0),
                ('Advanced Engineering Bld.', 0.0),
                ('Learning Innovation Bld.', 0.021),
                ('Global Change Institute', 0.03),
            ]
        self._check(DATA_SINGLE, expected)

    @simple_description('single row, different number of arrays')
    @replace('ARRAYS', ARRAYS_TRIMMED)
    def testSingleRowTrimmed(self):
        expected = [
                ('Prentice Building', 0.0),
                ('Advanced Engineering Bld.', 0.0),
                ('Learning Innovation Bld.', 0.021),
                ('Global Change Institute', 0.03),
            ]

        self._check(DATA_SINGLE_TRIMMED, expected)

    @simple_description('multiple rows')
    def testMultipleRows(self):
        expected = [
                ('UQ Centre, St Lucia', 248.165),
                ('Concentrating Array', 6.76),
                ('Multi Level Car Park #1', 196.85),
                ('Multi Level Car Park #2', 194.25),
                ('Sir Llew Edwards Bld.', 44.82),
                ('Prentice Building', 10.476),
                ('Advanced Engineering Bld.', 62.9),
                ('Learning Innovation Bld.', 18.82),
                ('Global Change Institute', 62.506),
            ]

        self._check(DATA_MULTIPLE, expected)

    @simple_description('multiple rows, different number of arrays')
    @replace('ARRAYS', ARRAYS_TRIMMED)
    def testMultipleRowsTrimmed(self):
        expected = [
                ('Prentice Building', 10.476),
                ('Advanced Engineering Bld.', 62.9),
                ('Learning Innovation Bld.', 18.82),
                ('Global Change Institute', 62.506),
            ]

        self._check(DATA_MULTIPLE_TRIMMED, expected)


@tests_function('display_stats')
class DisplayStatsTests(StreamReplacingTestCase, IdenticalOutputTests):
    def setUp(self):
        StreamReplacingTestCase.setUp(self)

        self.fSolution = modules.SOLUTION.display_stats
        self.f = modules.SCRIPT.display_stats

    @fail_if_timeout(1)
    @fail_if_undefined(modules.SCRIPT, 'display_stats')
    def _check(self, sIn, webResult):
        @replace('get_data_for_date', lambda date: webResult)
        def fn(sIn):
            IdenticalOutputTests._check(self, sIn, 'DATE :)')

        fn(sIn)

    @simple_description('single line')
    def testSingleLine(self):
        self._check('', RESULT_STRING_SINGLE_LINE)

    @simple_description('multiple lines')
    def testMultipleLines(self):
        self._check('', RESULT_STRING_TWO_LINES)

    @simple_description('single line, different number of arrays')
    @replace('ARRAYS', ARRAYS_TRIMMED)
    def testSingleLineTrimmed(self):
        self._check('', RESULT_STRING_SINGLE_LINE_TRIMMED)

    @simple_description('multiple lines, different number of arrays')
    @replace('ARRAYS', ARRAYS_TRIMMED)
    def testMultipleLinesTrimmed(self):
        self._check('', RESULT_STRING_TWO_LINES_TRIMMED)


# We generate some random weekly results
# As they're all the same format, it doesn't really matter what the values are
def get_random_results_max(date, cache={}):
    if date not in cache:
        data = [date, random.random()*40, random.random()*1000] \
                + [random.randint(0, 10e6) for _ in modules.SUPPORT.ARRAYS]
        cache[date] = ','.join(map(str, data))

    return cache[date]


def get_random_results_date(date, cache={}):
    if date not in cache:
        entries = []

        for n in range(random.randint(1, 50)):
            data = ['01:%02d'%n, random.random()*40, random.random()*1000] \
                    + [random.randint(0, 10e6) for _ in modules.SUPPORT.ARRAYS]
            entries.append(','.join(map(str, data)))

        cache[date] = '\n'.join(entries) + '\n'

    return cache[date]


@tests_function('display_weekly_stats')
class DisplayWeeklyStatsTests(StreamReplacingTestCase, IdenticalOutputTests):
    def setUp(self):
        StreamReplacingTestCase.setUp(self)

        self.fSolution = modules.SOLUTION.display_weekly_stats
        self.f = modules.SCRIPT.display_weekly_stats

    @fail_if_timeout(1)
    @fail_if_undefined(modules.SCRIPT, 'display_weekly_stats')
    @replace('get_max_data', get_random_results_max)
    def _check(self, sIn, date):
        IdenticalOutputTests._check(self, sIn, date)

    @simple_description('january')
    def testJanuary(self):
        self._check('', '01-01-2014')

    @simple_description('july')
    def testJuly(self):
        self._check('', '01-07-2014')


fDate = lambda date: 'date %s\n'%date
fWeek = lambda date: 'week %s\n'%date
fInvalid = lambda blah: '%s\n'%blah
fQuit = lambda : 'q\n'


@tests_function('interact')
class InteractTests(StreamReplacingTestCase, IdenticalOutputTests):
    def setUp(self):
        StreamReplacingTestCase.setUp(self)

        self.fSolution = modules.SOLUTION.interact
        self.f = modules.SCRIPT.interact

    @fail_if_timeout(1)
    @fail_if_undefined(modules.SCRIPT, 'interact')
    @replace('get_data_for_date', get_random_results_date)
    @replace('get_max_data', get_random_results_max)
    def _check(self, sIn):
        IdenticalOutputTests._check(self, sIn)

    @simple_description('immediate quit')
    def testImmediateQuit(self):
        s = fQuit()
        self._check(s)

    @simple_description('single command')
    def testSingleCommandThenQuit(self):
        s = fDate('01-07-2014') + fQuit()
        self._check(s)

    @simple_description('date without leading zero')
    def testDateWithoutLeadingZero(self):
        s = fDate('1-7-2014') + fQuit()
        self._check(s)

    @simple_description('two commands')
    def testTwoCommandsThenQuit(self):
        s = fDate('01-07-2014') + fDate('02-07-2014') + fQuit()
        self._check(s)

    @simple_description('invalid command')
    def testInvalidCommandThenQuit(self):
        s = fInvalid('hello arg') + fQuit()
        self._check(s)

    @simple_description('invalid command, then valid command')
    def testInvalidCommandThenValidCommandThenQuit(self):
        s = fInvalid('hello arg') + fDate('01-07-2014') + fQuit()
        self._check(s)

    @simple_description('valid command, then invalid command')
    def testValidCommandThenInvalidCommandThenQuit(self):
        s = fDate('01-07-2014') + fInvalid('hello arg') + fQuit()
        self._check(s)

    @simple_description('valid date command without leading zeros')
    def testValidDateCommandWithoutLeadingZeros(self):
        s = fDate('1-7-2014') + fInvalid('hello arg') + fQuit()
        self._check(s)

    @simple_description('invalid command starting with d')
    def testInvalidCommandStartingWithD(self):
        s = fInvalid('daNOPE man') + fQuit()
        self._check(s)

    @simple_description('date <space> is invalid')
    def testDateSpaceIsInvalid(self):
        s = fInvalid('date ') + fQuit()
        self._check(s)

    @simple_description('invalid command with single token')
    def testInvalidCommandWithSingleToken(self):
        s = fInvalid('hi') + fQuit()
        self._check(s)

    @simple_description('invalid command with date in it')
    def testInvalidCommandContainingDate(self):
        s = fInvalid('nota date') + fQuit()
        self._check(s)

    @simple_description('invalid command with three arguments')
    def testInvalidCommandWithThreeArguments(self):
        s = fInvalid('one two three') + fQuit()
        self._check(s)

    @simple_description('invalid date command with three arguments')
    def testInvalidDateCommandWithThreeArguments(self):
        s = fInvalid('date two three') + fQuit()
        self._check(s)

    @simple_description('invalid empty command')
    def testEmptyCommand(self):
        s = fInvalid('') + fQuit()
        self._check(s)

    @simple_description('invalid quit command')
    def testInvalidQuitCommand(self):
        s = fInvalid('quit') + fQuit()
        self._check(s)

    @simple_description('invalid quit command with arg')
    def testInvalidQuitCommandWithArg(self):
        s = fInvalid('q nope') + fQuit()
        self._check(s)

    @simple_description('interact does not appear to be recursive')
    def testIfRecursive(self):
        s = fInvalid('invalid')*1250 + fQuit()
        self._check(s)

    @simple_description('masters: single command')
    @unittest.skipUnless(cfg.masters, 'Not a masters student')
    def testSingleMastersCommandThenQuit(self):
        s = fWeek('01-07-2014') + fQuit()
        self._check(s)

    @simple_description('masters: two commands')
    @unittest.skipUnless(cfg.masters, 'Not a masters student')
    def testTwoMastersCommandsThenQuit(self):
        s = fWeek('01-07-2014') + fWeek('01-06-2014') + fQuit()
        self._check(s)

    @simple_description('masters: mixed normal and masters commands')
    @unittest.skipUnless(cfg.masters, 'Not a masters student')
    def testMixedMastersCommandsThenQuit(self):
        s = fWeek('01-07-2014') + fDate('01-06-2014') + fQuit()
        self._check(s)

    @simple_description('masters: invalid week command with three args')
    @unittest.skipUnless(cfg.masters, 'Not a masters student')
    def testMastersInvalidWeekCommand(self):
        s = fInvalid('week one two') + fQuit()
        self._check(s)


def suite():
    loader = unittest.TestLoader()

    testsToRun = [
            loader.loadTestsFromTestCase(LoadDataTests),
            loader.loadTestsFromTestCase(MaxTemperatureTests),
            loader.loadTestsFromTestCase(TotalEnergyTests),
            loader.loadTestsFromTestCase(MaxPowerTests),
            loader.loadTestsFromTestCase(DisplayStatsTests),
            loader.loadTestsFromTestCase(InteractTests),
        ]

    if cfg.masters:
        testsToRun.extend([
                loader.loadTestsFromTestCase(DisplayWeeklyStatsTests),
            ])

    suite = unittest.TestSuite(testsToRun)

    return suite
