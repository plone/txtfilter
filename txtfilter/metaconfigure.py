from txtfilter.interfaces import IFilterField, IFieldFilter, IFilterList
from txtfilter.interfaces import IFilterDecorator, EndFiltration
from zope.component import queryMultiAdapter, queryAdapter
from zope.interface import implements
import inspect as ins

try:
    from zope.component.interface import provideInterface
    from zope.component.zcml import adapter
except ImportError:
    from zope.app.component.interface import provideInterface
    from zope.app.component.metaconfigure import adapter

_marker = object()

class FilterDecorator(object):
    implements(IFilterDecorator)
    name = u''
    
    def __init__(self, txtfilter=tuple(), skipkw=tuple(), interface=None, arguments=tuple()):
        self.txtfilter = txtfilter
        self.interface = interface
        self.arguments = arguments
        self.skipkw=skipkw
        if len(arguments)>1: 
            self.queryAdapter = queryMultiAdapter

    def queryAdapter(self, obj, interface, name):
        if isinstance(obj, tuple) or isinstance(obj, list):
            obj = obj[0]
        return queryAdapter(obj, interface, name)
    
    def yield_filter(self, obj, txtfilter):
        for filter_name in txtfilter:
            yield self.queryAdapter(obj, IFieldFilter, filter_name)

    def determine_filters(self, obj, name=u''):
        txtfilters = []
        if self.txtfilter:
            txtfilters.extend(self.txtfilter)
        else:
            ifilters = self.queryAdapter(obj, self.interface, name)
            if ifilters:
                txtfilters.extend(ifilters)
        return txtfilters

    def do_filter(self, value, obj, name=u'', **kwargs):
        txtfilters = self.determine_filters(obj, name=name)
        for txtfilter in self.yield_filter(obj, txtfilters):
            try:
                # @@ eventually, value should be an updated reference
                # rather than an assignment
                value=txtfilter(value, **kwargs)
            except EndFiltration:
                break
        return value

    def wrap_method(self, method):
        def wrappedmethod(*args, **kwargs):
            __name__=method.__name__
            __doc__="""%s
            -----------------
            This method is filtered. see txtfilter
            """ %method.__doc__
            value = method(*args, **kwargs)
            if [True for kw in self.skipkw if kwargs.get(kw, False)]:
                return value

            objects = list()
            if self.arguments:
                argspec = ins.getargspec(method)[0]
                for arg in self.arguments:
                    objects.append(args[argspec.index(arg)])
            else:
                objects.append(args[0])
            return self.do_filter(value, objects, self.name, **kwargs)
        return wrappedmethod
    
    __call__=wrap_method

_method_monkies=[]
def decorateMethod(_context, class_, method,
                   skipkeywords=list(('raw', 'skip_filters')),
                   txtfilter=tuple(), interface=None, arguments=None):
    def wrap_method(class_, method, txtfilter=txtfilter,
                   skipkw=skipkeywords, interface=interface, arguments=arguments):
        oldmethod = getattr(class_, method)
        prename = '_pre_txtfilter_%s' %method
        if not hasattr(class_, prename):
            setattr(class_, prename, oldmethod)
            fd = FilterDecorator(txtfilter=txtfilter, skipkw=skipkeywords,
                                 interface=interface, arguments=arguments)
            wrapped = fd.wrap_method(oldmethod)
            dummy = type('dummy', (object,), dict(f=wrapped))
            setattr(class_, method, dummy.f.im_func)
            _method_monkies.append((class_, method, prename))
        else:
            oldkw = list(oldmethod.skipkw)
            oldkw.extend(kw for kw in skipkeywords \
                         if kw not in oldmethod.skipkw)
            oldmethod.skipkw=tuple(oldkw)
            oldmethod.arguments = oldmethod.arguments + arguments
    
    _context.action(
        discriminator = (class_, method, tuple(txtfilter)),
        callable = wrap_method,
        args = (class_, method)
        )
    
    if interface:
        _context.action(
            discriminator = None,
            callable = provideInterface,
            args = (interface.__module__ + '.' + interface.getName(),
                    interface)
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

def wrap_registration(func):
    name = 'name'
    def wrapper(*args, **kwargs):
        _context, = args,
        factory = kwargs['factory'][0] # filters should only have one
                                       # factory ever
        kwargs[name] = kwargs.get(name, getattr(factory, name))
        func(*args, **kwargs)
    return wrapper
        
txtfilter = wrap_registration(adapter)


