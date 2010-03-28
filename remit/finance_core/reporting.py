from decimal import Decimal
from django.db.models import Q, Sum
import finance_core.models

def build_table_annotate(line_items, main_lineitem_limit_primary, primary_axis, primary_axis_objs, secondary_axis, ):
    # Setup
    arcprimary = {}
    table = []
    zero = Decimal('0.00')
    for num, (pk, label, qobj, objrel_qobj) in enumerate(primary_axis):
        arcprimary[pk] = num
        table.append([zero]*len(secondary_axis))

    def lineitem_total(obj):
        if obj.lineitem__amount__sum is None: return zero
        else: return obj.lineitem__amount__sum

    # Do the real work
    for num, (pk, label, qobj_lineitem, qobj_primary) in enumerate(secondary_axis):
        secondary_results = (primary_axis_objs.filter(main_lineitem_limit_primary, qobj_primary, ).annotate(Sum('lineitem__amount')))
        for cell in secondary_results:
            #print cell, cell.pk, arcprimary[cell.pk], num, table[arcprimary[cell.pk]]
            table[arcprimary[cell.pk]][num] = lineitem_total(cell)

    return table

def build_table_valannotate(line_items, primary_field, secondary_field, primary_axis, secondary_axis, ):
    # Setup
    arcprimary = {}
    arcsecondary = {}
    table = []
    zero = Decimal('0.00')
    for num, (pk, label, qobj, objrel_qobj) in enumerate(primary_axis):
        arcprimary[pk] = num
        table.append([zero]*len(secondary_axis))
    for num, (pk, label, qobj, objrel_qobj) in enumerate(secondary_axis):
        arcsecondary[pk] = num

    def lineitem_total(obj):
        if obj['amount__sum'] is None: return zero
        else: return obj['amount__sum']

    # Do the real work
    results = line_items.values(primary_field, secondary_field,).annotate(Sum('amount'))
    for result in results:
        print result
        table[arcprimary[result[primary_field]]][arcsecondary[result[secondary_field]]] = lineitem_total(result)
    #for num, (pk, label, qobj_lineitem, qobj_primary) in enumerate(secondary_axis):
    #    secondary_results = (primary_axis_objs.filter(main_lineitem_limit_primary, qobj_primary, ).annotate(Sum('lineitem__amount')))
    #    for cell in secondary_results:
    #        #print cell, cell.pk, arcprimary[cell.pk], num, table[arcprimary[cell.pk]]
    #        table[arcprimary[cell.pk]][num] = lineitem_total(cell)

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
                total_amount(line_items.filter(primary[2], secondary[2]))
            for secondary in secondary_axis]
        for primary in primary_axis]

    return table

build_table = build_table_annotate
build_table = build_table_aggregate


def get_primary_axis(slug, base_area, term, ):
    if slug in axes and axes[slug][3]:
        return axes[slug][0:2] + axes[slug][2](base_area, term, )
    else:
        raise NotImplementedError

def get_secondary_axis(slug, base_area, term, ):
    if slug in axes and axes[slug][4]:
        return axes[slug][0:2] + axes[slug][2](base_area, term, )
    else:
        raise NotImplementedError

def get_budget_areas(base_area, term, ):
    base_area_depth = base_area.depth
    areas = base_area.get_descendants()
    if term:
        areas = areas.filter(Q(always=True) | Q(budget_term=term))
    axis = [
        (
            area.pk,
            area.indented_name(base_area_depth),
            Q(budget_area=area),
            Q(lineitem__budget_area=area),
        )
        for area in areas
    ]
    axis_objs = areas
    return axis, axis_objs,

def get_budget_terms(base_area, term, ):
    if term:
        terms = finance_core.models.BudgetTerm.objects.filter(pk=term.pk)
    else:
        terms = finance_core.models.BudgetTerm.objects.all()
    axis = [
        (
            term.pk,
            term.name,
            Q(budget_term=term),
            Q(lineitem__budget_term=term),
        )
        for term in terms
    ]
    return axis, terms

def get_layers(base_area, term, ):
    axis = [
        (
            finance_core.models.layer_num(layer),
            finance_core.models.layer_name(layer),
            Q(layer=finance_core.models.layer_num(layer)),
            Q(lineitem__layer=finance_core.models.layer_num(layer)),
        )
        for layer in finance_core.models.layers
    ]
    return axis, None,

axes = {
    'budget-areas': ('Budget Areas', 'budget_area', get_budget_areas, True,  True,  ),
    'budget-terms': ('Budget Terms', 'budget_term', get_budget_terms, True,  True,  ),
    'layers':       ('Layers',       'layer',       get_layers,       False, True,  ),
}

