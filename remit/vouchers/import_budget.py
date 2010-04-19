import sys
import os
import csv
import subprocess
import vouchers.models
import finance_core.models
from finance_core.models import BudgetArea
from finance_core.models import coerce_full_email
from finance_core.models import Transaction
from finance_core.models import get_layer_by_name, layer_num
from decimal import *

columns = ['comm_name','priority','expense_type','start_date','end_date','project','item_name','desc','people','count','costitem','subtotal','per_person','email_list']
line_format = "%(priority)-4.4s  %(expense_type)-10.10s  %(subtotal)10.10s  %(project)-16.16s  %(item_name)-20.20s  %(desc)-20.20s  %(people)6.6s  %(count)5.5s  %(costitem)10.10s"

def build_committees(infile=sys.stdin):
    committees = {}
    reader = csv.reader(infile)
    for comm in reader:
        email_list,chair_list,name,prefer_chair,area,account = comm
        if prefer_chair=='yes': prefer_chair = True
        else: prefer_chair = False
        committees[email_list] = { 'email_list': email_list, 'chair_list': chair_list, 'name': name, 'prefer_chair':prefer_chair, 'area':area, 'account':account}
    return committees

def do_populate_area_structure(default_addr):
    nodes = [
        [ ('Accounts', 'Root',) ],
        [ ('Assets', 'Assets', ) ],
        [ ('Budget', "This period's intended operating budget", ) ],
        [
            ('Holding', "Holding account for the budgets between income and transferring to committee / line item accounts", ),
            ('Core', "Core budget areas", ),
            ('Committees', "Committees and auxiliary budget areas", ),
        ],
    ]
    parent = None
    for zdepth, accounts in enumerate(nodes):
        depth=zdepth+1
        for name, comment in accounts:
            if(len(BudgetArea.objects.filter(name=name, depth=depth)) == 0):
                # Create the new node
                if parent:
                    parent.add_child(name=name, comment=comment,
                        always=True, use_owner=True,)
                else:
                    BudgetArea.add_root(name=name, comment=comment,
                        always=True, use_owner=True,
                        owner=default_addr,
                        interested=default_addr,
                        account_number=0,
                    )
        # This is sorta evil, in that it abuses the fact that Python
        # won't put name out of scope
        parent = BudgetArea.objects.get(name=name, depth=depth)
    return (depth, )

def do_populate_committees(default_addr, committees):
    (depth,) = do_populate_area_structure(default_addr, )
    core = BudgetArea.objects.get(name='Core', depth=depth)
    comms = BudgetArea.objects.get(name='Committees', depth=depth)
    parents = {
        'Core':core,
        'Committees':comms,
    }
    for comm in committees.values():
        parent = parents[comm['area']]
        if len(parent.get_children().filter(name=comm['name'])) > 0:
            pass
        else:
            parent.add_child(
                name=comm['name'],
                owner=coerce_full_email(comm['chair_list']),
                interested=coerce_full_email(comm['email_list']),
                use_owner=comm['prefer_chair'],
                account_number=(comm['account'] or 0),
                always=True,
            )
    return (depth+1, )

budget_layer = layer_num(get_layer_by_name('budget'))
def do_process_rows(committees, budget, term, depth):
    reader = csv.reader(budget)

    header = reader.next()
    line_dict = {}
    for key, elem in zip(columns, header,):
        line_dict[key]=elem

    budget_source = BudgetArea.get_by_path(
        ['Accounts','Assets','Budget','Holding']
    )

    for line in reader:
        comm_name,priority,expense_type,start_date,end_date,project,item_name,desc,people,count,costitem,subtotal,perperson,email_list=line
        line_dict = {}
        for key, elem in zip(columns, line,):
            line_dict[key]=elem
        if(email_list != "" and comm_name[-4:] != " Sum"):
            email_list = coerce_full_email(email_list.lower())
            comm = BudgetArea.objects.get(depth=depth, interested=email_list,)
            projects = comm.get_children().filter(name=project)
            if(len(projects)==0):
                parent_project = comm.add_child(
                    name=project,
                    always=False,
                )
            else: parent_project = projects[0]
            parent_project.mark_used(term)
            line_items = parent_project.get_children().filter(name=item_name)
            if(len(line_items)==0):
                line_item_obj = parent_project.add_child(
                    name=item_name,
                    always=False,
                )
            else: line_item_obj = line_items[0]
            line_item_obj.mark_used(term)
            amount = Decimal(subtotal.replace('$', '').replace(',', ''))
            finance_core.models.make_transfer(
                item_name, amount, budget_layer,
                term, budget_source, line_item_obj, desc=desc,
                incurred_time=None,
            )


def main(default_addr, committees_file, budget_file, term_name, ):
    term = vouchers.models.BudgetTerm.objects.get(name=term_name)
    committees = build_committees(committees_file,)
    (depth, ) = do_populate_committees(default_addr, committees)
    do_process_rows(committees, budget_file, term, depth)
