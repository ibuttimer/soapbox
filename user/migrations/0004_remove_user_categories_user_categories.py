# Generated by Django 4.1 on 2022-09-05 14:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('categories', '0001_initial'),
        ('user', '0003_alter_user_avatar_alter_user_bio'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='categories',
        ),
        migrations.AddField(
            model_name='user',
            name='categories',
            field=models.ManyToManyField(to='categories.category'),
        ),
    ]
