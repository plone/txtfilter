from Products.filter.config import *
from Products.filter.example.smartlink import usingRBW
from Products.Archetypes import public as atapi
from Products.Archetypes import listTypes
from Products.Archetypes.Extensions.utils import installTypes, install_subskin
from Products.Archetypes.config import REFERENCE_CATALOG
from Products.CMFCore.utils import getToolByName

from StringIO import StringIO

def configureReferenceCatalog(portal, out):
    """
    required for the ReferenceLinkFilter to work.
    """
    
    catalog = getToolByName(portal, REFERENCE_CATALOG)
    for indexName, indexType in (
        ('targetId', 'FieldIndex'),
        ('targetTitle', 'FieldIndex'),
        ('targetContentType', 'FieldIndex'),
        ('targetURL', 'FieldIndex'), ):

        try:
            catalog.addIndex(indexName, indexType, extra=None)
        except:
            pass
        try:
            catalog.addColumn(indexName)
        except:
            pass

        catalog.manage_reindexIndex(indexName)

def configureWysiwyg(portal, out):
    props = getToolByName(portal, 'portal_properties')
    if not hasattr(props, 'site_properties'): # not plone
        return
    
    editors = props.site_properties.getProperty('available_editors')
    if "Kupu" in editors:
        # move it up in the list
        editors = list(editors)
        editors.remove('Kupu')
        editors = ['Kupu',] + editors
        props.site_properties._updateProperty('available_editors', editors)

def install(self):
    """ set this up to only load """
    out=StringIO()
    typeInfo = atapi.listTypes(PROJECTNAME)

    installTypes(self, out,
                 typeInfo,
                 PROJECTNAME)

    install_subskin(self, out, GLOBALS)
    
    if usingRBW and\
           not self.portal_quickinstaller.isProductInstalled('ATReferenceBrowserWidget'):
        self.portal_quickinstaller.installProducts(['ATReferenceBrowserWidget'], stoponerror=True)
    
    configureReferenceCatalog(self, out)
    configureWysiwyg(self, out)


