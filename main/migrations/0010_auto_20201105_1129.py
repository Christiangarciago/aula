# Generated by Django 3.1 on 2020-11-05 11:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0009_profile_group_public_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='group_password',
            field=models.CharField(max_length=4, null=True, verbose_name='Password grup'),
        ),
        migrations.AlterField(
            model_name='profile',
            name='group_public_name',
            field=models.CharField(max_length=255, null=True),
        ),
    ]
