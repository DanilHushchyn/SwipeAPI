# Generated by Django 4.2.3 on 2023-09-18 11:58

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('builder', '0003_alter_apartment_price_alter_apartment_square'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='apartment',
            unique_together={('floor', 'sewer')},
        ),
    ]
