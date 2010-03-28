from decimal import Decimal
from django.db.models import Q, Sum
import finance_core.models

def build_table_annotate(line_items, primary_field, secondary_field, primary_axis, secondary_axis, ):
    # Setup
    arcprimary = {}
    arcsecondary = {}
    table = []
    zero = Decimal('0.00')
    for num, (pk, label, qobj, ) in enumerate(primary_axis):
        arcprimary[pk] = num
        table.append([zero]*len(secondary_axis))
    for num, (pk, label, qobj, ) in enumerate(secondary_axis):
        arcsecondary[pk] = num

    def lineitem_total(obj):
        if obj['amount__sum'] is None: return zero
        else: return obj['amount__sum']

    # Do the real work
    results = line_items.values(primary_field, secondary_field,).annotate(Sum('amount'))
    for result in results:
        pkey = arcprimary[result[primary_field]]
        skey = arcsecondary[result[secondary_field]]
        assert table[pkey][skey] == zero
        table[pkey][skey] = lineitem_total(result)

    return table

def build_table_aggregate(line_items, primary_field, secondary_field, primary_axis, secondary_axis):
    # This uses a simpler but probably slower method
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


def get_primary_axis(slug, base_area, term, ):
    if slug in axes and axes[slug][3]:
        return axes[slug][0:2] + (axes[slug][2](base_area, term, ), )
    else:
        raise NotImplementedError

def get_secondary_axis(slug, base_area, term, ):
    if slug in axes and axes[slug][4]:
        return axes[slug][0:2] + (axes[slug][2](base_area, term, ), )
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
        )
        for area in areas
    ]
    return axis

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
        )
        for term in terms
    ]
    return axis

def get_layers(base_area, term, ):
    axis = [
        (
            finance_core.models.layer_num(layer),
            finance_core.models.layer_name(layer),
            Q(layer=finance_core.models.layer_num(layer)),
        )
        for layer in finance_core.models.layers
    ]
    return axis

axes = {
    'budget-areas': ('Budget Areas', 'budget_area', get_budget_areas, True,  True,  ),
    'budget-terms': ('Budget Terms', 'budget_term', get_budget_terms, True,  True,  ),
    'layers':       ('Layers',       'layer',       get_layers,       True,  True,  ),
}

def append_totals(table):
    # Row totals
    for row in table:
        row.append(sum(row))
    # Column totals
    if len(table) > 0:
        totalrow = [None]*len(table[0])
        for col in xrange(len(table[0])):
            totalrow[col] = sum([row[col] for row in table])
        table.append(totalrow)
