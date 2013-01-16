from setuptools import setup, find_packages
import os

version = '0.2dev'

setup(name='plomino.leaflet',
      version=version,
      description="Leaflet/Plomino integration",
      long_description=open("README.rst").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from
      # http://pypi.python.org/pypi?:action=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        ],
      keywords='Plomino,leaflet',
      author='Eric BREHAULT',
      author_email='eric.brehault@makina-corpus.org',
      url='https://github.com/plomino/plomino.leaflet',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['plomino'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'Products.CMFPlomino',
          'collective.js.leaflet',
      ],
      entry_points="""
      # -*- Entry points: -*-

      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
