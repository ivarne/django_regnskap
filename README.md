
Django regnskap
===============

### List of dependencies:

Installable using easy_install:
django version 1.8  # Later versions will not work
openpyxl    # to enable Excel export
dropbox     # for dropbox upload and make security copies of files
mathplotlib # for making graphs
reportlab   # for generating PDF files
MySQL-python# for mysql drivers
django-extensions # for JSONField

you can also run

```
pip install -r requirements.txt
```

### Configure database settings etc.

* copy local_settings.py.dist to local_settings.py and insert your local settings (Database, apiKeys...)

Then it should behave as a normal django app:)

### Pythonanywhere.com

To run on pythonanywhere.com you need to set ut WSGI and create a virtual envirement to install packages.

Se how in [documentation/run on pythonanywhere.com/README.md](documentation/run on pythonanywhere.com/README.txt)


