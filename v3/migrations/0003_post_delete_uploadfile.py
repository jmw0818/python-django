# Generated by Django 5.0.4 on 2024-04-07 12:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('v3', '0002_uploadfile_delete_fileupload'),
    ]

    operations = [
        migrations.CreateModel(
            name='Post',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=30)),
                ('content', models.TextField()),
                ('head_image', models.ImageField(blank=True, upload_to='blog/images/%Y/%m/%d')),
                ('file_upload', models.FileField(blank=True, upload_to='blog/files/%Y/%m/%d')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.DeleteModel(
            name='UploadFile',
        ),
    ]
