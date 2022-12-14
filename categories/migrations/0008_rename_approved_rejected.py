# Generated by Django 4.1.3 on 2022-11-28 14:27

from django.db import migrations

from categories.constants import (
    STATUS_APPROVED, STATUS_REJECTED, STATUS_UNACCEPTABLE, STATUS_ACCEPTABLE
)


class Migration(migrations.Migration):

    dependencies = [
        ('categories', '0007_add_deleted_status'),
    ]

    # https://docs.djangoproject.com/en/4.1/ref/migration-operations/#runsql

    operations = [
        migrations.RunSQL(
            sql=[
                ("UPDATE categories_status SET name=%s WHERE name=%s;",
                 [new_name, old_name])
            ],
            reverse_sql=[
                ("UPDATE categories_status SET name=%s WHERE name=%s;",
                 [old_name, new_name])]
        )
        for old_name, new_name in [
            (STATUS_APPROVED, STATUS_UNACCEPTABLE),
            (STATUS_REJECTED, STATUS_ACCEPTABLE)
        ]
    ]
