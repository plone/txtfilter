===========================================
Bricolite - An Introduction to Archetypes
===========================================

:author: Benjamin Saller <bcsaller@objectrealms.net>
:date: Aug. 21th, 2004
:version: Version 1.0
:abstract: *This document is designed to guide one through both understanding this
           product as well as creating your own Archetypes based Products.*



Introduction
~~~~~~~~~~~~~

This document serves to show how one might extend the Plone Content
Management System using the Archetypes Framework. It assumes some
experience with Plone and hopefully requires next to none with
Archetypes.

The goal is that the reader be able to introduce new Products into
Plone, add Archetypes based content and attach new or specific
functionality to those types. Additionally we touch on advanced topics
from time to time.


The system we will attempt to layout is based on the
Bricolage::http://www.bricolage.cc/ Content Management
System. Bricolage does a number of things that this project won't
show, it focuses on deployment and provides some data flexibility we
don't show here. That said we offer a much improved editing
environment and out of the box usefulness.

That said we will define two new types as shown below.

.. image:: bricolite.png

The Story type is akin to an article in a magazine or a newspaper
story, the Media type is designed to hold media objects (such as
images) that appear within the story.




Step 1: Project Layout
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Typically a Zope/Plone software development project is implemented
using one or more Zope Products. A Product is a Zopeish extension to
the traditional Python notion of a package. Each Zope Product can
introduce new types of content, tools, skins, etc. to a Plone
system. Plone and Archetypes are examples of Products, as is this
package.

There is a fair amount of code required to introduce your code and
concepts to a running Plone system. Because of this and for reasons of
good general software design typical each new Zope undertaking is
implemented using a Product and each Product has a similar layout.

As an Archetypes developer it makes sense to reuse some of the
skeleton code and in order to do that we need to discuss how a project
is broken out, whats general and what is specific.


High level project overview
===========================

::

 /Project/
        /content
        /docs
        /Extensions
        /lib
        /skins/
                /projectskin
        /tests/
        /tools

        README.txt
        __init__.py
        config.py
        permissions.py
        version.txt



Descriptions of each project element follow:

content/
        Projects that introduce content types should place each
        content types implementation in a file in this directory.

doc/
        Information about installing and using your product go here

Extensions/
        The installer for your product goes here and will be used by
        the QuickInstaller product to easily add/remove your product from a
        site.

lib/
        Library level code for this project. Many projects only
        introduce skins and content types and will not need to include a lib
        directory.

skins/
        PageTemplates, Python scripts and static content (typically
        images) related to your project go into subdirectories here with names
        that make sense to you.

tests/
        Every project should include tests of new features and code
        that it introduces. Plone and Archetypes leverage powerful testing
        frameworks that make this simple to do. It speeds development and
        saves debugging time.

tools/
        If your project provides additional tools you might include
        those here.


README.txt
        Your projects letter of introduction.

__init__.py
        Includes boilerplate code that will register the project
        elements with Zope and Archetypes as needed.


config.py
        Typically I use config.py to include static definitions and
        variables that are the product of import time decisions. config.py
        should contain only immutable variables as a matter of convention.

permissions.py
        If you require additional security permissions for your new
        content or tools it is suggested you place them here

version.txt
        A simple text file containing a version string used when
        talking about the product.




Bricolite Project Specifics
===========================

Briolite mostly follows the above project layout. We will walk though
its additions and its customizations.

conf/
        Briolite makes the useful addition of a conf/ directory. This
        contains ZConfig information used to help bootstrap the
        project. While this document contains information on
        Archetypes and ZConfig is off-topic the pattern used there
        seems useful (and reuseable) enough to warrant inclusion.

The code in this directory creates an import system for other
project dependencies, if you look at depends.conf you can see that
this project requires "kupu" to be installed and will make sure that
it gets installed in the portal when Briolite is installed.

        "required" and "optional" are the two allowed keywords.

This same code and config is used to bootstrap the testing environment
with its Products as well, making sure that they get installed as
needed.


Step 2: Content
~~~~~~~~~~~~~~~

content/ contains the new content or data types that the Briolite
project exposes.

The Bricolage CMS exposes two content types, Stories which are
analogous to newspaper or magazine articles and Media which are the
other assets (typically images) related one or more stories.

These simple content types are created using the Archetypes framework,
which is a schema driven system for introducing content types into
Plone sites. A schema is simply data describing the properties and
behavior of another object.

Archetypes is based around the idea of providing simple descriptions
of new types and attaching rich behaviors to those descriptions. Lets
see how this is done.

If you look at content/story.py we can see where the Story datatype is
defined.

Lets explore this file in some detail::

 from AccessControl import ClassSecurityInfo
 from Products.Archetypes import public as atapi
 from Products.Bricolite import config as config
 from Products.CMFCore import CMFCorePermissions
 from Products.CMFCore.utils import getToolByName
 from ZODB.POSException import ConflictError

This is a fairly standard set of imports used in most project
work. The notable statements being the import of the Archetypes API as
atapi and the project specific config mentioned in the overview. Using
the atapi namespace helps some people to keep their own code more
readable and I will move to using it more consistently in the
future. I also keep the static symbols from config.py prefixed with
the config namespace.


::

 from Products.Bricolite.lib.smartlink import SmartLink, SmartLinkField

Next comes the import of library code from within this
project. Archetypes provides many features and utilities to
application and content type developers but when it does its designed
to be extended. This project will show how and the starting point
would be to take any additions you will make in your lib/ directory
and use them in your content types and tools.



The schema
==========

::

 schema = atapi.BaseSchema + \
         atapi.Schema((

This is the standard schema preamble, it says use the "BaseSchema"
which includes the interface expected by the CMF and Plone and then we
are adding new fields that will compose our type. The list of fields
follow.

.. _story_schema:

::

    SmartLinkField('body',
                   required=1,
                   searchable=1,
                   template="story_view", # used to lookup
                                          # runtime/filtering macros
                                          # and custom to this project
                   page_size_kb=5120,     # another custom prop, fed
                                          # into the pagination filter
                   default_content_type='text/html',
                   default_output_type='text/html',
                   allowable_content_types = ( 'text/html',
                                               ),
                   widget=atapi.RichWidget(label="Body",
                                           description="""This is the copy
                                           used for the story.
                                           """,
                                           rows=15,),
                   ),
    atapi.ReferenceField('assets',
                         relationship=config.MEDIA_RELATIONSHIP,
                         multiValued=True,
                         allowed_types=('Media',),
                         referenceClass=SmartLink,
                         widget=atapi.ReferenceWidget(label="Media Assets",
                                                      description="""Any media
                                                      assets referenced by the
                                                      object in this way will be
                                                      available for substitution
                                                      directly within the story
                                                      body"""),
                         ),
    ))


Looking you can see we added two field. Each field is a regular Python
object which gets used to describe the new content type. You can see
that we added something called a SmartLinkField with the name 'body'
and something something else called a ReferenceField with the name
'assets'.  Each of these have a number of properties passed in as
standard Python keyword arguments. Each of these is assumed to have
meaning to the underlying Field.

Archetypes provide field implementations for most common data types,
Strings, different types of Numbers, delimited lines of text, rich or
marked up text from a variety of sources. There are times when it
doesn't provide something with the full behavior required by your
type.

-----

When Archetypes doesn't provide the feature you require out of the box
you have two general ways to deal with this.

    1. Accessors/Mutators: Control the flow of information in and out of your content
       objects by providing custom implementations of access to fields.

    2. Custom Field/Widget implementations.


These both require some explanation. For option 1 you need to
understand that when ever an Archetypes based content object is
accessed a method called an accessor must be called.  For example, if
you have a field called 'body', the default name for the accessor
would be getBody. If you don't provide an accessor a default one will
be provided for you by the Archetypes runtime. What this means however
is that you _can_ provide your own accessor that can generate the
value for a field in any number of ways. (It important to note that
there is a mutator for every field as well that is called to store
data into the object, in the previous example this would be
'setBody').

For option 2 you might introduce a new type of Field that can be used
in your schema (anywhere in your project, and possibly in other
projects as well). This generally requires a little more upfront
thought as you are trying to abstract some new type of data concerns
or behavior into something that is reusable.

The rule of thumb for choosing the right method is simple. Application
specific business logic goes in accessors (or maybe mutators) and
anything that can be generalized should be a field or widget.

Back to the schema definition. Rather than provide a full reference to
all the properties of each different field type I will simply try to
show how this works and cite other documentation as a reference. For
example, the lines::

                 SmartLinkField('body',
                              required=1,
                              searchable=1,

This indicates that we have a SmartLinkField and it is required for
the object to be in a valid state. We also indicate that its
'searchable' which is a blanket switch for saying that general
searches of Plone's catalog should include content from this field in
its result set. Elements like 'searchable' and 'required' belong to
every field type shipped with Archetypes. The next properties in the
declaration are examples of things specific to a given field::

                   template="story_view", # used to lookup
                                          # runtime/filtering macros
                                          # and custom to this project
                   page_size_kb=5120,     # another custom prop, fed
                                          # into the pagination filter

The field API makes it very simple to add new properties that schema
authors can use to configure the behavior of fields used in their
types.


Class Definition
================

After the schema is defined we need to use a Python class to contain
our new content type::

  class Story(atapi.BaseContent):
    """A Story or Article, loosly modelled after Bricolage but
    intended to use the Kupu, 'document-centric' editing model
    """
    archetype_name = portal_type = meta_type = "Story"
    security = ClassSecurityInfo()
    schema = schema


This is the entire class. By using the Archetypes BaseContent type we
indicate that this is basically a specialized version of a content
type that is designed to fix nicely with Plone's expectations. We give
it a name, "Story", assign a security object that can be used later if
needed and associate the schema we created above with this
class. Thats it, the schema provides the behavior so you can see that
none is needed in this class.

The last line is important::

    atapi.registerType(Story)

This tells the Archetypes runtime that the new class is available and
sets it up to fix its security and supply any needed support code to
the class.



Thats it for the Story Archetype, but there is still quite a bit that
is not explained by looking at just this file. Archetypes strives to
reduce the amount of code you need to write, evolve and maintain. The
implementation files tend to avoid much of what I call "incidental
complexity", that is code and complexity that doesn't relate
specifically to the business goal. This has the consequence that you
will want to understand what the framework is doing for you where the
code doesn't clearly show due to its terseness.

Let's follow the story type in more detail and see where it leads in
the code.

References and ReferenceFields
==============================

The second element of the Story schema is a ReferenceField. References
are a standard feature that any Archetypes objects can use and take
advantage of. References allow for objects to enforce relationships to
other objects and the ReferenceField/Widget pair provide a sort of
simplified interface to this and a web form based UI. As an example we
model the relationship between a Story and its Media assets using a
Reference Field. Lets look at how this is done::

    atapi.ReferenceField('assets',
                         relationship=config.MEDIA_RELATIONSHIP,
                         multiValued=True,
                         allowed_types=('Media',),
                         referenceClass=SmartLink,
                         widget=atapi.ReferenceWidget(label="Media Assets",
                                                      description="""Any media
                                                      assets referenced by the
                                                      object in this way will be
                                                      available for substitution
                                                      directly within the story
                                                      body"""),

We assign a relationship which is a string denoting what type of
reference this might be, it only exists to group references between
objects and is driven by convention, not contract. This means you can
supply any relationship name you desire. The multiValued property
indicates if we want to model a one-to-one or a one-to-many
relationship using this reference field. The reference API itself is
always bidirectional many-to-many, so the restriction come from a
higher level construct such as the policy in the reference field. The
allowed_types property takes a list of type names that will appear in
the list of choices used by the default reference widget for display
in forms. A less common, but highly useful option is to supply a class
that will be used to create references for this field. In this case we
have requested that a project specific reference class (from
lib/smartlink.py) be used in place of the default implementation.


The result is that the object referred to have a bi-directional
relationship that tracks moves, changes, renames of the objects in
question. By being able to provide our own implementation of the
reference class we can hook behavior that does things like prohibit
deletes of referenced objects or enforce a policy of delete cascades.

If you look at lib/smartlink.py you will find the implementation of
the Reference class::

 class SmartLink(HoldingReference):
    relationship = config.MEDIA_RELATIONSHIP

    # In addition to being a normal holding reference
    # we want to track the URL of the target for easy brains based
    # linking. For this to work the reference catalog should be
    # updated to inlcude this index and metadata.
    def targetURL(self):
        target = self.getTargetObject()
        if target:
            return target.absolute_url()
        return '#'

It is a HoldingReference which is one of the default reference
subclasses provided with Archetypes, we use that classes behavior and
provide an additional method, targetURL which we expect will get
indexed and included in reference catalog searches as a function of
code not shown here (for example an install script in Extensions).

References are used to establish connections between objects, however
once those references are in place you need a way to use or consume
them. The reference field and widget pair provide a simple interface,
choose a set of objects, reference them and then a list of as
clickable links when you view your object. This is hardly a
sophisticated use, nor does exploring it shed much light on
references. To this end we introduce a new Field type, SmartLinkField
which is used by the Stories' 'body' field. This takes advantage or
references made using the reference field.


Custom Field Implementations
============================

The SmartLinkField in lib/smartlink.py relies on the behavior of the
standard Archetypes field, TextField and thus subclasses it. Supposing
that body were a regular text field in Archetypes 1.x the operations
to access the contents of this field might go as follows::

   at_instance.getBody() -> TextField.get(at_instance) -> """some
                                                       transformed
                                                       text"""


By subclassing TextField and calling its implementation we say that we
want to continue to do this work::

        value = atapi.TextField.get(self,
                                    instance,
                                    mimetype,
                                    raw,
                                    **kwargs)

We then extend it by calling other library code (from lib/filter.py)
that can 'filter' or post-process the return value. If you recall I
discussed two options for providing custom implementations, overriding
the accessor or mutator or doing a custom field implementation. I hope
you can see how this notion of context aware filtering of the date
makes sense as a more general pattern rather that something that would
appear in a Story/getBody (and anywhere else we might choose to reuse
the pattern).

If filtering were abstracted and made into a core part of Archetypes
then we would consume filters like we do validation, from a
declarative list or some other means than statically coding it it like
in this example, however::

        filter = getFilter("Reference Link")
        value = filter(instance, value)

        filter = getFilter('HTML Paginator')
        value = filter(instance, value,
                       template=self.template,
                       limit=self.page_size_kb,
                       **kwargs)

        return value

From the filtering library we gather registered filters and apply them
to the value of the TextField. This is done at runtime (as opposed to
on "set" in the mutator) so that we can take advantage of the current
system state.

-----

In lib/filter.py you can see the ReferenceLinkFilter. This will look
for certain patterns in the original text and replace them with views
of referenced objects. There are a number of ways to use the Reference
Engine and its API. The simplest is to use the IReferenceable
interface that all Archetype objects implement. This will allow you to
get all of the references from a given instance or to gather all the
object that point to it::

       at_instance.getReferences() # -> [referenced objects]
       at_instance.getBackReferences() # -> [objects pointing to this
                                             instance]


Another method for using the Reference Engine is to deal with it using
the catalog interface. This requires some understanding of how
catalogs work in Zope, but its actually quite simple::

                brains = reference_tool._queryFor(sid=instance.UID(),
                                                  tid=targetId,
                                                  relationship=self.relationship)

using the helper method _queryFor of the reference catalog we can
search for things based on their source and target uuids (sid and tid
respectively). This will return a list of brains that are the
references we are interested in. In the case of the
ReferenceLinkFilter we want to be able to change text in the form of
"${reference/id/URL}" into a runtime resolved expression. After
strings of this nature are parsed from the original text we see if the
id after the "${reference/...} is a UUID or the id of an asset
explicitly referenced by this object. In this case we are looking to
resolve media assets into useful forms for inclusion in the stories'
view.

If we found a ${reference/...} string in the text we convert it to a
ZopePageTemplate TALES expression and evaluate it. This affords us
some flexibility. By default we convert simple ${reference/id}
expressions into resolving the view for the referenced object. This
has interesting consequences as we will see when we look at the Media
Type next.


Adding Business Logic and Features to Objects
=============================================

In content/media.py you will find the media type. Its definition is a
little more complex than the Story type. The schema code follows::

 schema = atapi.BaseSchema + \
         atapi.Schema((
               atapi.FileField('contents',
                               primary=True,
                               ),

    )) + TemplateMixinSchema

 schema = schema.copy()
 schema['layout'].schemata = 'presentation'


Like with story we take the BaseSchema provided and extend it. In this
case we use a FileField which is intended for BLOB like storage where
we don't expect to be able to process the data inside directly. We
also mix in the TemplateMixinSchema from Archetypes which is intended
to allow for selection of templates on that are used for the "view"
action (on a per-instance basis). Because we are going to slightly
change the notion of what TemplateMixin does here we do some schema
post-processing to update properties for this class. The important
thing to remember here is that you must copy the schema. If you
directly modify the properties of a shared object it would otherwise
impact multiple classes.


Vocabularies
============

The class implementation does a number of things. First lets talk
about the idea of Vocabularies. Many times you will need the content
author or the user of your object to enter data selected from a
variety of choices. Sometimes this list is static and known when the
application is written, for example "Select Gender, Male, Female or
None Selected", at other times the vocabulary is only known while the
application is running. These are known as static and dynamic
vocabularies and Archetypes supports both. Typically to define a
static vocabulary we use an Archetypes utility class called
DisplayList.

A DisplayList maintains ordering or the set of options, allows for a
display value and a value that gets stored on the object. Extending
the previous example we might say::

    gender_vocab = DisplayList((
                                (None, 'None Specified'),
                               ('M', 'Male'),
                               ('F', 'Female'),
                               ))

and then in the field itself::

    StringField('gender',
                vocabulary=gender_vocab,
                widget=SelectionWidget(),
                ),

this would indicate which vocabulary we are using and we selected a
widget that will present the options. If for example we needed a
dynamic vocabulary we might change the method in the following way::

        StringField('gender',
                vocabulary="_vocab_gender",
                ...
                )

The by supplying the string '_vocab_gender' we indicate that there
will be a resolvable method of that name on the class that can be used
to generate the vocabulary at runtime, typically this method will
generate a DisplayList.

Looking back at the Media class you can see we override a method from
Archetypes/TemplateMixin.py and include our custom '_voc_templates'
method. Here we are delegating to a tool to gather a dynamic
vocabulary based on the content type of the uploaded media. We will
discuss the tool in a bit more detail later.


Defaults
========

The next method is::

     def getDefaultLayout(self):
        return self._voc_templates()[0]

which the TemplateMixinSchema uses to select a default layout, we
again want a custom implementation, we assume that if the user doesn't
supply a selected layout the first one in the vocabulary list will be
fine.


To see that this method gets triggered you need to understand how
defaults work. When an object is created a default value is supplied,
this can come from directly setting it in the schema::

     StringField('gender',
                 default=None,
                 ),

or by supplying a default method::

   StringField('gender',
                default_method="gender_default"
                )

which would then require that the object have a method with the name
"gender_default" and that supply a default value.


Views
=====

Next in the Media class is the is the __call__ method. This special
method is used in Python when an object is invoked, for example::

       at_instance()

In Zope this is used by the object publisher to invoke the view
associated with the object (actually Zope checks a number of places,
an 'index_html' method, __call__ and in cases like the CMF/Plone
'view'). By overriding this method we are allowing our code to replace
the default viewing code::

    def __call__(self):
        """return the view registered for this media object"""
        macro = self.unrestrictedTraverse(self.getLayout())
        context = createContext(self,
                                contents=self.Schema()['contents'].get(self))
        return macro_render(macro, self, context)

What we are doing here is resolving the value of our own 'getLayout'
method, this is storing the path to a macro that will be used to
render the view. This is different that what Plone normally does where
you might have a page template registered for the view of the
object. By allowing media to render itself though the use of macros we
make something that is easy to embed in another view, such as the
Story. Our Media assets are not meant to be view outside of the
stories that reference them so this model makes sense.

While this is a highly specialized view model its quite common to need
customized views of your Archetypes content. The standard way to
accomplish this is to create a specially named file and provide
override macros. Archetypes  base_view.pt which is the default view
for any type will look for a file named with the portal_type of the
content object and the postfix '_view'. For example, Story has
story_view.pt in the /skins/briolite/ directory. In this file you can
use METAL to define macros for "header", "footer" and
"body". Folderish types also have a "folderlisting" macro that can be
overridden.

This is done as follows::

    <div metal:define-macro="body">

      <div tal:replace="structure here/getBody">
        The Body -- this will have any media embedded in it.
      </div>

    </div>

This just invokes the accessor for the field we are interested in
showing as representing the document. You can also require that the
widgets that would normally be used to render a field be placed in a
certain part of a custom form as follows::


    <div metal:define-macro="body">
         <div metal:use-macro="python: here.widget('title', mode='view')"/>
         <div metal:use-macro="python: here.widget('body', mode='view')"/>
    </div>


Which would use the registered widgets to show the title and the body.


Step 3: Tests
~~~~~~~~~~~~~

Next [*]_ comes testing. The tests in Bricolite are simplistic and not
all very comprehensive but they will show how a to author and run
tests for Archetypes products. Testing is critical to the ability to
rapidly evolve projects and later to maintain them. Here I only
explain the mechanics, not the methodology.

By changing into the tests/ directory we can run the included script
that launches the testing framework::

     # python ./runalltests.py
     <snip>
     ...
     ----------------------------------------------------------------------
     Ran <n> tests in 0.723s

This should run whatever tests you have in your project and report on
their successes or failures.

Most of the files in the tests/ directory are boilerplate and simply
need to be copied. Project specific tests go into any number of files
prefix with the name "test\_". An example and the file we will discuss
is tests/test_project.py. For each component of your project that you
wish to test you may choose to introduce a "test_whatever" file. This
file will contain one or more TestCases. TestCases will be subclasses
of the ArcheSiteTestCase and ultimately Python unittest framework's
TestCase. The "hello world" of testing follows::

 class BricoliteProjectTest(ArcheSiteTestCase):
     def afterSetUp(self):
         ArcheSiteTestCase.afterSetUp(self)
         installBrico(self.portal)

     def test_installer(self):
         pass

The afterSetUp code will be triggered for each method on the TestCase
class prefixed with "test\_" and will run the normal product installer
from the Extensions/ directory::

  from Products.Bricolite.Extensions.Install import install as installBrico

Now even a simple Python "pass" statement will assert that the project
on the filesystem is installable, and the basic "well-formedness" of
the project.


Inspecting an actual test
=========================

In the content types section we speculated that Story objects should
be able to refer to Media objects directly in their content. Let's
test this assertion::

    def test_smartlink(self):
        s = makeContent(self.folder, 'story1', 'Story')
        m = makeContent(self.folder, 'media1', 'Media')

        s.setAssets([m.UID()])

        media_text = 'The media 1 reference.'
        m.setContents( media_text, mimetype="text/html")
        m.setLayout('media_views/macros/text')

        # Now rewrite the body to include a reference to the new media
        s.setBody("this is ${reference/media1}",
                  mimetype="text/html")

        # and assert that the reference resolved
        assert media_text in s.getBody()

The testing framework provides a user folder available for use in
testing and referred to as self.folder. We use this here to construct
a Media object and later a Story object. We then establish an 'assets'
reference between the Story and its media object (`see the Story
Schema`__).

Next we set a blob of text into the media object with the hopes that
it will be rendered in-line by the SmartLinkField. Then we place link
to the object in the body of the story. In the end we are able to
assert that the text found in media directly appears in the body of
the story.

This helps enable development, allows for refactoring and helps
future-proof the project.


Step 3: Tools
~~~~~~~~~~~~~

Bricolite includes a simple tool that is derived from the Archetypes
framework as well. The file tools/mediacenter.py contains the
implementation of the MediaCenter which acts as a kind of registry for
mapping mime/types to allowed views within the media object. What
distinguishes a tool in Plone and the CMF is that its an object with a
fixed known name that is intended to be addressed through Acquisition.

In /__init__.py we have to register this tool explicitly which is its
main difference from how content is handled::

    cmf_utils.ToolInit(
        "%s Tool" % config.PROJECTNAME,
        tools = (tools.MediaCenter,),
        product_name = config.PROJECTNAME,
        icon = "tool.gif",
        ).initialize( context )

Looking at the tool itself should show just how simple creating tools
with Archetypes is::

 class MediaCenter(UniqueObject, atapi.BaseContent,
                  ActionProviderBase):
    title = portal_type = meta_type = 'Media Center'
    id = config.MEDIA_CENTER
    global_allow = 0

This shows that we include UniqueObject as a Base Class which
indicates that once the id is set we don't want to alter it (as things
are looking for it by that name).

This is handled in __init__::

    def __init__(self):
        atapi.BaseContent.__init__(self, MediaCenter.id)
        self.setTitle(MediaCenter.title)

Validation
==========

The media center does do one important general thing and that is
define a custom validator. Validation is the process by which form
data is verified to be correct. In Archetypes validation is handled in
two common ways. The simplest is to declare in your Schema that some
pre-written validation routines get applied to your field::

           StringField('homepage',
                    validators = ('isURL',),
                    )

This would used the canned validation to assure that when the edit
form is submitted the value we are applying is indeed a URL. The other
method is to define a custom validator on your class. Using the
"validate\_" prefix we are able to define a method "validate_mediamap"
which is the name of the field in the schema. This method parses the
media map and returns an error if there is a problem::

    def validate_mediamap(self, value):
        result = self._parseMediaMap(value)
        if result is True:
            return None
        else:
            # This would be the error
            return result

This will use the _parseMediaMap to generate an error message
including a line number if something is wrong.

As a tool (resolvable by name) we also provide the
"getVocabByMimeType" method which will return a DisplayList from its
internal registry. This is consumed by the "_voc_templates" method of
media.py and is used as the choices for a given mime/types display.



Step 4: Library
~~~~~~~~~~~~~~~

Other minor things of interest in the project

 - The conf module bootstrapping code
 - The ploneCustom.css facade for easier per project styles
 - The weak whimpering wiki filter that can form automatic title based
   links between content.



Additional Resources
~~~~~~~~~~~~~~~~~~~~


Archetypes
           - http://plone.org/documentation/archetypes
Testing
        - http://docs.python.org/lib/module-unittest.html
        - http://zope.org/Members/shh/ZopeTestCase


.. [*] Technically this should have been step two, but for an introduction to
   Archetypes it would have been hard to talk about testing project and
   content concepts that hadn't been explained yet.

__ story_schema_


