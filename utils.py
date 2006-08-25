from TAL.TALInterpreter import TALInterpreter
from Products.CMFCore.utils import getToolByName
from Products.PageTemplates.Expressions import SecureModuleImporter
from Products.PageTemplates.Expressions import getEngine
from os.path import abspath, dirname, join
from cStringIO import StringIO

from Products.filter.interfaces import IFieldFilter

TYPEMAP = {
    # strings = True, iterables = false
    type(''):False,
    type(u''):False,
    type([]):True,
    type(()):True,
    }

## TAL Magic
def macro_render(macro, aq_ob, context, **kwargs):
    assert macro, """No macro was provided"""
    buffer = StringIO()
    TALInterpreter(macro, {}, context, buffer)()
    return buffer.getvalue()

def createContext(object, **kwargs):
    '''
    An expression context provides names for TALES expressions.
    '''
    pm = getToolByName(object, 'portal_membership')
    if pm.isAnonymousUser():
        member = None
    else:
        member = pm.getAuthenticatedMember()

    data = {
        'context'     : object,
        'here'        : object,
        'nothing':      None,
        'request':      getattr(object, 'REQUEST', None ),
        'modules':      SecureModuleImporter,
        'member':       member,
        }
    data.update(kwargs)
    return getEngine().getContext(data)

def ijoin(a,b):
    """yield a0,b0,a1,b1.. if len(a) = len(b)+1"""
    yield(a[0])
    for i in range(1,len(a)):
        yield(b[i-1])
        yield(a[i])

DIR_PATH = abspath(dirname(__file__))
def doc_file(file):
    return join(DIR_PATH, 'doc', file)

from Products.filter import filter as filters

def providedFieldFilters():
    klasses = [getattr(filters, klass) for klass in filters.__all__]
    available_filters = [klass.name for klass in klasses if klass.name] 
    return available_filters
