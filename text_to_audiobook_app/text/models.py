from django.db import models
import api.utils as api
from .utils import extract_text, extract_text_from_url, write_text_to_file
import os
from django.conf import settings
import requests
import shutil


# Create your models here.

def text_file_upload_path(instance, filename):
        return f'text_files/{filename}'

class TextFile(models.Model):

    def __str__(self):
        return self.name

    file = models.FileField(upload_to=text_file_upload_path)

    name = models.CharField(max_length=255)

    description = models.CharField(max_length=255)

    synthesis_id = models.CharField(null=True,blank=True, max_length=255)

    status = models.CharField(max_length=255, default='Not submitted')

    def num_characters(self):
        with open(self.file.path) as file:
            data = file.read()
        return len(data)

    def is_short(self):
        num_characters = self.num_characters()
        return num_characters < 8000

    def synthesis_cost(self):
        num_characters = self.num_characters()
        is_short = num_characters < 8000

        price_per_character_short = 0.000022
        price_per_character_long = 0.000139

        dollars = (num_characters * price_per_character_short
            if is_short else
            num_characters * price_per_character_long)

        return '$' + format(dollars, ',.2f')
            
    def audio_file_upload_path(instance, filename):
        text_file_name = os.path.basename(instance.file.name)
        text_file_name_without_extension = os.path.splitext(text_file_name)[0]
        return f'mp3_files/{instance.id}/{text_file_name_without_extension}.mp3'

    mp3_file = models.FileField(upload_to=audio_file_upload_path, null=True, blank=True)

    download_link = models.URLField(null=True,blank=True, max_length=255)

    def text_content(self):
        with open(self.file.path) as file:
            text = file.read()
        
        return text

    def create_audio_version(self):
        num_characters = self.num_characters()
        is_short = self.is_short()
        if is_short:
            done = api.synthesise_short_text(self)
            if done:
                self.mp3_file.name = self.audio_file_upload_path(None)
                self.status = 'Ready to download'
                self.save()
        else:
            synthesis_id = api.submit_synthesis_for_text_file(self)
            if synthesis_id:
                self.synthesis_id = synthesis_id
                self.status = 'Submitted'
                self.save()
    
    def update_synthesis_status(self):
        if (self.mp3_file):
            self.status = 'Ready to download'
            self.save()
            return
        if (self.synthesis_id):
            status_data = api.get_synthesis_status(self.synthesis_id)
            print(status_data)
            self.status = status_data['status']
            self.save()

    def download_synthesis(self):
        status_data = api.get_synthesis_status(self.synthesis_id)
        if not status_data['status'] == 'Succeeded':
            print('synthesis not ready yet')
            print(status_data)
            return False
        
        synthesis_download_url = status_data['resultsUrl']

        # create a folder for the synthesis zip file
        synthesis_files_folder = os.path.join(settings.MEDIA_ROOT, 'synthesis_files', self.synthesis_id)

        if not os.path.isdir(synthesis_files_folder):
            os.makedirs(synthesis_files_folder)

        zip_file_name = f'{self.synthesis_id}.zip'

        zip_file_path = os.path.join(synthesis_files_folder, zip_file_name)

        download_response = requests.get(synthesis_download_url, stream=True)

        if download_response.ok:
            print("saving to", os.path.abspath(zip_file_path))
            with open(zip_file_path, 'wb') as f:
                for chunk in download_response.iter_content(chunk_size=1024 * 8):
                    if chunk:
                        f.write(chunk)
                        f.flush()
                        os.fsync(f.fileno())
        else:  # HTTP status code 4XX/5XX
            print("Download failed: status code {}\n{}".format(
                download_response.status_code,
                download_response.text))
            return False
        
        # unpack the zip file
        shutil.unpack_archive(zip_file_path, synthesis_files_folder)

        download_mp3_file_path = os.path.join(synthesis_files_folder, 'output.mp3')

        text_file_name = os.path.basename(self.file.name)
        text_file_name_without_extension = os.path.splitext(text_file_name)[0]

        new_mp3_folder = f'mp3_files/{self.id}'
        new_mp3_folder_absolute = os.path.join(settings.MEDIA_ROOT, new_mp3_folder)

        if not os.path.isdir(
            new_mp3_folder_absolute
        ):
            os.makedirs(new_mp3_folder_absolute)

        new_mp3_file_name = f'{new_mp3_folder}/{text_file_name_without_extension}.mp3'

        new_mp3_file_path = os.path.join(
            settings.MEDIA_ROOT,
            new_mp3_file_name
        )

        shutil.copy(download_mp3_file_path, new_mp3_file_path)

        self.mp3_file.name = new_mp3_file_name
        self.status = 'Ready to download'
        self.save()

class Webpage(models.Model):
    name = models.CharField(max_length=255)
    url = models.URLField(max_length=1000)

    text_file = models.OneToOneField(TextFile, on_delete=models.SET_NULL, null=True, blank=True, related_name='source')

    def create_text_version(self):
        text = extract_text_from_url(self.url)

        text_file_path = os.path.join(settings.MEDIA_ROOT, f'text_files/from_webpage/{self.id}/trafilatura.txt')

        written_file = write_text_to_file(text, text_file_path)

        if not self.text_file:
            self.text_file = TextFile.objects.create(
                file=text_file_path,
                name=self.name,
                description=self.url
            )

            self.save()

        return text


    


class Image(models.Model):
    def image_upload_path(instance, filename):
        return f'images/{filename}'
        
    file = models.FileField(upload_to=image_upload_path)
    name = models.CharField(max_length=255)

    operation_id = models.CharField(null=True,blank=True, max_length=255)
    status = models.CharField(max_length=255, default='Not submitted')

    text_file = models.OneToOneField(TextFile, on_delete=models.SET_NULL, null=True, blank=True, related_name='source_image')

    def __str__(self):
        return self.name

    def create_text_version(self, **textract_options):
        # try textract
        text = extract_text(self.file.path, **textract_options)

        text_file_path = os.path.join(settings.MEDIA_ROOT, f'text_files/from_image/{self.id}/textract.txt')

        written_file = write_text_to_file(text, text_file_path)

        if not self.text_file:
            self.text_file = TextFile.objects.create(
                file=text_file_path,
                name=self.name,
                description=self.name
            )

            self.save()
    
        return text

        # operation_id = api.submit_ocr_request(self.file.path)
        # if operation_id:
        #     self.operation_id = operation_id
        #     self.save()

    def get_ocr_result(self):
        if not self.operation_id:
            return False
        
        text = api.get_ocr_result(self.operation_id)

        text_file_path = os.path.join(settings.MEDIA_ROOT, f'text_files/from_image/{self.id}/ocr.txt')

        text_file_folder = os.path.dirname(text_file_path)

        if not os.path.isdir(text_file_folder):
            os.makedirs(text_file_folder)

        with open(text_file_path, 'w') as file:
            file.write(text)

        text_file = TextFile.objects.create(
            file=text_file_path,
            name=self.name,
            description=self.name
        )

        print(text)