# Generated by Django 4.1.7 on 2023-03-20 19:45

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('question_app', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='question',
            name='uuid',
        ),
    ]
