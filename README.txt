===========
 txtfilter
===========

`txtfilter` provides a basic framework for filtering text. It was
derived from Ben Saller's bricolite example product.

A txtfilter is a named adapter that implements IFieldFilter and adapts
IFilterable.  These adapters may be run individually or as a
pipeline(see field.FilterField).


Highlights
==========

txtfilter.field.FilterField
---------------------------

   A drop-in replacement for the archetypes TextField.  Add one
   additional property: filters, an iterable returning names of filters.

txtfilter.filter
----------------

   Abstract class Filter forms the basis for 3 filters:
   ReferenceLinkFilter, PaginatingFilter,
   WeakWikiFilter

txtfilter.example
-----------------

   An example content type that uses the field and all filters

txtfilter.interfaces
--------------------

   Documentation on api.


Credits
=======

Ben Saller <bcsaller@objectrealms.net>: concept, original code

Whit Morriss <whit@openplans.org>: maintenance, repackaging



License
=======

see doc/LICENSE.txt

