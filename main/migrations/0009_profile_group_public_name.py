# Generated by Django 3.1 on 2020-11-05 10:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0008_auto_20201105_0957'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='group_public_name',
            field=models.CharField(default='kk', max_length=255),
            preserve_default=False,
        ),
    ]