from django.contrib.syndication.views import Feed
from django.urls import reverse
from .models import TextFile
import os
from decouple import config

class AudioFeed(Feed):
    title = "text-to-speech-app items"
    link = f"http://{config('SERVER_IP')}"
    description = "Audio versions of your text files."
    author = 'Larry Hudson'

    def items(self):
        return TextFile.objects.exclude(mp3_file='')

    def item_title(self, item):
        return item.name

    def item_description(self, item):
        return item.description

    def item_link(self, item):
        return item.mp3_file.url

    def item_enclosure_mime_type(self, item):
        return 'audio/mpeg'

    def item_enclosure_url(self, item):
        return item.mp3_file.url

    def item_enclosure_length(self, item):
        return os.path.getsize(item.mp3_file.path)