# Generated by Django 4.1 on 2022-09-12 13:36

import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion

from ..constants import CLOSE_REVIEW_PERM, WITHDRAW_REVIEW_PERM


class Migration(migrations.Migration):

    dependencies = [
        ('categories', '0004_add_preview_status'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('opinions', '0002_opinion_user'),
    ]

    # NOTE: when reversing this migration the content type is left in
    # the 'django_content_type' table and permissions are left in
    # the 'auth_permission' table, but it doesn't cause a problem when
    # it's reapplied.

    operations = [
        migrations.CreateModel(
            name='Review',
            fields=[
                ('id', models.BigAutoField(
                    auto_created=True, primary_key=True, serialize=False,
                    verbose_name='ID')),
                ('reason', models.CharField(
                    max_length=500, verbose_name='reason')),
                ('comment', models.CharField(
                    max_length=500, verbose_name='comment')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('resolved', models.DateTimeField(
                    default=datetime.datetime(
                        1, 1, 1, 0, 0, tzinfo=datetime.timezone.utc))),
                ('opinion', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    to='opinions.opinion')),
                ('requested', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='requested_by',
                    to=settings.AUTH_USER_MODEL)),
                ('reviewer', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='reviewed_by',
                    to=settings.AUTH_USER_MODEL)),
                ('status', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    to='categories.status')),
            ],
            options={
                'permissions': [
                    (CLOSE_REVIEW_PERM,
                     'Can close a review by setting its status to resolved'),
                    (WITHDRAW_REVIEW_PERM,
                     'Can close a review by setting its status to withdrawn')
                ],
            },
        ),
    ]
