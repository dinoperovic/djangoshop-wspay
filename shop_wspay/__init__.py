# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

"""
Release logic:
 1. Bump the __version__.
 2. git add shop_wspay/__init__.py
 3. git commit -m 'Bump to <version>'
 4. git push
 5. Make sure all tests pass on https://travis-ci.org/dinoperovic/djangoshop-wspay
 6. git tag <version>
 7. git push --tags
 8. python setup.py sdist
 9. twine upload dist/djangoshop-wspay-<version>.tar.gz
10. Done!
"""
__version__ = '0.1.2'
