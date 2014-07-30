import api.views
from rest_framework import status
from rest_framework.decorators import api_view
import uqx_api.courses
from collections import OrderedDict
import pycountry
import urllib2
import json
from api.models import UserEnrol

# Logging
import logging
logger = logging.getLogger(__name__)

@api_view(['GET'])
def meta_courses(request):
    """
    Lists the course information, in particular the course ID
    """
    if api.views.is_cached(request):
        return api.views.api_cacherender(request)
    courses = []
    for db in uqx_api.courses.EDX_DATABASES:
        if db == 'default':
            continue

        course = OrderedDict()
        course['id'] = db
        course['name'] = str(db).replace('_', ' ')
        course['icon'] = uqx_api.courses.EDX_DATABASES[db]['icon']
        courses.append(course)
    data = courses
    return api.views.api_render(request, data, status.HTTP_200_OK)


@api_view(['GET'])
def meta_courseinfo(request):
    """
    Lists the course information, in particular the course ID with extra information
    """
    if api.views.is_cached(request):
        return api.views.api_cacherender(request)
    courses = []
    for db in uqx_api.courses.EDX_DATABASES:
        if db == 'default':
            continue

        course = OrderedDict()
        course['id'] = db
        course['name'] = str(db).replace('_', ' ')
        course['icon'] = uqx_api.courses.EDX_DATABASES[db]['icon']

        coursedb = api.views.get_course(course['id'])

        filename = coursedb['dbname'].replace("_", "-")
        courseurl = 'https://tools.ceit.uq.edu.au/datasources/course_structure/'+filename+'.json';
        data = '[]'
        try:
            data = urllib2.urlopen(courseurl).read().replace('<script','').replace('</script>','')
        except:
            return api.views.api_render(request, {'error': 'Could not load course data'}, status.HTTP_404_NOT_FOUND)
        data = json.loads(data)
        if 'end' in data:
            course['end'] = data['end']
        if 'start' in data:
            course['start'] = data['start']
        if 'display_name' in data:
            course['display_name'] = data['display_name']

        course['enrolments'] = 9999
        course['enrolments_per_day'] = 3.4


        courses.append(course)
    data = courses
    return api.views.api_render(request, data, status.HTTP_200_OK)


@api_view(['GET'])
def meta_uniques(request):
    """
    The number of unique students for UQx courses
    """
    if api.views.is_cached(request):
        return api.views.api_cacherender(request)
    users = []
    total = 0
    for db in uqx_api.courses.EDX_DATABASES:
        if db == 'default':
            continue

        for user in UserEnrol.objects.using(db).all():
            total += 1
            if user.user_id not in users:
                users.append(user.user_id)
    data = OrderedDict()
    data['uniques'] = len(users)
    data['total'] = total
    return api.views.api_render(request, data, status.HTTP_200_OK)


@api_view(['GET'])
def meta_countries(request):
    """
    Lists the country codes and names
    """
    if api.views.is_cached(request):
        return api.views.api_cacherender(request)
    countries = list(pycountry.countries)
    data = OrderedDict()
    for country in countries:
        data[country.alpha2] = country.name
    return api.views.api_render(request, data, status.HTTP_200_OK)


@api_view(['GET'])
def meta_modes(request):
    """
    Lists the modes of enrolment
    """
    if api.views.is_cached(request):
        return api.views.api_cacherender(request)
    data = OrderedDict()
    data['blank'] = {'name': 'blank', 'description': ''}
    data['audit'] = {'name': 'audit', 'description': ''}
    data['honor'] = {'name': 'honor', 'description': ''}
    data['verified'] = {'name': 'verified', 'description': ''}
    return api.views.api_render(request, data, status.HTTP_200_OK)


@api_view(['GET'])
def meta_structure(request, course_id=''):

    """
    Returns a nested structure of the course structure for an edX course
    """
    if course_id is '':
        return api.views.api_render(request, {'error': 'Must supply a course ID'}, status.HTTP_400_BAD_REQUEST)
    if api.views.is_cached(request):
        return api.views.api_cacherender(request)

    course = api.views.get_course(course_id)
    if course is None:
        return api.views.api_render(request, {'error': 'Unknown course code'}, status.HTTP_404_NOT_FOUND)

    filename = course['dbname'].replace("_", "-")
    courseurl = 'https://tools.ceit.uq.edu.au/datasources/course_structure/'+filename+'.json';
    data = '[]'
    try:
        data = urllib2.urlopen(courseurl).read().replace('<script','').replace('</script>','')
    except:
        return api.views.api_render(request, {'error': 'Could not find course file'}, status.HTTP_404_NOT_FOUND)
    data = json.loads(data)
    return api.views.api_render(request, data, status.HTTP_200_OK)