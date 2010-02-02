from django.conf.urls.defaults import *
import finance_core.views

urlpatterns = patterns('',
    (r'^display_accounts', finance_core.views.display_tree),
)
