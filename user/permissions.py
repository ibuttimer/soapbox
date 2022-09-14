#  MIT License
#
#  Copyright (c) 2022 Ian Buttimer
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to
#  deal in the Software without restriction, including without limitation the
#  rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
#  sell copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in
#  all copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
#  FROM,OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
#  DEALINGS IN THE SOFTWARE.
#
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.db.backends.base.schema import BaseDatabaseSchemaEditor
from django.db.migrations.state import StateApps

from opinions.constants import CLOSE_REVIEW_PERM, WITHDRAW_REVIEW_PERM
from opinions.models import Opinion, Review
from soapbox import OPINIONS_APP_NAME
from utils import permission_name, Crud
from .constants import AUTHOR_GROUP, MODERATOR_GROUP
from .models import User


def create_author_group(
        apps: StateApps = None,
        schema_editor: BaseDatabaseSchemaEditor = None) -> Group:
    """
    Create the authors group
    :param apps: apps registry, default None
    :param schema_editor:
        editor generating statements to change database schema, default None
    :return: new group
    """
    return create_group_and_permissions(
        AUTHOR_GROUP, review_custom=WITHDRAW_REVIEW_PERM, apps=apps,
        schema_editor=schema_editor)


def remove_author_group(apps: StateApps,
                        schema_editor: BaseDatabaseSchemaEditor):
    """
    Migration reverse function to remove the author group
    :param apps: apps registry
    :param schema_editor:
        editor generating statements to change database schema
    """
    migration_remove_group(apps, schema_editor, AUTHOR_GROUP)


def create_moderator_group(
        apps: StateApps = None,
        schema_editor: BaseDatabaseSchemaEditor = None) -> Group:
    """
    Create the moderators group
    :param apps: apps registry, default None
    :param schema_editor:
        editor generating statements to change database schema, default None
    :return: new group
    """
    return create_group_and_permissions(
        MODERATOR_GROUP, review_custom=CLOSE_REVIEW_PERM, apps=apps,
        schema_editor=schema_editor)


def remove_moderator_group(apps: StateApps,
                           schema_editor: BaseDatabaseSchemaEditor):
    """
    Migration reverse function to remove the moderator group
    :param apps: apps registry
    :param schema_editor:
        editor generating statements to change database schema
    """
    migration_remove_group(apps, schema_editor, MODERATOR_GROUP)


def create_group_and_permissions(
        group_name: str,
        review_custom: list[str] | None = None,
        apps: StateApps = None,
        schema_editor: BaseDatabaseSchemaEditor = None) -> Group:
    """
    Create a group and assign permissions
    :param group_name: name of group to create
    :param review_custom: additional custom permissions for Review model
    :param apps: apps registry, default None
    :param schema_editor:
        editor generating statements to change database schema, default None
    :return: new group
    """
    group = None
    if apps:    # called from a migration
        migration_add_group(apps, schema_editor, group_name)

        set_basic_permissions(group_name, review_custom,
                              apps=apps, schema_editor=schema_editor)
    else:       # called from the app
        group, created = Group.objects.get_or_create(name=group_name)
        if created or group.permissions.count() == 0:
            set_basic_permissions(group, review_custom)

    return group


def migration_add_group(
        apps: StateApps, schema_editor: BaseDatabaseSchemaEditor, name: str):
    """
    Migration function to add a group
    :param apps: apps registry
    :param schema_editor:
        editor generating statements to change database schema
    :param name: name of group to add
    """
    group = apps.get_model("auth", "Group")
    db_alias = schema_editor.connection.alias
    group.objects.using(db_alias).create(name=name)


def migration_remove_group(
        apps: StateApps, schema_editor: BaseDatabaseSchemaEditor, name: str):
    """
    Migration reverse function to remove a group
    :param apps: apps registry
    :param schema_editor:
        editor generating statements to change database schema
    :param name: name of group to remove
    """
    group = apps.get_model("auth", "Group")
    db_alias = schema_editor.connection.alias
    group.objects.using(db_alias).filter(name=name).delete()


def set_basic_permissions(group: [Group, str],
                          review_custom: list[str] = None,
                          apps: StateApps = None,
                          schema_editor: BaseDatabaseSchemaEditor = None):
    """
    Set the permissions for the specified group
    :param group:
        group to update; Group object in app mode or name of group in
        migration mode
    :param review_custom: additional custom permissions for Review model
    :param apps: apps registry, default None
    :param schema_editor:
        editor generating statements to change database schema, default None
    """
    # review to add; create/read/update and any custom
    review_permissions = [
        permission_name(Review, op)
        for op in list(Crud) if op != Crud.DELETE
    ]
    if review_custom:
        if isinstance(review_custom, str):
            review_custom = [review_custom]
        review_permissions.extend(review_custom)

    if apps:    # called from a migration
        db_alias = schema_editor.connection.alias
        group = apps.get_model("auth", "Group")\
            .objects.using(db_alias).filter(name=group).first()
        permission = apps.get_model("auth", "Permission")

        # add all Opinion crud permissions
        permissions = permission.objects.using(db_alias).filter(
            codename__endswith="_opinion",
            content_type__app_label=OPINIONS_APP_NAME)
        group.permissions.set(permissions)

        # add Review permissions
        permissions = permission.objects.using(db_alias).filter(
            codename__in=review_permissions,
            content_type__app_label=OPINIONS_APP_NAME)
        group.permissions.add(*permissions)

    else:   # called from the app

        # add all Opinion crud permissions
        content_type = ContentType.objects.get_for_model(Opinion)
        permissions = Permission.objects.filter(content_type=content_type)
        group.permissions.set(permissions)

        # add Review permissions
        content_type = ContentType.objects.get_for_model(Review)
        permissions = Permission.objects.filter(
            content_type=content_type, codename__in=review_permissions)
        group.permissions.add(*permissions)


def add_to_authors(user: User):
    """
    Add the specified user to the authors group
    :param user: user to update
    """
    user.groups.add(
        create_author_group()
    )


def add_to_moderators(user: User):
    """
    Add the specified user to the moderators group
    :param user: user to update
    """
    user.groups.add(
        create_moderator_group()
    )
