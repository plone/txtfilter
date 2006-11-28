from zope.interface import Interface, Attribute
from Products.Archetypes.interfaces import IFileField
from zope.interface.common.sequence import IReadSequence

class IFilterList(IReadSequence):
    """list of txtfilters to apply"""

class IFilterDecorator(Interface):
    """ decorator for a method """

class IFilterable(Interface):
    """s
    this will later simply be applied to AT once
    AT's interfaces are sanified
    """

class IFilterField(IFileField):
    """
    An AT Text Field with assignable filtration.

    Assignment of filters is by directive
    """

class ITxtFilter(Interface):
    """Abstract Base for filters.

    Filters are the inverse of transforms.
    Transforms create new versions of the object when the object is
    set. This doesn't require runtime context.

    Filters happen during object access (rendering for example) and
    include the context the object is being run in.

    Properly filters should implement the PortalTransforms.itransforms
    interface and be used accordingly. In the future they will,
    however for the purpose of this demo they will not as that
    interface is designed around mimetype transformation which this is
    not.
    """
    
    context = Attribute('context the filter is running in')

    def filter(text, **kwargs):
        """This is the only method required by the interface, the rest
        is included so subclasses don't have to do so much lifting
        """

    def _filterCore(chunk, **kwargs):
        """This is the only method required by the interface, the rest
        is included so subclasses don't have to do so much lifting
        """

    def __call__(chunk, **kwargs):
        """Normally an alias to filter
        """

class IFieldFilter(ITxtFilter):
    """A filter that takes a field and a context"""
    
    def __init__(field, context):
        """ multiadapting here """

class EndFiltration(Exception):
    """raise to stop continuation of filtering"""
