from django.http import HttpResponse
import finance_core.models
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.http import Http404, HttpResponseRedirect
from django.db.models import Q, Sum
from decimal import Decimal

def display_tree(request):
    root = finance_core.models.BudgetArea.get_by_path(['Accounts'])
    return HttpResponse(root.dump_to_html())

def reporting(request):
    line_items = finance_core.models.LineItem.objects.all()
    term_name = 'All'
    term_primary_Q = Q()
    if 'term' in request.REQUEST:
        term_obj = get_object_or_404(finance_core.models.BudgetTerm, slug=request.REQUEST['term'])
        term_name = term_obj.name
        line_items = line_items.filter(budget_term=term_obj)
        term_primary_Q = Q(lineitem__budget_term=term_obj)
    if 'area' in request.REQUEST:
        base_area_obj = get_object_or_404(finance_core.models.BudgetArea, pk=request.REQUEST['area'])
    else:
        base_area_obj = finance_core.models.BudgetArea.get_by_path(['Accounts'])
    line_items = line_items.filter(budget_area__in=base_area_obj.get_descendants())
    base_area_depth = base_area_obj.depth
    print base_area_obj

    primary_name = 'Budget Areas'
    primary_axis = [
        (area.pk, area.indented_name(base_area_depth), Q(budget_area=area), ) for area in base_area_obj.get_descendants()
    ]
    primary_axis_objs = base_area_obj.get_descendants()
    secondary_name = 'Layers'
    secondary_axis = [
        (
            finance_core.models.layer_name(layer),
            Q(layer=finance_core.models.layer_num(layer)),
            Q(lineitem__layer=finance_core.models.layer_num(layer)),
        )
        for layer in finance_core.models.layers
    ]

    secondary_axis.append(('Total', Q(), Q()))

    primary_labels = [ ]
    arcprimary = {}
    table = []
    zero = Decimal('0.00')
    for num, (pk, label, qobj, ) in enumerate(primary_axis):
        primary_labels.append(label)
        arcprimary[pk] = num
        table.append([zero]*len(secondary_axis))
    print arcprimary

    secondary_labels = [ secondary[0] for secondary in secondary_axis ]

    def lineitem_total(obj):
        if obj.lineitem__amount__sum is None: return zero
        else: return obj.lineitem__amount__sum
    for num, (label, qobj_lineitem, qobj_primary) in enumerate(secondary_axis):
        secondary_results = (primary_axis_objs.filter(qobj_primary, term_primary_Q).annotate(Sum('lineitem__amount')))
        for cell in secondary_results:
            print cell, cell.pk, arcprimary[cell.pk], num, table[arcprimary[cell.pk]]
            table[arcprimary[cell.pk]][num] = lineitem_total(cell)

    slow = False
    if slow:
        # This uses a simpler but probably slower method
        # In theory, if we grow unit tests, comparing this method with
        # the one above using annotate would be a good idea
        def total_amount(queryset):
            amount = queryset.aggregate(Sum('amount'))['amount__sum']
            if amount is None: return zero
            else: return amount
        table = [ # Primary axis
                [ # Secondary axis
                    total_amount(line_items.filter(primary[1], secondary[1]))
                for secondary in secondary_axis]
            for primary in primary_axis]

    debug = False
    if debug:
        from django.db import connection
        print connection.queries
        print "Number of queries:\t%d" % (len(connection.queries),)
        print "Table size:\t%dx%d" % (len(primary_labels), len(secondary_labels), )

    context = {
        'pagename':'reporting',
        'term_name': term_name,
        'area': base_area_obj,
        'primary_name': primary_name,
        'secondary_name': secondary_name,
        'primary_labels': primary_labels,
        'secondary_labels': secondary_labels,
        'table': table,
        'table_with_row_labels': zip(primary_labels, table),
    }
    return render_to_response('finance_core/reporting.html', context, context_instance=RequestContext(request), )
