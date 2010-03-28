if __name__ == '__main__':
    import sys
    import os

    cur_file = os.path.abspath(__file__)
    django_dir = os.path.abspath(os.path.join(os.path.dirname(cur_file), '..'))
    sys.path.append(django_dir)
    os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

import finance_core.models
import vouchers.models

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
    ('Computer Supplies', 421900),
)

def add_gl_accounts():
    try:
        base = finance_core.models.BudgetArea.get_by_path(['Accounts', 'Expenses', ])
    except KeyError:
        base = finance_core.models.BudgetArea.get_by_path(['Accounts',])
        base = base.add_child(name='Expenses', always=True, use_owner=True)

    for name, number in expense_gls:
        try:
            path = 'Accounts.Expenses.' + name
            elem = finance_core.models.BudgetArea.get_by_pathstr(path)
        except KeyError:
            print "Adding %s (%s)" % (name, number,)
            # It doesn't exist
            if '.' in name:
                parts = name.rsplit('.', 1)
                path = 'Accounts.Expenses.'+parts[0]
                name = parts[1]
                parent = finance_core.models.BudgetArea.get_by_pathstr(path)
            else:
                parent = base
            parent.add_child(name=name, account_number=number, always=True, )
        else:
            print "%s (%s) already present" % (name, number,)

if __name__ == '__main__':
    add_gl_accounts()
