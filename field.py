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

from Products.filter.interfaces import IFieldFilter, IFilterField

from utils import TYPEMAP
from zope.app import zapi
from zope.interface import implements
from zope.component.exceptions import ComponentLookupError

class FilterField(atapi.TextField):
    #implements(IFilterField)
    
    _properties = atapi.TextField._properties.copy()
    _properties.update({
        'filter':tuple(),
        })

    security  = ClassSecurityInfo()

    def filterGenerator(self, instance):
        filters = self.filter
        if not TYPEMAP[type(self.filter)]:
            filters = (self.filter,)
            
        for filter_name in filters:
            try:
                yield zapi.getAdapter(instance.aq_inner, IFieldFilter, filter_name)
            except ComponentLookupError:
                # no CA available
                # this should be made switchable
                # as to not improper mask config errors
                pass

    def get(self, instance, mimetype=None,
            raw=False, skip_filters=False, **kwargs):

        value = super(FilterField, self).get(instance, mimetype,
                                             raw,
                                             **kwargs)
        if raw or skip_filters:
            return value

        for textfilter in self.filterGenerator(instance):
            value=textfilter(value, **kwargs)

        return value


