"""
shamelessly derived from ben's smartlink

$Id:$
"""

__authors__ = 'Benjamin Saller <bcsaller@objectrealms.net>'
__docformat__ = 'restructuredtext'

from Products.Archetypes import public as atapi
from Products.CMFCore import CMFCorePermissions
from Products.CMFCore.utils import getToolByName
from ZODB.POSException import ConflictError
from AccessControl import ClassSecurityInfo

from Products.filter.api import getFilter

from utils import TYPEMAP

class FilterField(atapi.TextField):
    """
    A smartlink field with assignable filtration.

    Assignment is by name of the filter in a sequence.

    """
    
    __implements__ = atapi.TextField.__implements__
    _properties = atapi.TextField._properties.copy()
    _properties.update({
        'filter':tuple(),
        })

    security  = ClassSecurityInfo()
    
    def filterGenerator(self, filters):
        for filter_name in filters:
            yield getFilter(filter_name) 

    def get(self, instance, mimetype=None, raw=False, skip_filters=False,
            **kwargs):
        """from SmartLinkField: Do normal textfield get followed by filtering.
        Whats interesting about this is that we need to staticly
        encode this join point. The basic of the Archetypes V2 model
        is that you could attach things like a filtering aspect to
        any/all fields w/o altering their code base.

        When you think about how many filters can be registered on the
        same call this becomes an even more expressive argument for AOP.
        """
        value = atapi.TextField.get(self,
                                    instance,
                                    mimetype,
                                    raw,
                                    **kwargs)

        if raw or skip_filters: return value

        filters = self.filter

        if not TYPEMAP[type(self.filter)]:
            filters = (self.filter,)

        for filter in self.filterGenerator(filters):
            value=filter(instance, value, **kwargs)

        return value


