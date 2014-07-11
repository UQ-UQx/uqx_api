import api.views
from rest_framework import status
from rest_framework.decorators import api_view
from api.models import Log


@api_view(['GET'])
def download_os(request):
    """
    Returns a count of operating systems which have downloaded videos from the file server (not including youtube)
    """
    if api.views.is_cached(request):
        return api.views.api_cacherender(request)

    data = Log.countfield('request_header_user_agent__os__family',False,"online_access_logs")
    return api.views.api_render(request, data, status.HTTP_200_OK)


@api_view(['GET'])
def download_browsers(request):
    """
    Returns a count of browsers which have downloaded videos from the file server (not including youtube)
    """
    if api.views.is_cached(request):
        return api.views.api_cacherender(request)
    data = Log.countfield('request_header_user_agent__browser__family',False,"online_access_logs")
    return api.views.api_render(request, data, status.HTTP_200_OK)


@api_view(['GET'])
def download_countries(request):
    """
    Returns a count of countries which have downloaded videos from the file server (not including youtube)
    """
    if api.views.is_cached(request):
        return api.views.api_cacherender(request)
    data = Log.countfield('country',False,"online_access_logs")
    return api.views.api_render(request, data, status.HTTP_200_OK)