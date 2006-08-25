from zope.app.component.interface import provideInterface
from zope.app.component.metaconfigure import adapter
from decorator import FilterDecorator

def wrapRegistration(func):
    name = 'name'
    def wrapper(*args, **kwargs):
        _context, = args,
        factory = kwargs['factory'][0] # filters should only have one
                                       # factory ever
        kwargs[name] = kwargs.get(name, getattr(factory, name))
        func(*args, **kwargs)
    return wrapper
        
txtfilter = wrapRegistration(adapter)
_method_monkies=[]
def decorateMethod(_context, class_, method,
                   skipkeywords=list(('raw', 'skip_filters')),
                   txtfilters=tuple(), contextInterface=None):
    
    def wrapMethod(class_, method, txtfilter=txtfilters,
                   skipkw=skipkeywords, contextInterface=contextInterface):
        oldmethod = getattr(class_, method)
        prename = '_prefilter_%s' %method
        setattr(class_, prename, oldmethod)
        fd = FilterDecorator(txtfilter=txtfilters, skipkw=skipkeywords,
                             contextInterface=contextInterface)
        wrapped = fd.wrapMethod(oldmethod)
        dummy = type('dummy', (object,), dict(f=wrapped))
        setattr(class_, method, dummy.f.im_func)
        _method_monkies.append((class_, method, prename))
    
    _context.action(
        discriminator = (class_, method, txtfilters),
        callable = wrapMethod,
        args = (class_, method)
        )
    
    if contextInterface:
        _context.action(
            discriminator = None,
            callable = provideInterface,
            args = (contextInterface.__module__ + '.' + contextInterface.getName(),
                    contextInterface)
            )
        
def cleanUp():
    # unmonkey!
    for class_, method, prename in _method_monkies:
        # setUp() triggers cleanups so we have to account for cleanups
        # before actual patching occurs
        if hasattr(class_, prename): 
            delattr(class_, method)
            setattr(class_, method, getattr(class_, prename))
            delattr(class_, prename)
        
from zope.testing.cleanup import addCleanUp
addCleanUp(cleanUp)
del addCleanUp
