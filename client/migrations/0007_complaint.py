# Generated by Django 4.2.3 on 2023-08-21 20:48

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('client', '0006_remove_announcement_moderation_decide_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Complaint',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.TextField(null=True)),
                ('complaint_reason', models.CharField(choices=[('', ''), ('theft', 'Мошенничество'), ('bad_photo', 'Некорректное фото'), ('bad_description', 'Некорректное описание')], default='')),
                ('announcement', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='complaints', to='client.announcement')),
                ('sender', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='complaints', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]