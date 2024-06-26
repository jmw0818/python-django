# Generated by Django 5.0.4 on 2024-04-07 12:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('v3', '0003_post_delete_uploadfile'),
    ]

    operations = [
        migrations.CreateModel(
            name='UploadedFile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.FileField(upload_to='')),
                ('uploaded_on', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.DeleteModel(
            name='Post',
        ),
    ]
