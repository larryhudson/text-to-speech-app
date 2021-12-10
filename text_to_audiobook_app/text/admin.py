from django.contrib import admin
from . import models

# Register your models here.

admin.site.register(models.TextFile)
admin.site.register(models.Image)
admin.site.register(models.Webpage)