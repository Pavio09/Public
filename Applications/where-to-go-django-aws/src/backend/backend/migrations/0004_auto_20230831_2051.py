# Generated by Django 3.2 on 2023-08-31 18:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0003_remove_amenity_description_en'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='amenity',
            name='group_name',
        ),
        migrations.AddField(
            model_name='amenity',
            name='amenity_key',
            field=models.CharField(default='x', max_length=200, unique=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='amenity',
            name='group_amenity',
            field=models.CharField(default='x', max_length=200, unique=True),
            preserve_default=False,
        ),
    ]