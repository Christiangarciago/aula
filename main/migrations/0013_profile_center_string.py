# Generated by Django 3.1 on 2020-11-19 11:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0012_profile_groups_string'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='center_string',
            field=models.CharField(blank=True, max_length=1000, null=True),
        ),
    ]
