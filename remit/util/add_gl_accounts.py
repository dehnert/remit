#!/usr/bin/env python

import sys
import os

if __name__ == '__main__':
    cur_file = os.path.abspath(__file__)
    django_dir = os.path.abspath(os.path.join(os.path.dirname(cur_file), '..'))
    sys.path.append(django_dir)
    os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

import finance_core.models
import vouchers.models
import finance_core.util

expense_gls = (
    ('Travel', 420050),
    ('Audio-Visual', 420106),
    ('Conference Expense', 420140),
    ('Entertainment', 420166),
    ('Materials and Services', 420226),
    ('Office Supplies', 420258),
    ('Professional Services', 420298),
    ('Copying', 420392),
    ('Books and Publications', 420800),
    ('Food', None),
    ('Food.Meetings', 421000),
    ('Food.Events', 421200),
    ('IT', None),
    ('IT.Computer Supplies', 421900),
    ('IT.On-line Services', 421920),
    ('Promotional & Memorabilia', 420302),
)

def add_gl_accounts():
    try:
        base = finance_core.models.BudgetArea.get_by_path(['Accounts', 'Expenses', ])
    except KeyError:
        base = finance_core.models.BudgetArea.get_by_path(['Accounts',])
        base = base.add_child(name='Expenses', always=True, use_owner=True)
        base = finance_core.models.BudgetArea.get_by_path(['Accounts', 'Expenses', ])
    finance_core.util.mass_add_accounts(base, expense_gls, writeto=sys.stdout)


if __name__ == '__main__':
    add_gl_accounts()
