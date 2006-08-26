"""
$Id: $
"""
from zope.component import adapts
from Products.Archetypes import public as atapi
from Products.Archetypes.debug import log as atlog
from Products.Archetypes.config import REFERENCE_CATALOG
from Products.txtfilter import config as config
from Products.CMFCore import CMFCorePermissions
from Products.CMFCore.utils import getToolByName, _getViewFor
from ZODB.POSException import ConflictError

from Products.txtfilter.utils import macro_render, createContext, ijoin
from Products.PageTemplates.Expressions import PathExpr, getEngine

from zope.interface import implements
from interfaces import IFieldFilter, IMacroFilter

import re

TALESEngine = getEngine()

from Products.txtfilter.interfaces import IFilterable

class Filter(object):
    """abstract base class for filters
    """
    implements(IFieldFilter)
    adapts(IFilterable)
    
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


class MacroSubstitutionFilter(Filter):
    name = "Macro Substitution Filter"

    # This looks for $$key$$ in the text and replaces it
    pattern = re.compile('\$\$(\w+)\$\$')
    
    def _macro_renderer(self,  macro, template=None, **kw):
        """render approved macros"""
        try:
            if not template:
                view = _getViewFor(self.context)
                macro = view.macros[macro]
            else:
                template = self.context.restrictedTraverse(path=template)
                macro = template.macros[macro]
        except ConflictError:
            raise
        except:
            import traceback
            traceback.print_exc()
            return ''

        econtext = createContext(self.context, **kw)
        return macro_render(macro, self.context, econtext, **kw)


    def _filterCore(self,  macro, template, **kwargs):
        """ in the macro filter, all chunks are macros """
        return self._macro_renderer(macro, template=template, **kwargs)


class ReferenceLinkFilter(Filter):
    """designed to be used in HTML, implements a simple strategy for
    doing TALES like expressions on references of a given relationship

    example:
    <a href="${reference/id/URL}">${reference/id/Title}</a>

    we mangle the expression (to make it simpler for the user)
    in the following way
    id in these examples becomes "reference" in the evaluation context
    Title and URL are resolved and available
    here is the tricky part, to make this work, the
    "${reference/foo/xxx}" really becomes ${xxx}
    so that /Title referes to the Title of the reference
    automatically.
    If you need the reference object directly you can say
    ${reference/id/getTargetObject/xxx}
    """

    name = "Reference Link"
    pattern = re.compile('\${reference/([^}]+?)}')
    relationship = config.LINK_RELATIONSHIP

    def _filterCore(self,  chunk, **kwargs):
        # Obtain the id of the reference from the expression
        parts =  chunk.split('/', 1)
        targetId = parts[:1]
        expr = parts[1:]
        if targetId:
            targetId = targetId[0]
            # resolve references for this id and relationship
            reference_tool = getToolByName(self.context,
                                           REFERENCE_CATALOG)
            # We employ two strategies here.
            # look for the targetId as a UID (this is the most
            # flexible form as it allow even the object to be renamed)
            brains = reference_tool._queryFor(sid=self.context.UID(),
                                              tid=targetId,
                                              relationship=self.relationship)
            if not brains:
                # look for targetId as an Id ( this is more common on
                # smaller sites with hand coded HTML)
                brains = reference_tool._queryFor(sid=self.context.UID(),
                                                  targetId=targetId,
                                                  relationship=self.relationship)

            if not brains:
                # if there were no results we can't do anything
                atlog('''Link Resolution Problem: %s references
                             missing object with id (%s)''' % (
                    self.context.getId(), targetId))
                return chunk
            elif len(brains) > 1:
                # there should only be one, however, its possible that
                # referenced objects could share an id (not a UUID). In
                # this unlikely event we issue a warning and use the first
                atlog('''Link Resolution Problem: %s references
                             more than one object with the same id (%s)''' % (
                    self.context.getId(), targetId))
                brains = (brains[0],)


        # Generate a TALES Expression from chunk
        if expr:
            expr = expr[0]
        else:
            expr = "reference/getTargetObject"

        expression = PathExpr('reference', expr, TALESEngine)

        # brains is still in context, we can use it to generate the
        # default context, remember, this points to the "reference
        # object", not the targetObject itself.
        brain  = brains[0]
        refobj = brain.getObject()

        # some of this information is not in the default referernce
        # object. To get this to appear and be used here we need to
        # update the ref catalog and use a new relationship that
        # inlcudes this information as the referenceClass.
        # Extensions/Install/configureReferenceCatalog shows this
        econtext = createContext(self.context,
                                reference=refobj,
                                Title=brain.targetTitle,
                                URL=brain.targetURL,
                                )
        # and evaluate the expression
        result = expression(econtext)
        if callable(result):
            result = result()
        return result

class PaginatingFilter(Filter):
    """
    Pagination,
      'its not more professional, but you can show more ads'(tm)

    designed to be used in HTML

    parses text breaking it into pages. this example is more complex
    that the last in that it needs both information from the request
    (what page are we looking for) and to provide information to the
    template for the purpose for rendering prev/next page links.

    The parser itself is not that sophisticated. Pagination to a fixed
    sized page when including such things as table layout and images
    becomes extremely complex. luckly we are not doing real
    typesetting here and are only showing the concept. :)
    """

    name = "HTML Paginator"

    SIZE_LIMIT = 4096
    SIGNIFICANT_TAGS = ['P', 'DIV', 'TABLE', ]
    BREAK_BEFORE = ['<h1', '<h2', '<h3', '<h4', '<h6', '<h6', '<hr']

    END_TAGS = ['</%s>' % i for i in SIGNIFICANT_TAGS]
    END_RE = re.compile('(?i)%s' %( '|'.join(END_TAGS + BREAK_BEFORE)))
    UNBREAKABLE_RE = re.compile('(?i)<table|<ul|<ol|<dl')
    UNBREAKABLE_CLOSE_RE = re.compile('(?i)</table>|</ul>|</ol>|</dl>')

    def chunkpage(self, text, limit=SIZE_LIMIT):
        pages = []
        para = self.findHTMLChunks(text)
        para = list(para)
        current = []
        for p in para:
            cpage = ''.join(current)
            clen = len(cpage)

            if clen > limit:
                pages.append(cpage)
                current = []

            current.append(p)

        return pages


    def findHTMLChunks(self, text):
        """
        yield a stream of chunks of devisible text
        the page breaker can use these

        we can not count on \n and the like to mean much in HTML, we need
        close tags
        """
        start = 0
        end = len(text)
        end_re = self.END_RE

        unbreakable_re = self.UNBREAKABLE_RE
        unbreakable_close_re = self.UNBREAKABLE_CLOSE_RE

        while 1:
            match = end_re.search(text, start)
            if match:
                # the only real sin would be to break a table or a list
                # we should scan for open tags within this
                # chunk, if we find one, we have to expand the search
                chunk = text[start:match.end()]
                tm = unbreakable_re.search(chunk)
                if tm:
                    tm = unbreakable_close_re.search(chunk)
                    if not tm:
                        tm = unbreakable_close_re.search(text, start)
                        if tm:
                            match = tm
                            chunk = text[start:match.end()]
                        # else we just keep the old match, it was
                        # broken HTML anyway
                yield chunk
                start = match.end()
            else:
                yield text[start:]
                break


    def filter(self,  text, **kwargs):
        page = kwargs.get('page')
        if not page:
            page = self.context.REQUEST.get('page', 1)
        page = int(page)
        if page == 0: page = 1 # non-geek counting

        pages = self.chunkpage(text, limit=int(kwargs.get('limit', self.SIZE_LIMIT)))
        # if we couldn't parse it or they indicated they want everything
        if not pages or page == -1:
            # we couldn't do anything?
            return text

        page -= 1
        if page > len(pages) or page < 0:
            page = 0
        p = pages[page]

        # we should now have the relevant page text, but we want to
        # include some additional information in the output that can
        # be used to page among these things
        if kwargs.get('template'):
            data = {
                'pages'   : len(pages),
                'current' : page + 1,
                'prev'    : max(page, 1),
                'next'    : min(page + 2, len(pages)),
                }
            econtext = createContext(self.context,
                                    **data)

            # reuse some of the macro code to render the "pages" macro
            # and insert a pager into the resultant text
            template = self.context.restrictedTraverse(path=kwargs.get('template'))
            if template:
                macro = template.macros['pages']
                text = macro_render(macro, self.context, econtext)
                p = p + text
        return p

    __call__ = filter

class WeakWikiFilter(Filter):
    ## This just showns another type of Wiki-like dynamic filtering
    ## transforms BumpyWords into links of something with that title
    ## exists in the portal_catalog

    name = "Weak Wiki Filter"
    pattern = re.compile('([A-Z][a-z]+[A-Z]\w+)')

    def _filterCore(self,  chunk, **kwargs):
        pc = self.context.portal_catalog
        brains = pc(Title=chunk)

        # lets only handle unique matches
        if brains and len(brains) == 1:
            url = brains[0].getURL()
            # build a context and render a macro for the link
            # (again, to keep things flexible)
            data = {
                'url' : url,
                'anchor' : chunk,
                }
            
            econtext = createContext(self.context,
                                    **data)

            # reuse some of the macro code to render the "wikilink" macro
            # and insert a stylized link into the output
            template = self.context.restrictedTraverse(path=kwargs.get('template'))
            if template:
                macro = template.macros['wikilink']
                return macro_render(macro, self.context, econtext)

        return chunk

__all__=('Filter', 'WeakWikiFilter', 'PaginatingFilter', 'ReferenceLinkFilter', 'MacroSubstitutionFilter')



