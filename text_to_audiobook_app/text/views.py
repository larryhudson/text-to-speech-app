from django.shortcuts import render, redirect
from django.http import JsonResponse
from .models import TextFile, Image, Webpage

# Create your views here.

def index(request):
    text_files = TextFile.objects.all()

    return render(request, 'index.html', {'text_files': text_files})

def detail(request, id):
    text_file = TextFile.objects.get(id=id)

    return render(request, 'detail.html', {'text_file': text_file})

def create_audio_version(request, id):
    text_file = TextFile.objects.get(id=id)

    text_file.create_audio_version()

    return JsonResponse({
        'status': text_file.status,
        'mp3_file_path': text_file.mp3_file.url if text_file.mp3_file else None
    })

def view_text_file(request, id):
    text_file = TextFile.objects.get(id=id)

    return render(request, 'view_text_file.html', {'text_file': text_file})

def update_status(request, id):
    text_file = TextFile.objects.get(id=id)

    text_file.update_synthesis_status()

    return redirect(f'/')

def download(request, id):
    text_file = TextFile.objects.get(id=id)

    text_file.download_synthesis()

    return redirect('/')

def extract_text(request, image_id):
    image = Image.objects.get(id=image_id)

    text = image.create_text_version()

    return render(request, 'extract_text.html', {'image': image, 'text': text})

def extract_webpage_text(request, webpage_id):
    webpage = Webpage.objects.get(id=webpage_id)

    text = webpage.create_text_version()

    return render(request, 'extract_text.html', {'image': webpage, 'text': text})
