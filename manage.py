#!/usr/bin/env python
#try:
#    import sys
#    sys.path.append("/Users/ivarne/django/Django-1.3.1")
#    sys.path.append("/Users/ivarne/django/Django-1.4")
#    sys.path.append("/Users/ivarne/django/Django-1.4/django")
#except:
#    pass

#!/usr/bin/env python
import os
import sys
sys.path.append("/Users/ivarne/django")

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "django_regnskap.settings")

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)