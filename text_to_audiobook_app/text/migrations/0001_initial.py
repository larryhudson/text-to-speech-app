# Generated by Django 4.0 on 2021-12-08 20:06

from django.db import migrations, models
import text.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='TextFile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.FileField(upload_to=text.models.text_file_upload_path)),
                ('name', models.CharField(max_length=255)),
                ('description', models.CharField(max_length=255)),
                ('synthesis_id', models.CharField(blank=True, max_length=255, null=True)),
                ('download_link', models.URLField(blank=True, max_length=255, null=True)),
            ],
        ),
    ]
