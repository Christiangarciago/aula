# Generated by Django 3.1 on 2020-11-12 15:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0011_profile_group_picture'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='groups_string',
            field=models.CharField(blank=True, max_length=1000, null=True),
        ),
    ]
