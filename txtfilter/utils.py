from cStringIO import StringIO
from os.path import abspath, dirname, join
from txtfilter.interfaces import IFieldFilter
from _txtfilter import ijoin

TYPEMAP = {
    # strings = True, iterables = false
    type(''):False,
    type(u''):False,
    type([]):True,
    type(()):True,
    }


DIR_PATH = abspath(dirname(__file__))
def doc_file(file):
    return join(DIR_PATH, 'doc', file)


