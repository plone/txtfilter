"""
mild switcheroo on the the old adapter to create super simple fieldfilter directive
"""
import zope.configuration.fields
import zope.interface
import zope.schema

import zope.app.security.fields
import zope.app.component.metadirectives 
import Products.filter.interfaces

class IFieldFilterDirective(zope.app.component.metadirectives.IAdapterDirective):
    """
    Register an adapter
    """

    provides = zope.configuration.fields.GlobalObject(
        title=u"Interface the component provides",
        description=u"""This attribute specifes the interface the adapter
        instance must provide.""",
        required=True,
        default=Products.filter.interfaces.IFieldFilter
        )
    
    trusted = zope.configuration.fields.Bool(
        title=u"Trusted",
        description=u"""Make the adapter a trusted adapter

        Trusted adapters have unfettered access to the objects they
        adapt.  If asked to adapt security-proxied objects, then,
        rather than getting an unproxied adapter of security-proxied
        objects, you get a security-proxied adapter of unproxied
        objects.

        This is a convenience override of normal adapter behavior
        """,
        required=False,
        default=True,
        )
    
from zope.app.component.metaconfigure import adapter 
def wrapforfilter(fx):
    name = 'name'
    def wrapper(*args, **kwargs):
        import pdb; pdb.set_trace()
        _context, factory, provides, for_ = args
        kwarg[name] = kwargs.get(name, getattr(factory, name))
        fx(*args, **kwargs)
    return wrapper
        
fieldfilter = wrapforfilter(adapter)
