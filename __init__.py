"""
$Id: $

filter is a framework piece that abstracts filtration out Ben Saller's Bricolite into its own product
"""
__authors__ = 'bcsaller@objectrealm.net, whit'
__docformat__ = 'restructuredtext'

from Extensions import Install
del Install
from Products.Archetypes import public as atapi
from Products.CMFCore import CMFCorePermissions
from Products.CMFCore import utils as cmf_utils
from Products.CMFCore.DirectoryView import registerDirectory

import api
import config

registerDirectory(config.SKINS_DIR, config.GLOBALS)

def initialize(context):
    import example
    
    types = atapi.listTypes(config.PROJECTNAME)

    content_types, constructors, ftis = atapi.process_types( types,
                                                             config.PROJECTNAME)
    cmf_utils.ContentInit(
        config.PROJECTNAME + ' Example Content',
        content_types      = content_types,
        permission         = CMFCorePermissions.AddPortalContent,
        extra_constructors = constructors,
        fti                = ftis,
        ).initialize(context)
