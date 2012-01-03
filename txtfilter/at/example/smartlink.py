"""
this example may be getting dated ;) 2005/12/12

see bottom for CA bits
"""

__authors__ = 'bcsaller'
__docformat__ = 'restructuredtext'

from Products.Archetypes import public as atapi
from Products.Archetypes.TemplateMixin import TemplateMixin, TemplateMixinSchema
from txtfilter.at import field, config
from txtfilter.at.example._txtfilter import providedFieldFilters
from txtfilter.interfaces import IFilterable, IFilterList, IFilterField
from zope.interface import implements, implementer
from zope.component import adapter
from Products.Archetypes.references import HoldingReference

try:
    import Products.ATReferenceBrowserWidget.ATReferenceBrowserWidget as rbw
    refwidget = rbw.ReferenceBrowserWidget
    usingRBW=True
except :
    usingRBW=False
    refwidget = atapi.ReferenceWidget

try:
    from Products.ATReferenceBrowserWidget import ATReferenceBrowserWidget as rbw
    refwidget = rbw.ReferenceBrowserWidget
    usingRBW=True
except ImportError:
    usingRBW=False
    refwidget = atapi.ReferenceWidget


class EmbeddedContentReference(HoldingReference):
    relationship = config.LINK_RELATIONSHIP
    # In addition to being a normal holding reference
    # we want to track the URL of the target for easy brains based
    # linking. For this to work the reference catalog should be
    # updated to inlcude this index and metadata.
    def targetURL(self):
        target = self.getTargetObject()
        if target:
            return target.absolute_url()
        return '#'

    def targetContentType(self):
        target = self.getTargetObject()
        if target:
            return target.getContentType()
        return 'application/octet'


class Smartlink(TemplateMixin, atapi.BaseContent):
    """
    Basic frankenstenized example for test suite
    and exhibition of filtration
    """
    implements(IFilterable)
    portal_type=meta_type='Smartlink'
    archetype_name='filter ex'
    schema = atapi.BaseSchema.copy() + atapi.Schema((
        field.FilterField( "body",
                           required=1,
                           searchable=1,
                           template='smartlink_doc_view',
                           primary=True,
                           page_size_kb=4096,
                           default_content_type='text/html',
                           default_output_type='text/html',
                           widget=atapi.RichWidget( label="Body",
                                                    description="This should be an explanation of how to use this field. see ben's walkthrough for Bricolite for now",
                                                    rows=15 ),
                           allowable_content_types=( 'text/html',
                                                     'text/x-rst',
                                                     )

                           ),

        atapi.ReferenceField('embedded_content',
                             relationship=config.LINK_RELATIONSHIP,
                             multiValued=True,
                             mutator="setEmbeddedContent",
                             allowed_types=('Smartlink',),
                             referenceClass=EmbeddedContentReference,
                             widget=refwidget( label="Doc Assets",
                                               description="""Any
                                               media assets referenced
                                               by the object in this
                                               way will be available
                                               for substitution
                                               directly within the
                                               doc body using the
                                               ${reference/id}
                                               notation with the value
                                               found in parentheses.
                                               """,
                                               ),
                             ),

        )) + TemplateMixinSchema.copy()

    schema['layout'].schemata = 'presentation'

atapi.registerType(Smartlink, config.PROJECTNAME)

# txtfilters lists for application may be declared in three way:
# 1. by 'txtfilter' in the filter-output directive
# 2. by an explicit interface for 'interface' in the filter-output
#    directive
# 3. by creating an adapter for your type(s) to IFilterList

# this is an unsophisticated version that returns all the example
# filters

@implementer(IFilterList)
@adapter(IFilterField, IFilterable)
def filter_list(field, context):
    return providedFieldFilters()









