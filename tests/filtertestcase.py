import traceback as tb
from Testing import ZopeTestCase
from Products.PloneTestCase import ptc
# should ztc load CA? I mean, when are you
# really testing units in zope2

pkgs = ( 'Archetypes',
         'txtfilter' )

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

class ZCMLLoad(object):
    zcml = zcml
    def __init__(self, pkg):
        self.clear()
        self.pkg = pkg
        
    def clear(self):
        self._loaded={}
        self._load_order=[]
        
    def load(self, name='configure.zcml', warn=True):
        if not self._loaded.get(name, False):
            try:
                self.zcml.load_config(name, self.pkg)
            except :
                if warn:
                    print "\n %s\n ----------------- \n %s \n" %(name, tb.print_exc())
            self._loaded[name] = True
            self._load_order.append(name)
            return True
        return False

    def loadmeta(self):
        return self.load('meta.zcml')
    
import Products.Five
import Products.txtfilter
import Products.txtfilter.example
fivezcml = ZCMLLoad(Products.Five)
filterzcml = ZCMLLoad(Products.txtfilter)
examplezcml = ZCMLLoad(Products.txtfilter.example)

# at conf must proceed filter
from Products import txtfilter

def setupCA():
    tearDown()
    setUp()
    fivezcml.loadmeta()
    fivezcml.load('permissions.zcml')
    
    examplezcml.load()
    [loader.clear() for loader in fivezcml, \
     filterzcml, examplezcml,]
    
ptc.setupPloneSite(products=['txtfilter'], required_zcml=setupCA)

class FilterTestCase(ArcheSiteTestCase):
    """ General class for filter tests """

    def afterSetUp(self):
        super(ArcheSiteTestCase, self).afterSetUp()
        setupCA()
        # Because we add skins this needs to be called. Um... ick.
        self._refreshSkinData()

    def beforeTearDown(self):
        tearDown()
