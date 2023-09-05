# Generated by Django 4.2.3 on 2023-08-30 08:16

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('builder', '0018_remove_complex_max_squares_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='DocKitComplex',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.FileField(upload_to='complexes/doc-kit/')),
                ('complex', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='documents', to='builder.complex')),
            ],
            options={
                'db_table': 'dockit_complex',
            },
        ),
        migrations.RemoveField(
            model_name='file',
            name='dock_kit',
        ),
        migrations.RemoveField(
            model_name='photo',
            name='gallery',
        ),
        migrations.AlterModelOptions(
            name='gallerycomplex',
            options={},
        ),
        migrations.RemoveField(
            model_name='gallerycomplex',
            name='order',
        ),
        migrations.DeleteModel(
            name='DocKit',
        ),
        migrations.DeleteModel(
            name='File',
        ),
        migrations.DeleteModel(
            name='Gallery',
        ),
        migrations.DeleteModel(
            name='Photo',
        ),
    ]