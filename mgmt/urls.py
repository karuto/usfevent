from django.conf.urls.defaults import patterns, include, url
from mgmt import views

urlpatterns = patterns('mgmt.views',

    url(r'^init/$', 'db_init', name="db_init"),
    url(r'^$', 'overview', name="overview"),
    url(r'^approve_user/(?P<pk>\d+)$', 'approve_user', name="approve_user"),
    url(r'^approve_event/(?P<pk>\d+)$', 'approve_event', name="approve_event"),
)
