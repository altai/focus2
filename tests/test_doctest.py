
import doctest
from focus2.utils import pagination, search, views

def load_tests(loader_, tests, ignore_):
    for m in (pagination, search, views):
        tests.addTests(doctest.DocTestSuite(m))
    return tests

