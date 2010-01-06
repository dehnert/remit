from django.conf.urls.defaults import *
import treasury.vouchers.views

urlpatterns = patterns('',
    (r'submit/(?P<term>[\d\w-]+)/(?P<committee>[\d\w-]+)/', 'treasury.vouchers.views.submit_request', )
)
