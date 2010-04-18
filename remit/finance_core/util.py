import finance_core.models

class NullWrite:
    def write(self, string, ):
        pass
nullwrite = NullWrite()

def mass_add_accounts(base, accounts, writeto=nullwrite):
    for name, number in accounts:
        try:
            elem = finance_core.models.BudgetArea.get_by_pathstr(name, base=base, )
        except KeyError:
            writeto.write("Adding %s (%s)\n" % (name, number,),)
            # It doesn't exist
            if '.' in name:
                parts = name.rsplit('.', 1)
                path = parts[0]
                name = parts[1]
                parent = finance_core.models.BudgetArea.get_by_pathstr(path, base=base, )
            else:
                parent = base
            child = parent.add_child(name=name, account_number=number, always=True, )
        else:
            writeto.write("%s (%s) already present\n" % (name, number,))

