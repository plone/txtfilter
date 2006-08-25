import Products.filter.config
from Testing import ZopeTestCase
from Products.PloneTestCase import ptc

Products.filter.config.INSTALL_TYPES=True

pkgs = ( 'Archetypes',
         'filter' )

[ ptc.installProduct(pkg) for pkg in pkgs ] 

from Testing.ZopeTestCase.placeless import zcml, setUp, tearDown
from Products.Archetypes.tests.ArchetypesTestCase import ArcheSiteTestCase

# util for making content in a container
def makeContent(container, id, portal_type, title=None):
    container.invokeFactory(id=id, type_name=portal_type)
    o = getattr(container, id)
    if title is not None:
        o.setTitle(title)
    return o
    
import Products.Five
import Products.filter
import Products.filter.example

# at conf must proceed filter
from Products import filter
load = zcml.load_config
def setUpCA():
    setUp()
    load('meta.zcml', Products.Five)
    load('meta.zcml', Products.filter)
    load('permissions.zcml', Products.Five)
    load('configure.zcml', Products.filter)
    load('configure.zcml', Products.filter.example)
    
ptc.setupPloneSite(products=['filter'], required_zcml=setUpCA)

class FilterTestCase(ArcheSiteTestCase):
    """ General class for filter tests """

    setUpCA=staticmethod(setUpCA)
    
    def afterSetUp(self):
        super(ArcheSiteTestCase, self).afterSetUp()
        self.setUpCA()
        # Because we add skins this needs to be called. Um... ick.
        self._refreshSkinData()


    def beforeTearDown(self):
        tearDown()
