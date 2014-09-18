from difflib import Differ
import unittest


class TestResult(unittest.TestResult):
    def __init__(self, *args, **kwargs):
        unittest.TestResult.__init__(self, *args, **kwargs)

        self.results = {}
        self.messages = {}

    def _addResult(self, test, err, wasSuccess):
        cls = test.__class__
        fnname = cls.FUNCTION_TESTED

        methodName = test.id().split('.')[-1]
        testName = getattr(cls, methodName).SIMPLE_DESCRIPTION

        if fnname not in self.results:
            self.results[fnname] = []

        self.results[fnname].append((testName, wasSuccess))

        # Grab just the error message
        if not wasSuccess:
            _,e,_ = err

            if fnname not in self.messages:
                self.messages[fnname] = []

            if fnname in ('interact', 'display_stats', 'display_weekly_stats'):
                one,_,two = str(e).partition(' != ')  # hacky as hell

                one = one.strip().strip("'").strip()
                two = two.strip().strip("'").strip()

                one = one.replace('\\n', '\n')
                two = two.replace('\\n', '\n')

                one = one.splitlines()
                two = two.splitlines()

                if max(len(one), len(two)) > 25:
                    message = 'Diff too long to display'
                else:
                    differ = Differ()
                    result = differ.compare(one, two)
                    message = '\n'.join(result)
            else:
                message = str(e)

            self.messages[fnname].append((testName, message))

    def addSuccess(self, test):
        unittest.TestResult.addSuccess(self, test)
        # shouldn't really have two args, the last could just be None on
        # success (as in this case)
        self._addResult(test, None, True)

    def addError(self, test, err):
        # Don't flood things on the recursion test
        tpe,val,tb = err

        if tb.tb_lineno > 50:
            tb = None

        err = tpe,val,tb

        unittest.TestResult.addError(self, test, err)
        self._addResult(test, err, False)

    def addFailure(self, test, err):
        unittest.TestResult.addFailure(self, test, err)
        self._addResult(test, err, False)
