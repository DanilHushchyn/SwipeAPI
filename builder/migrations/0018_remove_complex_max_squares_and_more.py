# Generated by Django 4.2.3 on 2023-08-27 13:20

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('builder', '0017_gallerycomplex'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='complex',
            name='max_squares',
        ),
        migrations.RemoveField(
            model_name='complex',
            name='square_price',
        ),
    ]
