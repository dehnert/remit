#!/usr/bin/python

import collections
import csv
import re
import sys

columns = ['blank1', 'account', 'budget', 'current', 'ytd', 'cumulative', 'unexpended', 'commitment', 'uncommitted', 'blank2', 'blank3', ]
output_cols = ['category', 'account', 'amount', ]

re_account = re.compile(r"       ?(?P<num>\d+) - (?P<name>.*)")

def import_sap_summary(summary_fd, account_fd, output_fd):
    account_reader = csv.DictReader(account_fd, dialect='excel-tab')
    account_map = {}
    cat_totals = collections.defaultdict(float)
    for row in account_reader:
        account_map[row['account']] = row['category']
    reader = csv.DictReader(summary_fd, dialect='excel-tab', fieldnames=columns, restkey='extras')
    writer = csv.writer(output_fd, )
    for row in reader:
        account = row['account']
        match = re_account.match(account)
        if match:
            account_num, account_name = match.groups()
            if account_name in account_map:
                cat_totals[account_map[account_name]] += float(row['ytd'].strip())
                #writer.writerow((account_map[account_name], account, row['ytd'].strip()))
                #print "Good row     '%s'" % (account, )
            else:
                amount = float(row['ytd'].strip())
                if amount != 0.0:
                    print "%s\t%s\t%f" % ("Misc", account_name, amount)
        else:
            print "Ignoring row '%s'" % (account, )
        if 'extras' in row: print >>sys.stderr, row
        if 'blank3' not in row: print >>sys.stderr, row
    writer.writerow(['category','amount'])
    for key, val in cat_totals.items():
        writer.writerow((key, val))

if __name__ == '__main__':
    summary_fd = open(sys.argv[1], 'r')
    account_fd = open(sys.argv[2], 'r')
    output_fd  = open(sys.argv[3], 'w')
    import_sap_summary(summary_fd, account_fd, output_fd)
