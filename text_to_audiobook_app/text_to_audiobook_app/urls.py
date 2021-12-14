"""text_to_audiobook_app URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from text.feeds import AudioFeed
from text import views

urlpatterns = [
    path('', views.index, name="index"),
    path('text_file/new', views.new_text_file, name="new_text_file"),
    path('text_file/<int:id>/', views.view_text_file, name="view_text_file"),
    path('text_file/<int:id>/modify', views.modify_text_content, name="modify_text_content"),
    path('text_file/<int:id>/create_audio_version', views.create_audio_version, name="create_audio_version"),
    path('text_file/<int:id>/update_status', views.update_status, name="update_status"),
    path('text_file/<int:id>/download', views.download, name="download"),
    path('document/new', views.new_image, name="new_image"),
    path('document/<int:image_id>/extract_text', views.extract_text, name='extract_text'),
    path('webpage/new', views.new_webpage, name="new_webpage"),
    path('webpage/<int:webpage_id>/extract_text', views.extract_webpage_text, name='extract_webpage_text'),

    path('admin/', admin.site.urls),
    path('audio-feed/', AudioFeed()),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)