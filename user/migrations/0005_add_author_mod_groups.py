# Generated by Django 4.1 on 2022-09-14 07:41

from django.db import migrations

from ..permissions import (
    create_moderator_group, remove_moderator_group,
    create_author_group, remove_author_group,
    migrate_permissions, reverse_migrate_permissions
)


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0004_remove_user_categories_user_categories'),
        # Required dependency for migrate_permissions as per
        # https://stackoverflow.com/a/40092780/4054609
        ("auth", "0012_alter_user_first_name_max_length"),
    ]

    # https://docs.djangoproject.com/en/4.1/ref/migration-operations/#runpython

    operations = [
        migrations.RunPython(
            migrate_permissions, reverse_migrate_permissions),
        migrations.RunPython(create_author_group, remove_moderator_group),
        migrations.RunPython(create_moderator_group, remove_author_group),
    ]
