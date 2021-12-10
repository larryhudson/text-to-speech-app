from django.contrib.syndication.views import Feed
from django.urls import reverse
from .models import TextFile

class AudioFeed(Feed):
    title = "Audio items"
    link = "/audio-items/"
    description = "Audio versions of your text files."

    def items(self):
        return TextFile.objects.exclude(mp3_file='')

    def item_title(self, item):
        return item.name

    def item_description(self, item):
        return item.description

    # item_link is only needed if NewsItem has no get_absolute_url method.
    def item_link(self, item):
        return item.mp3_file.url