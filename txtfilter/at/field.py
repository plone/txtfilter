"""
shamelessly derived from ben's smartlink

$Id:$
"""

__authors__ = 'Benjamin Saller <bcsaller@objectrealms.net>'
__docformat__ = 'restructuredtext'

from Products.Archetypes import public as atapi

class FilterField(atapi.TextField):
    """A bare field for demonstration"""
    _properties = atapi.TextField._properties.copy()


