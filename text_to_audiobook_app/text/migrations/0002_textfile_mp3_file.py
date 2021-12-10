# Generated by Django 4.0 on 2021-12-08 20:48

from django.db import migrations, models
import text.models


class Migration(migrations.Migration):

    dependencies = [
        ('text', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='textfile',
            name='mp3_file',
            field=models.FileField(blank=True, null=True, upload_to=text.models.TextFile.audio_file_upload_path),
        ),
    ]
