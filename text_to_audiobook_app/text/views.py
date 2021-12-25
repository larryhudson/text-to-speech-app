from django.shortcuts import render, redirect
from django.http import JsonResponse
from .models import TextFile, Image, Webpage
from . import forms
from .utils import write_text_to_file
from django.contrib.auth.decorators import login_required
from asgiref.sync import sync_to_async
# Create your views here.

def index(request):
    text_files = TextFile.objects.all()

    return render(request, 'index.html', {'text_files': text_files})

def detail(request, id):
    text_file = TextFile.objects.get(id=id)

    return render(request, 'detail.html', {'text_file': text_file})

async def create_audio_version(request, id):
    text_file = await sync_to_async(TextFile.objects.get)(id=id)

    await text_file.create_audio_version()

    request_is_fetch = request.headers.get("X-Is-Fetch", False)

    if (request_is_fetch):
        return JsonResponse({
            'status': text_file.status,
            'mp3_file_path': text_file.mp3_file.url if text_file.mp3_file else None
        })
    else:
        return redirect('/')


@login_required
def new_text_file(request):
    if request.method == 'GET':
        form = forms.TextFileForm()
        return render(request, 'modify.html', {'form': form, 'item_type': 'text file'})
    else:
        form = forms.TextFileForm(request.POST)
        if form.is_valid():
            text_file = form.save()
            return redirect(text_file)

@login_required
def new_image(request):
    if request.method == 'GET':
        form = forms.ImageForm()
        return render(request, 'modify.html', {'form': form, 'item_type': 'document'})
    else:
        form = forms.TextFileForm(request.POST)
        if form.is_valid():
            instance = form.save()
            return redirect(instance)
        else:
            return render(request, 'modify.html', {'form': form})

@login_required
def new_webpage(request):
    if request.method == 'GET':
        form = forms.WebpageForm()
        return render(request, 'modify.html', {'form': form, 'item_type': 'webpage'})
    else:
        form = forms.WebpageForm(request.POST)
        if form.is_valid():
            webpage = form.save()
            webpage.create_text_version()

            return redirect(webpage.text_file.get_absolute_url())

def view_text_file(request, id):
    text_file = TextFile.objects.get(id=id)

    return render(request, 'view_text_file.html', {'text_file': text_file})

@login_required
def modify_text_content(request, id):
    text_file = TextFile.objects.get(id=id)

    if request.method == 'POST':
        new_content = request.POST.get('text_content')
        written = write_text_to_file(new_content, text_file.file.path)
        return redirect(text_file.get_absolute_url())

    return render(request, 'modify_text.html', {'text_file': text_file})

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
