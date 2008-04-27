from zope.interface import Interface
import txtfilter.interfaces
import zope.component.zcml
import zope.configuration.fields as fields
import zope.interface
import zope.schema
from txtfilter.interfaces import IFilterList


class NewLineTokens(fields.Tokens):
    """ token field that splits on newline not space """
    
    def fromUnicode(self, u):
        u = u.strip()
        if u:
            vt = self.value_type.bind(self.context)
            values = []
            for s in u.split('\\n'):
                try:
                    v = vt.fromUnicode(s)
                except schema.ValidationError, v:
                    raise InvalidToken("%s in %s" % (v, u))
                else:
                    values.append(v)
        else:
            values = []

        self.validate(values)
        return values


class IFilterOutputDirective(Interface):
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

    skipkeywords = fields.Tokens(
        title=u"Keywords to skip",
        description=u"list of word if found, that will cause return of unfiltered value",
        required=False,
        value_type=fields.GlobalObject(missing_value=str())
        )
    
    txtfilter = NewLineTokens(
        title=u"Filters to be applied to this method",
        description=u"""
        a list of filters in the order they should be applied to the
        method output. If left empty, arguments  will be
        adapted to filter list interface to get a list""",
        required=False,
        value_type=zope.schema.TextLine(missing_value=str()))

    interface = fields.GlobalObject(
        title=u"interface providing names of filters",
        required=True,
        default=IFilterList
        )

    arguments = fields.Tokens(
        title=u"Arguments to be adapted",
        description=u"""
        Which arguments hold the object used to dispatch filters. Order is
        significant.
        """,
        required=False,
        value_type=zope.schema.TextLine(missing_value=str()))

#setattr(IFilterOutputDirective, 'adapted-arguments', adapted)
    
##     contextInterface = fields.GlobalObject(
##         title=u"Interface that context provides if context is not the method's instance",
##         description=u"For AT compatibility",
##         required=False
##         )


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
    
