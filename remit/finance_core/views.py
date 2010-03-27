from django.http import HttpResponse
import finance_core.models
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.http import Http404, HttpResponseRedirect
from django.db.models import Q
from decimal import Decimal
import finance_core.reporting

def display_tree(request):
    root = finance_core.models.BudgetArea.get_by_path(['Accounts'])
    return HttpResponse(root.dump_to_html())

def reporting(request):
    line_items = finance_core.models.LineItem.objects.all()
    term_name = 'All'
    compute_method = 'default'

    # Main limit to lineitems, relative to primary axis
    main_lineitem_limit_primary = Q()
    if 'compute_method' in request.REQUEST:
        compute_method = request.REQUEST['compute_method']
    if 'term' in request.REQUEST:
        term_obj = get_object_or_404(finance_core.models.BudgetTerm, slug=request.REQUEST['term'])
        term_name = term_obj.name
        line_items = line_items.filter(budget_term=term_obj)
        main_lineitem_limit_primary = Q(lineitem__budget_term=term_obj)
    if 'area' in request.REQUEST:
        base_area_obj = get_object_or_404(finance_core.models.BudgetArea, pk=request.REQUEST['area'])
    else:
        base_area_obj = finance_core.models.BudgetArea.get_by_path(['Accounts'])
    line_items = line_items.filter(budget_area__in=base_area_obj.get_descendants())

    # Initialize the axis
    # Primary
    if 'primary' in request.REQUEST:
        primary_slug = request.REQUEST['primary']
    else:
        primary_slug = 'budget-areas'
    try:
        primary_name, primary_axis, primary_axis_objs = finance_core.reporting.get_primary_axis(primary_slug, base_area_obj, )
    except NotImplementedError:
        raise Http404("Primary axis %s is not implemented" % primary_slug)

    # Secondary
    if 'secondary' in request.REQUEST:
        secondary_slug = request.REQUEST['secondary']
    else:
        secondary_slug = 'layers'
    try:
        secondary_name, secondary_axis, secondary_axis_obj = finance_core.reporting.get_secondary_axis(secondary_slug, base_area_obj, )
    except NotImplementedError:
        raise Http404("Secondary axis %s is not implemented" % secondary_slug)
    secondary_axis.append((None, 'Total', Q(), Q()))

    primary_labels = [ ]
    for num, (pk, label, qobj, objrel_qobj, ) in enumerate(primary_axis):
        primary_labels.append(label)
    secondary_labels = [ secondary[1] for secondary in secondary_axis ]

    # Do the computation
    compute_methods = {
        'default':   finance_core.reporting.build_table,
        'aggregate': finance_core.reporting.build_table_aggregate,
        'annotate':  finance_core.reporting.build_table_annotate,
    }
    if compute_method in compute_methods:
        build_table = compute_methods[compute_method]
    else:
        raise Http404("Unknown compute_method selected")
    table = build_table(line_items, main_lineitem_limit_primary, primary_axis, primary_axis_objs, secondary_axis, )

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
