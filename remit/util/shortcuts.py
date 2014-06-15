from django.http import HttpResponseForbidden
from django.template import RequestContext, Template
from django.template.loader import get_template
from django.views.generic.base import TemplateView
from django.views.generic.list import ListView

def get_403_response(request, errmsg=None, **extra_context):
    tmpl = get_template('403.html')
    ctx = RequestContext(request, dict(errmsg=errmsg, **extra_context))
    page = tmpl.render(ctx, )
    return HttpResponseForbidden(page)


class ListViewWithContext(ListView):
    extra_context = {}

    # I believe .queryset will work out-of-the-box

    def get_context_data(self, **kwargs):
        context = super(ListViewWithContext,self).get_context_data(**kwargs)
        context.update(self.extra_context)
        return context


class TemplateViewWithContext(TemplateView):
    extra_context = {}

    def get_context_data(self, **kwargs):
        context = super(TemplateViewWithContext,self).get_context_data(**kwargs)
        print context
        context.update(self.extra_context)
