from django.http import HttpResponseForbidden
from django.template import RequestContext, Template
from django.template.loader import get_template

def get_403_response(request, errmsg=None, **extra_context):
    tmpl = get_template('403.html')
    ctx = RequestContext(request, dict(errmsg=errmsg, **extra_context))
    page = tmpl.render(ctx, )
    return HttpResponseForbidden(page)
