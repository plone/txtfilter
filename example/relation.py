from Products.Archetypes.references import HoldingReference
from Products.txtfilter.config import LINK_RELATIONSHIP

class EmbeddedContentReference(HoldingReference):
    relationship = LINK_RELATIONSHIP

    # In addition to being a normal holding reference
    # we want to track the URL of the target for easy brains based
    # linking. For this to work the reference catalog should be
    # updated to inlcude this index and metadata.
    def targetURL(self):
        target = self.getTargetObject()
        if target:
            return target.absolute_url()
        return '#'

    def targetContentType(self):
        target = self.getTargetObject()
        if target:
            return target.getContentType()
        return 'application/octet'
