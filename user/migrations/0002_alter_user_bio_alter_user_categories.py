# Generated by Django 4.1 on 2022-08-30 07:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='bio',
            field=models.CharField(max_length=250, verbose_name='biography'),
        ),
        migrations.AlterField(
            model_name='user',
            name='categories',
            field=models.CharField(blank=True, max_length=250,
                                   verbose_name='categories'),
        ),
    ]
