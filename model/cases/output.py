import unittest
from StringIO import StringIO
import sys

from decorators.timeout import TimeoutError


class IdenticalOutputTests(object):
    def _check(self, sIn, *args, **kwargs):
        sys.stdin.write(sIn)
        sys.stdin.seek(0)

        self.fSolution(*args, **kwargs)

        correct = sys.stdout.getvalue()

        sys.stdout.truncate(0)
        sys.stdin.seek(0)

        try:
            self.f(*args, **kwargs)
        except TimeoutError:
            raise
        except Exception as e:
            self.fail('Encountered exception: %r'%e)

        output = sys.stdout.getvalue()

        # Ignore leading and trailing whitespace (eg, the line at the start)
        correct = correct.strip()
        output = output.strip()

        # Try with some lenient tests
        self._failIfStrippedLinesAreDifferent(correct, output)
        self._failIfCaseIsDifferent(correct, output)

        # Finally fall back to actual test
        self.assertEqual(correct, output)

    def _stripLines(self, value):
        lines = filter(None, map(str.strip, value.splitlines()))
        valueWS = '\n'.join(lines)

        return valueWS

    def _failIfStrippedLinesAreDifferent(self, correct, output):
        """
        Fail if there is any difference between the outputs once all empty
        lines and whitespace at the start and end of each line have been
        removed.

        """
        correctWS = self._stripLines(correct)
        outputWS = self._stripLines(output)

        if correct != output and correctWS == outputWS:
            self.fail('Whitespace mismatch')

    def _failIfCaseIsDifferent(self, correct, output):
        """
        Fail if there is any difference between the outputs once all empty
        lines and whitespace at the start and end of each line have been
        removed, and there is any difference in case.

        """
        correctWS = self._stripLines(correct)
        outputWS = self._stripLines(output)

        correctCase = '\n'.join(map(str.lower, correctWS.splitlines()))
        outputCase = '\n'.join(map(str.lower, outputWS.splitlines()))

        if correct != output and correctCase == outputCase:
            self.fail('Case mismatch')


class StreamReplacingTestCase(unittest.TestCase):
    def setUp(self):
        sys.stdout, self.oldstdout = StringIO(), sys.stdout
        sys.stdin, self.oldstdin = StringIO(), sys.stdin

    def tearDown(self):
        sys.stdin = self.oldstdin
        sys.stdout = self.oldstdout
