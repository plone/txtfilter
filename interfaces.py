from zope.interface import Interface
from Products.Archetypes.interfaces.field import IFileField

class IFilterable(Interface):
    """
    this will later simply be applied to AT once
    AT's interfaces are sanified
    """

class IFilterField(IFileField):
    """
    An AT Text Field with assignable filtration.

    Assignment is by name of the filter in a sequence.
    """
    def filterGenerator(instance):
        """
        @generator of filters in sequence.
        adapts instance and yields each filter 
        """
        
    def get(instance, mimetype=None, raw=False, skip_filters=False,
            **kwargs):
        """from SmartLinkField: Do normal textfield get followed by filtering.
        Whats interesting about this is that we need to staticly
        encode this join point. The basic of the Archetypes V2 model
        is that you could attach things like a filtering aspect to
        any/all fields w/o altering their code base.

        When you think about how many filters can be registered on the
        same call this becomes an even more expressive argument for AOP.
        """

class IFieldFilter(Interface):
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
