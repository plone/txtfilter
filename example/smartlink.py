__authors__ = 'bcsaller, brcwhit'
__docformat__ = 'restructuredtext'

from Products.Archetypes.TemplateMixin import TemplateMixin, TemplateMixinSchema
from Products.Archetypes import public as atapi
from Products.filter import config 
from Products.filter import api  
from Products.filter import utils

try:
    import Products.ATReferenceBrowserWidget.ATReferenceBrowserWidget as rbw
    refwidget = rbw.ReferenceBrowserWidget
    usingRBW=True
except :
    usingRBW=False
    refwidget = atapi.ReferenceWidget

available_filters = api.getRegistry().getAvailableFilters()

schema = atapi.BaseSchema.copy() + atapi.Schema((
        api.FilterField( "body",
                         required=1,
                         searchable=1,
                         template='smartlink_doc_view',
                         filter=available_filters,
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
                             referenceClass=api.EmbeddedContentReference,
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

class Smartlink(TemplateMixin, atapi.BaseContent):
    """
    Basic frankenstenized example for test suite
    and exhibition of filtration
    """

    portal_type=meta_type='Smartlink'
    archetype_name='filter ex'
    
    schema = schema

    def __call__(self):
        """return the view registered for this media object"""
        macro = self.unrestrictedTraverse(self.getLayout())
        context = utils.createContext(self,
                                      contents=self.Schema()['body'].get(self))
        return utils.macro_render(macro, self, context)
    
atapi.registerType(Smartlink, config.PROJECTNAME)
