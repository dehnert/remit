from django.conf.urls.defaults import *
import treasury.vouchers.views

urlpatterns = patterns('',
    (r'^accounts/display_tree', treasury.vouchers.views.display_tree),
)
