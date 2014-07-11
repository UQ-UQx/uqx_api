from django.conf.urls import patterns, include, url

from django.contrib import admin
from api import views
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'uqx_api.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^api/', include('api.urls')),
    url(r'^', include('api.urls', namespace='api')),
    url(r'^oauth2/', include('provider.oauth2.urls', namespace='oauth2')),
)
