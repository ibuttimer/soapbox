# Generated by Django 4.1 on 2022-10-12 07:22

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('categories', '0005_add_reaction_statuses'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('opinions', '0006_comment_published'),
    ]

    operations = [
        migrations.CreateModel(
            name='AgreementStatus',
            fields=[
                ('id', models.BigAutoField(
                    auto_created=True, primary_key=True,
                    serialize=False, verbose_name='ID')),
                ('updated', models.DateTimeField(auto_now=True)),
                ('comment', models.ForeignKey(
                    blank=True, null=True,
                    on_delete=django.db.models.deletion.CASCADE,
                    to='opinions.comment')),
                ('opinion', models.ForeignKey(
                    blank=True, null=True,
                    on_delete=django.db.models.deletion.CASCADE,
                    to='opinions.opinion')),
                ('status', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    to='categories.status')),
                ('user', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]