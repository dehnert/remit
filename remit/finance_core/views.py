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

@user_passes_test(lambda u: u.has_perm('finance_core.use_reporting'))
def reporting(request):
    compute_method = 'default'
    if 'compute_method' in request.REQUEST:
        compute_method = request.REQUEST['compute_method']

    ###############################
    # Retrieve the various limits #
    ###############################
    line_items = finance_core.models.LineItem.objects.all()

    # Term
    if 'term' in request.REQUEST and not request.REQUEST['term'] == 'all':
        term_obj = get_object_or_404(finance_core.models.BudgetTerm, slug=request.REQUEST['term'])
        term_name = term_obj.name
        line_items = line_items.filter(budget_term=term_obj)
    else:
        term_obj = None
        term_name = 'All'

    # Area
    if 'area' in request.REQUEST:
        base_area_obj = get_object_or_404(finance_core.models.BudgetArea, pk=request.REQUEST['area'])
    else:
        base_area_obj = finance_core.models.BudgetArea.get_by_path(['Accounts'])
    all_relevant_areas = base_area_obj.get_descendants()
    if term_obj:
        all_relevant_areas = all_relevant_areas.filter(Q(always=True) | Q(budget_term=term_obj))
    line_items = line_items.filter(budget_area__in=all_relevant_areas)

    # Layer
    if 'layer' in request.REQUEST and request.REQUEST['layer'] != 'all':
        try:
            layer_id = int(request.REQUEST['layer'])
            layer = finance_core.models.get_layer_by_num(layer_id)
        except KeyError:
            raise Http404("Invalid layer %s request" % request.REQUEST['layer'])
        line_items = line_items.filter(layer=layer_id)
    else:
        layer = 'all'

    #######################
    # Initialize the axes #
    #######################
    # Primary
    if 'primary' in request.REQUEST:
        primary_slug = request.REQUEST['primary']
    else:
        primary_slug = 'budget-areas'
    try:
        primary_name, primary_field, primary_axis = finance_core.reporting.get_primary_axis(primary_slug, base_area_obj, term_obj, )
    except NotImplementedError:
        raise Http404("Primary axis %s is not implemented" % primary_slug)

    # Secondary
    if 'secondary' in request.REQUEST:
        secondary_slug = request.REQUEST['secondary']
    else:
        secondary_slug = 'layers'
    try:
        secondary_name, secondary_field, secondary_axis = finance_core.reporting.get_secondary_axis(secondary_slug, base_area_obj, term_obj, )
    except NotImplementedError:
        raise Http404("Secondary axis %s is not implemented" % secondary_slug)

    primary_labels = [ ]
    for num, (pk, label, qobj, ) in enumerate(primary_axis):
        primary_labels.append(label)
    secondary_labels = [ secondary[1] for secondary in secondary_axis ]

    ######################
    # Do the computation #
    ######################
    compute_methods = {
        'default':   finance_core.reporting.build_table,
        'aggregate': finance_core.reporting.build_table_aggregate,
        'annotate':  finance_core.reporting.build_table_annotate,
    }
    if compute_method in compute_methods:
        build_table = compute_methods[compute_method]
    else:
        raise Http404("Unknown compute_method selected")
    table = build_table(line_items, primary_field, secondary_field, primary_axis, secondary_axis, )
    finance_core.reporting.append_totals(table)
    primary_labels.append("Total")
    secondary_labels.append("Total")

    debug = True
    debug = False
    if debug:
        from django.db import connection
        print connection.queries
        print "Number of queries:\t%d" % (len(connection.queries),)
        print "Table size:\t%dx%d" % (len(primary_labels), len(secondary_labels), )

    ##########
    # Render #
    ##########
    term_options = finance_core.models.BudgetTerm.objects.all()
    area_options = finance_core.models.BudgetArea.objects.filter(always=True)
    context = {
        'pagename':'reporting',
        'term_name': term_name,
        'term_options': term_options,
        'area': base_area_obj,
        'area_options': area_options,
        'layer': layer,
        'layer_options': finance_core.models.layers,
        'axes': finance_core.reporting.axes,
        'primary_name': primary_name,
        'secondary_name': secondary_name,
        'primary_labels': primary_labels,
        'secondary_labels': secondary_labels,
        'table': table,
        'table_with_row_labels': zip(primary_labels, table),
    }
    return render_to_response('finance_core/reporting.html', context, context_instance=RequestContext(request), )
