# Generated by Django 4.1 on 2022-09-27 13:28

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import utils.models


class Migration(migrations.Migration):

    dependencies = [
        ('categories', '0004_add_preview_status'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('opinions', '0004_opinion_excerpt_alter_opinion_content'),
    ]

    operations = [
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.BigAutoField(
                    auto_created=True, primary_key=True, serialize=False,
                    verbose_name='ID')),
                ('content', models.CharField(
                    max_length=700, verbose_name='content')),
                ('parent', models.BigIntegerField(
                    blank=True, default=0, verbose_name='parent')),
                ('level', models.IntegerField(
                    blank=True, default=0, verbose_name='level')),
                ('slug', models.SlugField(unique=True, verbose_name='slug')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('opinion', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    to='opinions.opinion')),
                ('status', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    to='categories.status')),
                ('user', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    to=settings.AUTH_USER_MODEL)),
            ],
            bases=(utils.models.SlugMixin, models.Model),
        ),
    ]
