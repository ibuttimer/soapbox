# Generated by Django 4.1 on 2022-10-10 17:34

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('opinions', '0005_comment'),
    ]

    operations = [
        migrations.AddField(
            model_name='comment',
            name='published',
            field=models.DateTimeField(
                default=datetime.datetime(
                    1, 1, 1, 0, 0, tzinfo=datetime.timezone.utc)),
        ),
    ]
