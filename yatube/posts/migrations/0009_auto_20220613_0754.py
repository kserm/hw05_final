# Generated by Django 2.2.16 on 2022-06-13 04:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0008_comment'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comment',
            name='created',
            field=models.DateTimeField(auto_now_add=True, help_text='Дата публикации комментария', verbose_name='Дата комментария'),
        ),
    ]
