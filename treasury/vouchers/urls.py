from django.conf.urls.defaults import *
import treasury.vouchers.views

urlpatterns = patterns('',
    (r'reimbursement/', 'vouchers.views.select_request_basics', ),
    (r'submit/(?P<term>[\d\w-]+)/(?P<committee>[\d\w-]+)/', 'vouchers.views.submit_request', ),
    (r'review/(?P<object_id>\d+)/', 'vouchers.views.review_request', ),
)
