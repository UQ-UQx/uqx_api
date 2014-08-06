from django.views.decorators.csrf import csrf_exempt
from django.core.cache import cache
import sys
from datetime import timedelta
from uqx_api import settings
from rest_framework.permissions import AllowAny

# APIs
from rest_framework.response import Response
from rest_framework.reverse import reverse

# Endpoints
from api.apis.meta import *
from api.apis.students import *
from api.apis.discussions import *
from api.apis.downloads import *
from api.apis.videos import *

# Logging
import logging
logger = logging.getLogger(__name__)


@csrf_exempt
@api_view(('GET',))
@permission_classes((AllowAny, ))
def api_index(request, theformat=None):
    """
    Lists the currently available API endpoints.
    """
    endpointlist = OrderedDict()
    the_endpoints = endpoints()
    for endpoint_key in the_endpoints:
        firstlevel = str(endpoint_key).split('_')[0]
        if firstlevel not in endpointlist:
            endpointlist[firstlevel] = OrderedDict()
        endpoint = the_endpoints[endpoint_key]
        if 'requirevar' not in endpoint or 'requirevar' == False:
            endpointlist[firstlevel][endpoint['path']] = reverse(endpoint_key, request=request, format=theformat)
        if "option" in endpoint:
            optionname = "<"+endpoint['option']+">"
            endpointlist[firstlevel][endpoint['path']+"/"+optionname] = reverse(endpoint_key+"_"+endpoint['option'], request=request, format=theformat, kwargs={endpoint['option']: ''+endpoint['option']})
            pass
    return Response(endpointlist)


# The list of endpoints available
def endpoints():
    points = OrderedDict()

    points['student_genders'] = {'path': 'students/genders', 'option': 'course_id'}
    points['student_ages'] = {'path': 'students/ages', 'option': 'course_id'}
    points['student_educations'] = {'path': 'students/educations', 'option': 'course_id'}
    points['student_countries'] = {'path': 'students/countries', 'option': 'course_id'}
    points['student_modes'] = {'path': 'students/modes', 'option': 'course_id'}
    points['student_dates'] = {'path': 'students/dates', 'option': 'course_id'}
    points['student_active'] = {'path': 'students/active', 'option': 'course_id'}
    points['student_activity'] = {'path': 'students/student_activity', 'option': 'course_id', 'requirevar': True}

    points['discussion_countries'] = {'path': 'discussions/countries', 'option': 'course_id'}
    points['discussion_dates'] = {'path': 'discussions/dates', 'option': 'course_id', 'requirevar': True}
    points['discussion_popular'] = {'path': 'discussions/popular', 'option': 'course_id'}
    points['discussion_top'] = {'path': 'discussions/top', 'option': 'course_id'}
    points['discussion_category'] = {'path': 'discussions/category', 'option': 'course_id', 'requirevar': True}

    points['download_os'] = {'path': 'downloads/os'}
    points['download_browsers'] = {'path': 'downloads/browsers'}
    points['download_countries'] = {'path': 'downloads/countries'}

    points['meta_courses'] = {'path': 'meta/courses'}
    points['meta_courseinfo'] = {'path': 'meta/courseinfo'}
    points['meta_uniques'] = {'path': 'meta/uniques'}
    points['meta_structure'] = {'path': 'meta/structure', 'option': 'course_id', 'requirevar': True}
    points['meta_countries'] = {'path': 'meta/countries'}
    points['meta_modes'] = {'path': 'meta/modes'}

    points['videos_views'] = {'path': 'videos/views', 'option': 'course_id', 'requirevar': True}
    logger.info("Getting endpoints")
    return points

@api_view(('GET',))
def refresh_cache(request):
    response = {'refreshed': 'true'}
    the_endpoints = endpoints()
    virtual_request = request
    virtual_request.refreshcache = True
    basepath = request.path.replace("refresh_cache","")
    for endpoint in the_endpoints:
        #if endpoint == 'student_genders':
        if 'requirevar' not in endpoint or 'requirevar' is False:
            request.path = basepath + the_endpoints[endpoint]['path']
            getattr(sys.modules[__name__], endpoint)(virtual_request)
            break
        if "option" in the_endpoints[endpoint]:
            if the_endpoints[endpoint]['option'] == 'course_id':
                courses = get_all_courses()
                for course in courses:
                    request.path = basepath + the_endpoints[endpoint]['path']+"/"+course
                    getattr(sys.modules[__name__], endpoint)(virtual_request)
    response['cachetime'] = settings.CACHES['default']['TIMEOUT']
    now = datetime.now()
    response['nextrefresh'] = now + timedelta(0, settings.CACHES['default']['TIMEOUT'])
    return Response(response)

# Private Methods

def api_render(request, data, response_status=status.HTTP_200_OK):
    if not is_cached(request):
        cache_save(cache_path(request), data)
    return Response(data, response_status)


def api_cacherender(request):
    return api_render(request, cache_get(cache_path(request)), status.HTTP_200_OK)


def is_cached(request):
    if cache.get(cache_path(request)):
        if 'refreshcache' in request.QUERY_PARAMS or hasattr(request, 'refreshcache') and request.refreshcache:
            logger.info("Refreshing Cache")
            return False
        return True
    return False


def get_course(course_id):
    if course_id in uqx_api.courses.EDX_DATABASES:
        return uqx_api.courses.EDX_DATABASES[course_id]
    return None


def get_all_courses():
    courses = dict(uqx_api.courses.EDX_DATABASES)
    del courses['default']
    return courses


def cache_save(path, data):
    logger.info("Saving cache for path "+fixpath(path)+", times out in "+str(settings.CACHES['default']['TIMEOUT']))
    cache.set(fixpath(path), data, settings.CACHES['default']['TIMEOUT'])
    pass


def cache_get(path):
    logger.info("Retrieving cache for path "+fixpath(path)+", times out in "+str(settings.CACHES['default']['TIMEOUT']))
    return cache.get(fixpath(path))


def cache_path(request):
    return str(fixpath(request.path))


def fixpath(path):
    return path.rstrip('\/')
