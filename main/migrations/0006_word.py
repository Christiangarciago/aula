# Generated by Django 3.1 on 2020-11-05 09:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0005_remove_profile_group_public_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='Word',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('word', models.CharField(max_length=50, verbose_name='A word')),
                ('type', models.CharField(choices=[('animal', 'animal'), ('color', 'color'), ('adjective', 'adjective')], max_length=9)),
            ],
        ),
    ]