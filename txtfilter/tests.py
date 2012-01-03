import unittest
from zope.testing import doctest

def test_suite():
    from Testing.ZopeTestCase import ZopeDocFileSuite
    from collective.testing.layer import ZCMLLayer
    suite = ZopeDocFileSuite('README.txt',
                             package="txtfilter",
                             optionflags = doctest.REPORT_ONLY_FIRST_FAILURE | doctest.ELLIPSIS
                             )
    suite.layer = ZCMLLayer
    directives = ZopeDocFileSuite('directives.txt',
                             package="txtfilter",
                             optionflags = doctest.REPORT_ONLY_FIRST_FAILURE | doctest.ELLIPSIS
                             )
    return unittest.TestSuite((suite, directives))


