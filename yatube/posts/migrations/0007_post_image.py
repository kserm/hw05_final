# Generated by Django 2.2.16 on 2022-06-11 07:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0006_auto_20220528_2012'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='image',
            field=models.ImageField(blank=True, help_text='Картинка поста', upload_to='posts/', verbose_name='Картинка'),
        ),
    ]
