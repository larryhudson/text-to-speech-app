from django.forms import ModelForm
from . import models

class TextFileForm(ModelForm):
    class Meta:
        model = models.TextFile
        fields = ['file', 'name', 'description']

class WebpageForm(ModelForm):
    class Meta:
        model = models.Webpage
        fields = ['name', 'url']

class ImageForm(ModelForm):
    class Meta:
        model = models.Image
        fields = ['file', 'name']