from zope.interface import implements
from zope.component import queryAdapter
from txtfilter.interfaces import IFilterField, IFieldFilter, IFilterDecorator

_marker = object()

class FilterDecorator(object):
    implements(IFilterDecorator)
    def __init__(self, txtfilter=tuple(), skipkw=tuple(), contextInterface=None):
        self.txtfilter = txtfilter
        self.contextInterface = contextInterface
        self.skipkw=skipkw

    def yieldFilter(self, context):
        for filter_name in self.txtfilter:
            yield queryAdapter(context.aq_inner, IFieldFilter, filter_name)

    def filterValue(self, value, context, **kwargs):
        for textfilter in self.yieldFilter(context):
            try:
                value=textfilter(value, **kwargs)
            except :
                import pdb; pdb.set_trace()
        return value

    def wrapMethod(self, method):
        def wrappedmethod(*args, **kwargs):
            __name__=method.__name__
            __doc__="""%s
            -----------------
            This method is filtered. see txtfilter
            """ %method.__doc__
            value = method(*args, **kwargs)
            if [True for kw in self.skipkw if kwargs.get(kw, False)]:
                return value
            methodInstance = args[0]
            context = methodInstance
            if self.contextInterface:
                # this is a hack for AT
                context = [x for x in args[:2] \
                           if self.contextInterface.providedBy(x)]
                context = context and context[0] or _marker
                if context is _marker:
                    raise "No context for these args %r" %args
            if not self.txtfilter:
                # to support config by AT.Field
                self.txtfilter = methodInstance.txtfilter
            return self.filterValue(value, context, **kwargs)
        return wrappedmethod
    
    __call__=wrapMethod
