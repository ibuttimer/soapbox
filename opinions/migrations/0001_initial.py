# Generated by Django 4.1 on 2022-09-05 14:00

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('categories', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Opinion',
            fields=[
                ('id', models.BigAutoField(
                    auto_created=True, primary_key=True, serialize=False,
                    verbose_name='ID')),
                ('title', models.CharField(
                    max_length=100, unique=True, verbose_name='title')),
                ('content', models.CharField(
                    max_length=1500, verbose_name='content')),
                ('slug', models.SlugField(unique=True, verbose_name='slug')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('published', models.DateTimeField(
                    default=datetime.datetime(
                        1, 1, 1, 0, 0, tzinfo=datetime.timezone.utc))),
                ('categories', models.ManyToManyField(
                    to='categories.category')),
                ('status', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    to='categories.status')),
            ],
            options={
                'ordering': ['title'],
            },
        ),
    ]
