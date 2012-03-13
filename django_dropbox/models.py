# -*- coding: utf-8 -*-
from django.db import models

from django.contrib.auth.models import User

class DropboxExtra(models.Model):
    user = models.OneToOneField(User,related_name="django_dropbox")
    dropbox_token = models.CharField(max_length=256)