#!/usr/bin/env python
try:
    import sys
#    sys.path.append("/Users/ivarne/django/Django-1.3.1")
#    sys.path.append("/Users/ivarne/django/Django-1.4")
    sys.path.append("/Users/marius/Downloads/Django-1.4")
except:
    pass


from django.core.management import execute_manager
import imp
try:
    imp.find_module('settings') # Assumed to be in the same directory.
except ImportError:
    import sys
    sys.stderr.write("Error: Can't find the file 'settings.py' in the directory containing %r. It appears you've customized things.\nYou'll have to run django-admin.py, passing it your settings module.\n" % __file__)
    sys.exit(1)

import settings

if __name__ == "__main__":
    execute_manager(settings)
