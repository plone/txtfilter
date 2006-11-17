"""
shamelessly derived from ben's smartlink

$Id:$
"""

__authors__ = 'Benjamin Saller <bcsaller@objectrealms.net>'
__docformat__ = 'restructuredtext'

from Products.Archetypes import public as atapi
from Products.filter.interfaces import IFilterField
from zope.interface import implements

class FilterField(atapi.TextField):
    _properties = atapi.TextField._properties.copy()
    _properties.update({
        'txtfilter':tuple(),
        })

