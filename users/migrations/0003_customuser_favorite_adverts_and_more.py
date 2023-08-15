# Generated by Django 4.2.3 on 2023-08-14 19:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('client', '0006_alter_advert_client_alter_chat_users_and_more'),
        ('builder', '0002_initial'),
        ('users', '0002_remove_client_agent_email_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='favorite_adverts',
            field=models.ManyToManyField(related_name='favorite_adverts_set', to='client.advert'),
        ),
        migrations.AddField(
            model_name='customuser',
            name='favorite_complexes',
            field=models.ManyToManyField(related_name='favorite_comlexes_set', to='builder.complex'),
        ),
        migrations.AddField(
            model_name='customuser',
            name='notification_type',
            field=models.CharField(choices=[('Мне', 'Мне'), ('Мне и агенту', 'Мне и агенту'), ('Агенту', 'Агенту'), ('Отключить', 'Отключить')], default='Мне', max_length=100),
        ),
        migrations.AddField(
            model_name='customuser',
            name='redirect_notifications_to_agent',
            field=models.BooleanField(default=False),
        ),
        migrations.DeleteModel(
            name='Client',
        ),
    ]
