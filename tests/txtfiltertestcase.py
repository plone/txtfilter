import traceback as tb
from Testing import ZopeTestCase
from Products.PloneTestCase import ptc
# should ztc load CA? I mean, when are you
# really testing units in zope2

pkgs = ( 'Archetypes',
         'txtfilter' )

[ ptc.installProduct(pkg) for pkg in pkgs ] 

from Products.Archetypes.tests.ArchetypesTestCase import ArcheSiteTestCase

# util for making content in a container
def makeContent(container, id, portal_type, title=None):
    container.invokeFactory(id=id, type_name=portal_type)
    o = getattr(container, id)
    if title is not None:
        o.setTitle(title)
    return o
    
# at conf must proceed filter
from Products import txtfilter

ptc.setupPloneSite(products=['txtfilter'])

class FilterTestCase(ArcheSiteTestCase):
    """ General class for filter tests """

    def afterSetUp(self):
        super(ArcheSiteTestCase, self).afterSetUp()
        # Because we add skins this needs to be called. Um... ick.
        self._refreshSkinData()

