from Products import filter
from Testing import ZopeTestCase

pkgs = ( 'Archetypes',
         'filter' )

[ ZopeTestCase.installProduct(pkg) for pkg in pkgs ]

from Products.CMFPlone.tests import PloneTestCase
from Products.Archetypes.tests.ArchetypesTestCase import ArcheSiteTestCase

# util for making content in a container
def makeContent(container, id, portal_type, title=None):
    container.invokeFactory(id=id, type_name=portal_type)
    o = getattr(container, id)
    if title is not None:
        o.setTitle(title)
    return o

class FilterTestCase(ArcheSiteTestCase):
    """ General class for filter tests """
    
    def afterSetUp(self):
        ArcheSiteTestCase.afterSetUp(self)
        
        # install a test type here
        self.portal.portal_quickinstaller.installProducts(['filter'], stoponerror=True)
        
        # Because we add skins this needs to be called. Um... ick.
        self._refreshSkinData()
