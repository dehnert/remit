from decimal import Decimal
from django.db.models import Sum

def build_table_annotate(line_items, main_lineitem_limit_primary, primary_axis, primary_axis_objs, secondary_axis, ):
    # Setup
    arcprimary = {}
    table = []
    zero = Decimal('0.00')
    for num, (pk, label, qobj, ) in enumerate(primary_axis):
        arcprimary[pk] = num
        table.append([zero]*len(secondary_axis))

    def lineitem_total(obj):
        if obj.lineitem__amount__sum is None: return zero
        else: return obj.lineitem__amount__sum

    # Do the real work
    print secondary_axis
    for num, (label, qobj_lineitem, qobj_primary) in enumerate(secondary_axis):
        print num
        secondary_results = (primary_axis_objs.filter(main_lineitem_limit_primary, qobj_primary, ).annotate(Sum('lineitem__amount')))
        for cell in secondary_results:
            #print cell, cell.pk, arcprimary[cell.pk], num, table[arcprimary[cell.pk]]
            table[arcprimary[cell.pk]][num] = lineitem_total(cell)

    return table

def build_table_aggregate(line_items, main_lineitem_limit_primary, primary_axis, primary_axis_objs, secondary_axis):
    # This uses a simpler but probably slower method
    # In theory, if we grow unit tests, comparing this method with
    # the one above using annotate would be a good idea
    zero = Decimal('0.00')
    def total_amount(queryset):
        amount = queryset.aggregate(Sum('amount'))['amount__sum']
        if amount is None: return zero
        else: return amount
    table = [ # Primary axis
            [ # Secondary axis
                total_amount(line_items.filter(primary[2], secondary[1]))
            for secondary in secondary_axis]
        for primary in primary_axis]

    return table
    

build_table = build_table_annotate
