from Extensions import Install
del Install
from Products.Archetypes import public as atapi
from Products.CMFCore import permissions as CMFCorePermissions
from Products.CMFCore import utils as cmf_utils
from Products.CMFCore.DirectoryView import registerDirectory

import config

registerDirectory(config.SKINS_DIR, config.GLOBALS)

def initialize(context):
    import example
    types = atapi.listTypes(config.PROJECTNAME)

    content_types, constructors, ftis = atapi.process_types(types,
                                                                config.PROJECTNAME)
    cmf_utils.ContentInit(
        config.PROJECTNAME + ' Example Content',
        content_types      = content_types,
        permission         = CMFCorePermissions.AddPortalContent,
        extra_constructors = constructors,
        fti                = ftis,
        ).initialize(context)
