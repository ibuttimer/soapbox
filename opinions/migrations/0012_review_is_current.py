# Generated by Django 4.1.3 on 2022-11-22 17:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('opinions', '0011_followstatus'),
    ]

    operations = [
        migrations.AddField(
            model_name='review',
            name='is_current',
            field=models.BooleanField(
                default=True,
                help_text='Designates that this record represents the '
                          'current review status.',
                verbose_name='is current record'),
        ),
    ]
