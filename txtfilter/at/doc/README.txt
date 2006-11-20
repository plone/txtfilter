========
 filter
========

filter is based on a simple system of text filtration system for the
AT TextField first introduced 'bricolite', Ben Saller's Archetypes
example product.

note: walkthrough.rst still refers to bricolite, not filter.

credits
=======

bcsaller@objectrealm.net

whit@openplans.org


Requirements
===========

* for at features: Archetypes 1.5.+

* Zope 2.10+


What does it do
===============

Currently, 'filter' provides a drop in field replacement for the
Archetypes TextField. This field allow for the registration of context
aware text filter for the output of said field.

see /example for information of registering filters and what filters
come with filter (complete documentation forthcoming).


Field Usage
-----------

if following example:

- Content using filter field must implement IFilterable

- filterfield must have property 'txtfilter' set to one or more
  registered filter names 

Filter may be registered for other interfaces than IFilterable.


Authoring custom filters
------------------------

A basic filter factory is a simple adapter factory. It may be
registered as a named adapter, or by using the 'archetypes:txtfilter'
directive.  The directive will check the factory for a 'name'
attribute, and register the factory as providing IFieldFilter.


Using the applyTxtFilter directive
----------------------------------

see 'decorator.zcml' for basic usage.

This directive decorates a method of a class so to apply txtfilters to
return values.

ex::

<configure
   xmlns:at="http://namespaces.zope.org/archetypes">
  <at:applyTxtFilter
     method="get"
     class="Products.filter.field.FilterField"
     contextInterface="Products.Archetypes.interfaces.IBaseObject"
     skipkeywords="raw
                   skip_filters"
     txtfilters="Macro Substitution Filter
                 Pagination" 
     />
</configure>

Explanation::

* method: method name.

* class: class that holds method to be decorated.

* contextInterface: if given, decorator will scan method arguments for
  object providing this interface to use as the context.  If nothing is given,
  will use instance of the decorated method as context.

* txtfilter: left blank, this will default to looking for attr
  'txtfilter' on the instance of the decorated method.

* skipkeywords: keywords to trigger nonfiltered return.defaults are
  shown here and are sufficient for basic AT cases.


Roadmap
=======

this product will be renamed 'txtfilter' by the end of this release.


License
=======

same as Archetypes



