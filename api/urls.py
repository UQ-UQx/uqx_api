from django.conf.urls import patterns, url

import views

urlpatterns = [url(r'^$', views.api_index, name='api_index'), url(r'^refresh_cache$', views.refresh_cache, name='refresh_cache'), url(r'^endpointlist', views.endpointlist, name='endpointlist')]

endpoints = views.endpoints()

for endpointkey in endpoints:
    endpoint = endpoints[endpointkey]
    urlpatterns.append(url(r'^'+endpoint['path']+'/$', getattr(views, endpointkey), name=endpointkey))
    if "option" in endpoint:
        option = '/(?P<'+endpoint['option']+'>[\w]+)'
        urlpatterns.append(url(r'^'+endpoint['path']+option+'/$', getattr(views, endpointkey), name=endpointkey+"_"+endpoint['option']))
        pass