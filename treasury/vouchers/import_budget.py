import sys
import os
import csv
import subprocess
import vouchers.models
from vouchers.models import BudgetArea
from vouchers.models import coerce_full_email

columns = ['comm_name','priority','expense_type','start_date','end_date','project','item_name','desc','people','count','costitem','subtotal','per_person','email_list']
line_format = "%(priority)-4.4s  %(expense_type)-10.10s  %(subtotal)10.10s  %(project)-16.16s  %(item_name)-20.20s  %(desc)-20.20s  %(people)6.6s  %(count)5.5s  %(costitem)10.10s"

def build_committees(infile=sys.stdin):
    committees = {}
    reader = csv.reader(infile)
    for comm in reader:
        email_list,chair_list,name,prefer_chair,area = comm
        if prefer_chair=='yes': prefer_chair = True
        else: prefer_chair = False
        committees[email_list] = { 'email_list': email_list, 'chair_list': chair_list, 'name': name, 'prefer_chair':prefer_chair, 'area':area}
    return committees

def do_populate_area_structure():
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
                        owner='ua-treasurer@mit.edu',
                        interested='ua-treasurer@mit.edu', )
        # This is sorta evil, in that it abuses the fact that Python
        # won't put name out of scope
        parent = BudgetArea.objects.get(name=name, depth=depth)
    return (depth, )

def do_populate_committees(committees):
    (depth,) = do_populate_area_structure()
    core = BudgetArea.objects.get(name='Core', depth=depth)
    comms = BudgetArea.objects.get(name='Committees', depth=depth)
    parents = {
        'Core':core,
        'Committees':comms,
    }
    for comm in committees.values():
        parent = parents[comm['area']]
        parent.add_child(
            name=comm['name'],
            owner=coerce_full_email(comm['chair_list']),
            interested=coerce_full_email(comm['email_list']),
            use_owner=comm['prefer_chair'],
            always=True,
        )
    return (depth+1, )

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

def main(committees_file, budget_file, term_name, ):
    term = vouchers.models.BudgetTerm.objects.get(name=term_name)
    committees = build_committees(committees_file,)
    (depth, ) = do_populate_committees(committees)
    do_process_rows(committees, budget_file, term, depth)

if __name__== '__main__':
    print "Syntax: %s committee_file format_file budget_file budget_term [override_address]" % (sys.argv[0], )
    committees_file = open(sys.argv[1])
    format_str = open(sys.argv[2]).read()
    budget_file = open(sys.argv[3])
    term = sys.argv[4]
    override_address = False
    if(len(sys.argv) > 5):
        override_address = sys.argv[5]
    main(committees_file, format_str, budget_file, term, override_address=override_address,)
