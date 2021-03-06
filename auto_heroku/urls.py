from django.conf.urls import patterns, include, url
from django.conf import settings

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    url(r'^$', 'auto.views.home', name='home'),
    url(r'^work/$', 'auto.views.work', name='work'),
    url(r'^delete/$', 'auto.views.delete', name='delete'),
    url(r'^logs/(?P<appname>[\w\d\-]+)/$', 'auto.views.logs', name='logs'),

    # url(r'^auto_heroku/', include('auto_heroku.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),

)

urlpatterns += patterns('',
                        (r'^static/(?P<path>.*)$', 'django.views.static.serve',
                         {'document_root': settings.STATIC_ROOT}),)
