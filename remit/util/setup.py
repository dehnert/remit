#!/usr/bin/python
import sys
import os

if __name__ == '__main__':
    cur_file = os.path.abspath(__file__)
    django_dir = os.path.abspath(os.path.join(os.path.dirname(cur_file), '..'))
    sys.path.append(django_dir)
    os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

import settings

import finance_core.models
import vouchers.models

import util.add_gl_accounts
import finance_core.util

from django.contrib.auth.models import User, Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q


base_structure = (
    ('Assets', None, ),
    ('Expenses', None, ),
    ('Income', None, ),
)

def get_or_create_group(name):
    try:
        group = Group.objects.get(name=name, )
    except Group.DoesNotExist:
        group = Group(name=name, )
        group.save()
    return group

def grant_by_codename(principal, codename):
    principal.permissions.add(Permission.objects.get(codename=codename, ))

if __name__ == '__main__':
    if len(finance_core.models.BudgetArea.objects.filter(depth=1)) == 0:
        base = finance_core.models.BudgetArea.add_root(name='Accounts', always=True, use_owner=True, )
    else:
        base = finance_core.models.BudgetArea.get_by_path(['Accounts',])
    finance_core.util.mass_add_accounts(base, base_structure, sys.stdout, )
    util.add_gl_accounts.add_gl_accounts()

    # Do the various auth setup
    get_or_create_group('autocreated')
    get_or_create_group('mit')
    local_auth_only = get_or_create_group('local-auth-only')
    treasurers = get_or_create_group('treasurers')
    treasurer_perms = Permission.objects.filter(content_type__app_label__in=['vouchers', 'finance_core', ],)
    for perm in treasurer_perms:
        treasurers.permissions.add(perm)
    treasurers.save()
    gdownloader = get_or_create_group('downloader')
    grant_by_codename(gdownloader, 'generate_vouchers', )
    gdownloader.save()
    try:
        udown = User.objects.get(username='downloader', )
    except User.DoesNotExist:
        udown = User.objects.create_user(username='downloader', email=settings.SERVER_EMAIL, )
        udown.is_active = False
        udown.is_staff  = True
        udown.groups.add(local_auth_only)
        udown.groups.add(gdownloader)
        udown.save()
