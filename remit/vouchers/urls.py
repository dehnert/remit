from django.conf.urls.defaults import *
from django.views.generic.list_detail import object_list
from django.contrib.auth.decorators import permission_required
import vouchers.views
import vouchers.models

urlpatterns = patterns('',
    url(r'list/', permission_required('vouchers.can_list')(object_list),
        kwargs={'queryset': vouchers.models.ReimbursementRequest.objects.all()},
        name='list_requests',
    ),
    url(r'reimbursement/', 'vouchers.views.select_request_basics', name='request_reimbursement', ),
    (r'submit/(?P<term>[\d\w-]+)/(?P<committee>[\d\w-]+)/', 'vouchers.views.submit_request', ),
    url(r'review/(?P<object_id>\d+)/', 'vouchers.views.review_request', name='review_request', ),
)
