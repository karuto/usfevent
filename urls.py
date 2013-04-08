from django.conf.urls.defaults import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'usfevent.views.home', name='home'),
    # url(r'^usfevent/', include('usfevent.foo.urls')),

	url(r'^events/', 'event.views.index'),

    # url(r'^$', 'accounts.views.index',name="index"),
    url(r'^accounts/index$', 'accounts.views.index',name="accounts_index"),
    url(r'^accounts/register$', 'accounts.views.register',name="register"),
    url(r'^accounts/login$', 'accounts.views.login',name="login"),
    url(r'^accounts/logout$', 'accounts.views.logout',name="logout"),

	url(r'^admin/', include(admin.site.urls)),
)
