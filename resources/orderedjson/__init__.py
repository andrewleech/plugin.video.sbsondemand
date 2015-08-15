"""
## Provides method for parsing json into an ordereddict
# Provides modules required for python2.6

## To add new py2.6 binary platform:
# Ensure python compatible toolchain is installed
# extract simplejson-3.6.5.tar.gz
# Ensure you run the same version of python used in kodi on your platform.

cd simplejson-3.6.5
python setup.py bdist_egg
cp dist/*.egg ../
cd ../
for filename in *.egg; do
 mkdir "${filename%.*}"
 unzip $filename -d "${filename%.*}"
 rm $filename
done
python __init__.py

# This will print out the identifier matches on the current system
# add a suitable identifier match -> new folder path below
# Please do contribute added distributions back to project!
"""

import os
import sys
import platform

path = None

identifier1 = (platform.system(), platform.architecture()[0]) + platform.python_version_tuple()[0:2]
identifier2 = None

if float(".".join(platform.python_version_tuple()[0:2])) > 2.6: # Newer than 2.6
    import json


else:
    ## Platform Identifiers
    identifier1_matches = {
        ('Darwin', '64bit', '2', '6')  : "simplejson-3.6.5-py2.6-macosx-10.10-intel",
        ('Windows', '32bit', '2', '6') : "simplejson-3.6.5-cp26-none-win32",
        ('Windows', '64bit', '2', '6') : "simplejson-3.6.5-cp26-none-win_amd64",
    }

    if identifier1 in identifier1_matches:
        path = os.path.join(os.path.dirname(__file__), identifier1_matches[identifier1])

    if not path:
        print "simplejson distribution not available for your platform. \nPlease add one if possible by following instructions in top of file: " + str(__file__)
    else:
        # Add required paths to python search path
        if path not in sys.path:
            sys.path.append(path)

    import simplejson as json

from ordereddict import OrderedDict


def loads(*args, **kwargs):
    kwargs["object_pairs_hook"] = OrderedDict
    return json.loads(*args, **kwargs)

if __name__ == "__main__":
    print "identifier1 = " + str(identifier1)
    if identifier2:
        print "identifier2 = " + str(identifier2)
