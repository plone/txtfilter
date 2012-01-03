"""
@@ remove rest of bricolite specific content and add test content
"""
import os, sys
import unittest
from sets import Set
import traceback

from txtfilter.utils import doc_file
from txtfilter.at.example import Smartlink

import txtfilter.at.config
from Products.PloneTestCase import ptc

# util for making content in a container
def makeContent(container, id, portal_type, title=None):
    container.invokeFactory(id=id, type_name=portal_type)
    o = getattr(container, id)
    if title is not None:
        o.setTitle(title)
    return o

ptc.setupPloneSite(products=['txtfilter.at'])

# our example type
portal_type = Smartlink.portal_type

class FilterTest(ptc.PloneTestCase):

    def afterSetUp(self):
        super(ptc.PloneTestCase, self).afterSetUp()
        # Because we add skins this needs to be called. Um... ick.
        self._refreshSkinData()
        self.loginAsPortalOwner()

    def test_chunksingleton(self):
        c1 = makeContent(self.folder, 'content1', portal_type, 'ContentOne')
        c1.Schema()['body'].filter='Weak Wiki Filter'
        c1.setBody("BumpyWord",
                   mimetype="text/html")

    def test_pagination(self):
        content = makeContent(self.folder, 'content', portal_type)
        # load in a document to use as body/text
        body = file(doc_file('walkthrough.rst'), 'r').read()
        content.setBody(body, mimetype="text/x-rst")
        content.Schema()['body'].filter="HTML Paginator"

        res = content.getBody()
        res2 = content.getBody(page=2)
        assert len(res) < len(body) and res != res2, """Doesn't seem to have gotten the proper pages"""

    def test_referencelink(self):
        content = makeContent(self.folder, 'content', portal_type)
        u2 = makeContent(self.folder, 'content2', portal_type)

        content.setEmbeddedContent([u2.UID()])
        content.Schema()['body'].filter='Reference Link'

        referred_text = 'The content2 reference.'
        u2.setBody( referred_text, mimetype="text/html")
        u2.setLayout('reflink_views/macros/text')

        # Now rewrite the body to include a reference to the new media
        content.setBody("this is ${reference/content2}",
                    mimetype="text/html")

        body = content.getBody()

        # and assert that the reference resolved
        assert referred_text in body

    def test_weakwiki(self):
        c1 = makeContent(self.folder, 'content1', portal_type, 'ContentOne')
        c1.Schema()['body'].filter='Weak Wiki Filter'
        c2 = makeContent(self.folder, 'content2', portal_type, 'BumpyWord')

        # force a reindexing to pick up the title...
        c2.reindexObject()

        # Create a BumpyWord that should become a link
        c1.setBody("find a link to BumpyWord",
                   mimetype="text/html")

        # try a singleton
        c1.setBody("BumpyWord",
                   mimetype="text/html")

        body = c1.getBody(template='smartlink_view')
        assert c2.absolute_url() in body


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(FilterTest))
    return suite

