#!/usr/bin/env python

from distutils.core import setup

setup(name='SbsOnDemand',
      version='0.0.20120228',
      author='Michael van der Kolff',
      author_email='mvanderkolff@gmail.com',
      url='https://github.com/mvanderkolff/sbsOnDemand',
      packages=['SbsOnDemand'],
      scripts=['scripts/sbs-downloader-ondemand'],
      description='Sbs (Australian TV Network) On-Demand downloader library',
      license='GPL 3.0',
     )
