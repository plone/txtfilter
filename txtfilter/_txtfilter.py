"""
$Id: $
"""
from zope.interface import implements
from interfaces import IFieldFilter

def ijoin(a,b):
    """yield a0,b0,a1,b1.. if len(a) = len(b)+1"""
    yield(a[0])
    for i in range(1,len(a)):
        yield(b[i-1])
        yield(a[i])

class Filter(object):
    """abstract base
    """
    implements(IFieldFilter)

    name = None    # required
    pattern = None

    def __init__(self, context):
        self.context = context

    def filter(self,  text, **kwargs):
        # Simple text replacement via co-op with the modules
        chunks = self.pattern.split(text)
        if len(chunks) == 1: # fastpath
            return text

        subs = []
        dynamic = chunks[1::2] # my ben, aren't you tricky..

        subs = [self._filterCore(d, **kwargs) for d in dynamic]

        # Now join the two lists (knowing that len(text) == subs+1)
        return ''.join(ijoin(chunks[::2], subs))

    __call__ = filter

    def _filterCore(self,  chunk, **kwargs):
        """Subclasses override this to provide specific impls"""
        return ''






