from django.conf.urls.defaults import patterns, include, url
from mgmt import views

urlpatterns = patterns('mgmt.views',

    url(r'^init/$', 'db_init', name="init"),
    url(r'^$', 'overview', name="overview"),
    url(r'^approve/(?P<pk>\d+)$', 'approve_user', name="approve_user"),
)
