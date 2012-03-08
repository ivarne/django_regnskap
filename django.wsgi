import os
import sys

os.environ['DJANGO_SETTINGS_MODULE'] = 'django_regnskap.settings'

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()

path = '/storage/regnskap'
if path not in sys.path:
    sys.path.append(path)
