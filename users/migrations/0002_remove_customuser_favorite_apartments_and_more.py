# Generated by Django 4.2.3 on 2023-08-21 20:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('builder', '0008_remove_apartment_is_active_apartment_is_moderated_and_more'),
        ('client', '0006_remove_announcement_moderation_decide_and_more'),
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='customuser',
            name='favorite_apartments',
        ),
        migrations.AddField(
            model_name='customuser',
            name='favorite_announcements',
            field=models.ManyToManyField(to='client.announcement'),
        ),
        migrations.AlterField(
            model_name='customuser',
            name='favorite_complexes',
            field=models.ManyToManyField(to='builder.complex'),
        ),
    ]