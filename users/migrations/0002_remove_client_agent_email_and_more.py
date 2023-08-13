# Generated by Django 4.2.3 on 2023-08-13 20:28

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('builder', '0002_initial'),
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='client',
            name='agent_email',
        ),
        migrations.RemoveField(
            model_name='client',
            name='agent_first_name',
        ),
        migrations.RemoveField(
            model_name='client',
            name='agent_last_name',
        ),
        migrations.RemoveField(
            model_name='client',
            name='agent_phone',
        ),
        migrations.CreateModel(
            name='Contact',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('contact_type', models.CharField(choices=[('Отдел продаж', 'Отдел продаж'), ('Агент', 'Агент')], max_length=20)),
                ('phone', models.CharField(max_length=19, validators=[django.core.validators.MaxLengthValidator(19), django.core.validators.MinLengthValidator(19), django.core.validators.ProhibitNullCharactersValidator(), django.core.validators.RegexValidator('^\\+38 \\(\\d{3}\\) \\d{3}-?\\d{2}-?\\d{2}$', message='Неверно введён номер телефона.Пример ввода: +38 (098) 567-81-23')])),
                ('first_name', models.CharField(blank=True, max_length=30, null=True)),
                ('last_name', models.CharField(blank=True, max_length=30, null=True)),
                ('email', models.EmailField(blank=True, max_length=254, null=True)),
                ('complex', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='complex_contacts', to='builder.complex')),
                ('user', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='agent_contacts', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
