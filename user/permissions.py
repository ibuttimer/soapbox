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
from collections import namedtuple

from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.db.backends.base.schema import BaseDatabaseSchemaEditor
from django.db.migrations.state import StateApps
from django.contrib.auth.management import create_permissions

from categories.models import Category
from opinions.constants import CLOSE_REVIEW_PERM, WITHDRAW_REVIEW_PERM
from opinions.models import Opinion, Review, Comment
from soapbox import OPINIONS_APP_NAME, CATEGORIES_APP_NAME
from utils import permission_name, Crud
from .constants import AUTHOR_GROUP, MODERATOR_GROUP
from .models import User

ADD = 'add'
REMOVE = 'remove'
PermSetting = namedtuple(
    'PermSetting',
    ['model', 'all', 'perms', 'app', 'action'],
    defaults=[None, False, [], '', ADD]
)


def review_permissions(group: str) -> list[str]:
    """
    Get review permissions
    :param group: AUTHOR_GROUP or MODERATOR_GROUP
    :return: list of permissions
    """
    permissions = [
        permission_name(Review, op)
        for op in list(Crud) if op != Crud.DELETE
    ]
    permissions.append(WITHDRAW_REVIEW_PERM
                       if group == AUTHOR_GROUP else CLOSE_REVIEW_PERM)

    return permissions


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
        AUTHOR_GROUP, [
            PermSetting(model=Opinion, all=True, app=OPINIONS_APP_NAME),
            PermSetting(model=Review,
                        perms=review_permissions(AUTHOR_GROUP),
                        app=OPINIONS_APP_NAME)
        ], apps=apps, schema_editor=schema_editor)


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
        MODERATOR_GROUP, [
            PermSetting(model=Opinion, all=True, app=OPINIONS_APP_NAME),
            PermSetting(model=Review,
                        perms=review_permissions(MODERATOR_GROUP),
                        app=OPINIONS_APP_NAME)
        ], apps=apps, schema_editor=schema_editor)


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
        perm_settings: list[PermSetting] | None = None,
        apps: StateApps = None,
        schema_editor: BaseDatabaseSchemaEditor = None) -> Group:
    """
    Create a group and assign permissions
    :param group_name: name of group to create
    :param perm_settings: list of permission settings
    :param apps: apps registry, default None
    :param schema_editor:
        editor generating statements to change database schema, default None
    :return: new group
    """
    group = None
    if apps:    # called from a migration
        migration_add_group(apps, schema_editor, group_name)

        set_basic_permissions(group_name, perm_settings,
                              apps=apps, schema_editor=schema_editor)
    else:       # called from the app
        group, created = Group.objects.get_or_create(name=group_name)
        if created or group.permissions.count() == 0:
            set_basic_permissions(group, perm_settings)

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
                          perm_settings: list[PermSetting] = None,
                          apps: StateApps = None,
                          schema_editor: BaseDatabaseSchemaEditor = None):
    """
    Set the permissions for the specified group
    :param group:
        group to update; Group object in app mode or name of group in
        migration mode
    :param perm_settings: list of permission settings
    :param apps: apps registry, default None
    :param schema_editor:
        editor generating statements to change database schema, default None
    """
    def set_permissions(grp: Group, setting: PermSetting, perms):
        # add/remove specified permissions
        if setting.action == ADD:
            grp.permissions.add(*perms)
        elif setting.action == REMOVE:
            grp.permissions.remove(*perms)

    if apps:    # called from a migration
        db_alias = schema_editor.connection.alias
        group = apps.get_model("auth", "Group")\
            .objects.using(db_alias).filter(name=group).first()
        assert group is not None
        permission = apps.get_model("auth", "Permission")

        if perm_settings:
            for perm_setting in perm_settings:
                if perm_setting.all:
                    # add all model crud permissions
                    model = perm_setting.model._meta.model_name.lower()
                    filter_args = {
                        'codename__endswith': f"_{model}",
                        'content_type__app_label': perm_setting.app
                    }
                else:
                    # add specified permissions
                    filter_args = {
                        'codename__in': perm_setting.perms,
                        'content_type__app_label': perm_setting.app
                    }
                permissions = permission.objects.using(db_alias).\
                    filter(**filter_args)
                assert permissions.exists()
                set_permissions(group, perm_setting, permissions)

    else:   # called from the app
        if perm_settings:
            for perm_setting in perm_settings:
                content_type = ContentType.objects. \
                    get_for_model(perm_setting.model)
                if perm_setting.all:
                    # add all model crud permissions
                    permissions = Permission.objects.\
                        filter(content_type=content_type)
                else:
                    # add specified permissions
                    permissions = Permission.objects.filter(
                        content_type=content_type,
                        codename__in=perm_setting.perms)
                assert permissions.exists()
                set_permissions(group, perm_setting, permissions)


def category_permissions() -> tuple[list, list]:
    """ Get author and moderator category permissions """
    return [
        permission_name(Category, Crud.READ)    # author
    ], [
        permission_name(Category, op)           # moderator
        for op in list(Crud) if op != Crud.DELETE
    ]


def set_category_permissions(
        action: str, apps: StateApps = None,
        schema_editor: BaseDatabaseSchemaEditor = None):
    """
    Set category permissions
    :param action: action to perform; ADD or REMOVE
    :param apps: apps registry, default None
    :param schema_editor:
        editor generating statements to change database schema, default None
    """
    author_group = AUTHOR_GROUP
    moderator_group = MODERATOR_GROUP
    if not apps:    # called from the app
        author_group = Group.objects.get_or_create(name=author_group)
        moderator_group = Group.objects.get_or_create(name=moderator_group)
    # else called from a migration

    author_permissions, moderator_permissions = category_permissions()
    set_basic_permissions(author_group, [
        PermSetting(model=Category, perms=author_permissions,
                    app=CATEGORIES_APP_NAME, action=action)
    ], apps=apps, schema_editor=schema_editor)

    set_basic_permissions(moderator_group, [
        PermSetting(model=Category, perms=moderator_permissions,
                    app=CATEGORIES_APP_NAME, action=action)
    ], apps=apps, schema_editor=schema_editor)


def add_category_permissions(apps: StateApps = None,
                             schema_editor: BaseDatabaseSchemaEditor = None):
    """
    Add category permissions
    :param apps: apps registry, default None
    :param schema_editor:
        editor generating statements to change database schema, default None
    """
    set_category_permissions(ADD, apps=apps, schema_editor=schema_editor)


def remove_category_permissions(
        apps: StateApps = None,
        schema_editor: BaseDatabaseSchemaEditor = None):
    """
    Remove category permissions
    :param apps: apps registry, default None
    :param schema_editor:
        editor generating statements to change database schema, default None
    """
    set_category_permissions(REMOVE, apps=apps, schema_editor=schema_editor)


def set_comment_permissions(
        action: str, apps: StateApps = None,
        schema_editor: BaseDatabaseSchemaEditor = None):
    """
    Set comment permissions
    :param action: action to perform; ADD or REMOVE
    :param apps: apps registry, default None
    :param schema_editor:
        editor generating statements to change database schema, default None
    """
    author_group = AUTHOR_GROUP
    moderator_group = MODERATOR_GROUP
    if not apps:    # called from the app
        author_group = Group.objects.get_or_create(name=author_group)
        moderator_group = Group.objects.get_or_create(name=moderator_group)
    # else called from a migration

    permissions = [
        permission_name(Comment, cmt) for cmt in list(Crud)
    ]
    for group in [author_group, moderator_group]:
        set_basic_permissions(group, [
            PermSetting(model=Comment, perms=permissions,
                        app=OPINIONS_APP_NAME, action=action)
        ], apps=apps, schema_editor=schema_editor)


def add_comment_permissions(apps: StateApps = None,
                            schema_editor: BaseDatabaseSchemaEditor = None):
    """
    Add comment permissions
    :param apps: apps registry, default None
    :param schema_editor:
        editor generating statements to change database schema, default None
    """
    set_comment_permissions(ADD, apps=apps, schema_editor=schema_editor)


def remove_comment_permissions(
        apps: StateApps = None,
        schema_editor: BaseDatabaseSchemaEditor = None):
    """
    Remove comment permissions
    :param apps: apps registry, default None
    :param schema_editor:
        editor generating statements to change database schema, default None
    """
    set_comment_permissions(REMOVE, apps=apps, schema_editor=schema_editor)


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


def migrate_permissions(apps: StateApps = None,
                        schema_editor: BaseDatabaseSchemaEditor = None):
    """
    Migrate permissions.

    This is a necessary operation prior to assigning permissions during
    migration on a *pristine* database. If this operation is not performed
    the permissions don't exist, so can't be assigned.
    Thanks to https://stackoverflow.com/a/40092780/4054609

    :param apps: apps registry, default None
    :param schema_editor:
        editor generating statements to change database schema, default None
    """
    for app_config in apps.get_app_configs():
        app_config.models_module = True
        create_permissions(app_config, apps=apps, verbosity=0)
        app_config.models_module = None


def reverse_migrate_permissions(
        apps: StateApps = None,
        schema_editor: BaseDatabaseSchemaEditor = None):
    """ Dummy reverse for migrate_permissions """
    pass
