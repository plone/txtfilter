from zope.interface import Interface
import txtfilter.interfaces
import zope.component.zcml
import zope.app.security.fields
import zope.configuration.fields as fields
import zope.interface
import zope.schema

class IApplyTxtFilterDirective(Interface):
    class_ = fields.GlobalObject(
        title=u"Class",
        required=True
        )

    method = zope.schema.TextLine(
        title=u"The name of the method.",
        description=u"The name of the method to be decorated",
        required=True,
        default=u'',
        )
    
    txtfilters = fields.Tokens(
        title=u"Filters to be applied to this method",
        description=u"""
        a list of filters in the order they should be applied to the
        method output. If left empty, methodInstance.txtfilter will be
        checked""",
        required=False,
        value_type=fields.GlobalObject(missing_value=str()))
    
    contextInterface = fields.GlobalObject(
        title=u"Interface that context provides if context is not the method's instance",
        description=u"For AT compatibility",
        required=False
        )

    skipkeywords = fields.Tokens(
        title=u"Keywords to skip",
        description=u"list of word if found, that will cause return of unfiltered value",
        required=False,
        value_type=fields.GlobalObject(missing_value=str())
        )


class ITxtFilterDirective(zope.component.zcml.IAdapterDirective):
    """
    Register an adapter
    ===================

    mild switcheroo on the the old adapter to create super simple
    fieldfilter directive
    """
    provides = zope.configuration.fields.GlobalObject(
        title=u"Interface the component provides",
        description=u"This attribute specifes the interface the adapter instance must"\
                    u"provide.",
        required=True,
        default=txtfilter.interfaces.IFieldFilter
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
    
