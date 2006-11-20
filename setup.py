from setuptools import setup, find_packages
import sys, os

version = '1.0.1'

setup(name='txtfilter',
      version=version,
      description="txtfilter provides generalized filtering facilities for processing text",
      long_description="""\
""",
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Zope2",
        "Framework :: Zope3",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='wicked txtfilter zope3 zope2 AT',
      author='whit',
      author_email='wicked@lists.openplans.org',
      url='http://www.openplans.org/projects/wicked/txtfilter',
      license='MIT',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['txtfilter'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
