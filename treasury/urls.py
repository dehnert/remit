from django.conf.urls.defaults import *

# Necessary views
import treasury.finance_core.views

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Example:
    (r'^accounts/display_tree', treasury.finance_core.views.display_tree),
    (r'^vouchers/', include('treasury.vouchers.urls')),
    (r'^finance_core/', include('treasury.finance_core.urls')),

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    (r'^admin/(.*)', admin.site.root),
)
