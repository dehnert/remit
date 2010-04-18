import sys
import os

if __name__ == '__main__':
    cur_file = os.path.abspath(__file__)
    django_dir = os.path.abspath(os.path.join(os.path.dirname(cur_file), '..'))
    sys.path.append(django_dir)
    os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

import finance_core.models
import vouchers.models

import util.add_gl_accounts
import finance_core.util

base_structure = (
    ('Assets', None, ),
    ('Expenses', None, ),
    ('Income', None, ),
)

if __name__ == '__main__':
    if len(finance_core.models.BudgetArea.objects.filter(depth=1)) == 0:
        base = finance_core.models.BudgetArea.add_root(name='Accounts', always=True, use_owner=True, )
    else:
        base = finance_core.models.BudgetArea.get_by_path(['Accounts',])
    finance_core.util.mass_add_accounts(base, base_structure, sys.stdout, )
    util.add_gl_accounts.add_gl_accounts()
