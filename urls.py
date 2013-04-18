from django.conf import settings
from django.conf.urls.defaults import patterns, include, url
from django.conf.urls.static import static

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'usfevent.views.home', name='home'),
    # url(r'^usfevent/', include('usfevent.foo.urls')),
    
    url(r'^$', 'accounts.views.index', name="index"),

    url(r'^events/', include('event.urls')),
    url(r'^user/', include('accounts.urls')),

    url(r'^admin/', include(admin.site.urls)),

)

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
