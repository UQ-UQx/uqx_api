import api.views
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
import uqx_api.courses
from collections import OrderedDict
import pycountry
import urllib2
import json
import datetime
from api.models import UserEnrol, CourseProfile, UserCertificate, PersonCourse, Ingestor
import dateutil
from rest_framework.permissions import AllowAny
import config

# Logging
import logging
logger = logging.getLogger(__name__)

@api_view(['GET'])
@permission_classes((AllowAny, ))
def meta_courses(request):
    """
    Lists the course information, in particular the course ID
    """
    if api.views.is_cached(request):
        return api.views.api_cacherender(request)
    courses = []
    for db in uqx_api.courses.EDX_DATABASES:
        if db == 'default' or db == 'personcourse':
            continue

        course = OrderedDict()
        course['id'] = db
        course['name'] = str(db).replace('_', ' ')
        course['icon'] = uqx_api.courses.EDX_DATABASES[db]['icon']
        course['year'] = uqx_api.courses.EDX_DATABASES[db]['year']
        courses.append(course)
    data = courses
    return api.views.api_render(request, data, status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes((AllowAny, ))
def meta_courseinfo(request):
    """
    Lists the course information, in particular the course ID with extra information
    """
    if api.views.is_cached(request):
        return api.views.api_cacherender(request)
    courses = []
    for db in uqx_api.courses.EDX_DATABASES:
        if db == 'default' or db == 'personcourse':
            continue

        course = OrderedDict()
        course['id'] = db
        course['name'] = str(db).replace('_', ' ')
        course['icon'] = uqx_api.courses.EDX_DATABASES[db]['icon']
        course['year'] = uqx_api.courses.EDX_DATABASES[db]['year']

        coursedb = api.views.get_course(course['id'])

        filename = coursedb['dbname'].replace("_", "-")
        courseurl = config.SERVER_URL + '/datasources/course_structure/'+filename+'.json';
        data = '[]'
        try:
            data = urllib2.urlopen(courseurl).read().replace('<script','').replace('</script>','')
        except:
            return api.views.api_render(request, {'error': 'Could not load course data'}, status.HTTP_404_NOT_FOUND)
        data = json.loads(data)
        max_per_day_date = datetime.datetime.now()
        if 'end' in data:
            course['end'] = data['end']
        if 'start' in data:
            course['start'] = data['start']
            max_per_day_date = dateutil.parser.parse(data['start']) + datetime.timedelta(days=7)
        if 'display_name' in data:
            course['display_name'] = data['display_name']
        max_per_day_date = max_per_day_date.replace(tzinfo=None)
        total = 0
        within_per_day = 0
        certificates = 0
        first_date = datetime.datetime.now()
        for user in UserEnrol.objects.using(db).all():
            userdate = user.created.replace(tzinfo=None)
            if first_date > userdate:
                first_date = userdate
            if userdate < max_per_day_date:
                within_per_day += 1
            total += 1
            certificates += 1

        certificates = len(UserCertificate.objects.using(db).filter(status='downloadable'))

        range = (max_per_day_date - first_date).days

        per_day = round(within_per_day/range, 2)

        course['enrolments'] = total
        course['enrolments_per_day'] = per_day
        course['certificates'] = certificates
        courses.append(course)
    data = courses
    return api.views.api_render(request, data, status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes((AllowAny, ))
def meta_uniques(request):
    """
    The number of unique students for UQx courses
    """
    if api.views.is_cached(request):
        return api.views.api_cacherender(request)
    users = []
    total = 0
    for db in uqx_api.courses.EDX_DATABASES:
        if db == 'default' or db == 'personcourse':
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
@permission_classes((AllowAny, ))
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
@permission_classes((AllowAny, ))
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
    courseurl = config.SERVER_URL + '/datasources/course_structure/'+filename+'.json'
    data = '[]'
    try:
        data = urllib2.urlopen(courseurl).read().replace('<script', '').replace('</script>', '')
    except:
        return api.views.api_render(request, {'error': 'Could not find course file'}, status.HTTP_404_NOT_FOUND)
    data = json.loads(data)
    return api.views.api_render(request, data, status.HTTP_200_OK)

@api_view(['GET'])
def meta_courseprofile(request, course_id='all'):
    """
    Returns derived course profiles for a course
    """
    if api.views.is_cached(request):
        return api.views.api_cacherender(request)
    courses = []
    if course_id is 'all':
        courselist = api.views.get_all_courses()
        for course in courselist:
            courses.append(courselist[course]['id'])
        pass
    else:
        course = api.views.get_course(course_id)
        if course is None:
            return api.views.api_render(request, {'error': 'Unknown course code'}, status.HTTP_404_NOT_FOUND)
        courses.append(course['id'])

    data = {}

    for course in courses:
        data[course] = {}
        course_data = CourseProfile.objects.using("personcourse").filter(course=course)
        if len(course_data) > 0:
            data[course] = course_data[0].to_dict(None)
            data[course]['status'] = 'available'
        else:
            data[course]['status'] = 'unavailable'

    return api.views.api_render(request, data, status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes((AllowAny, ))
def meta_enrolcount(request, course_id='all'):
    """
    Returns the enrolment count over the last week
    """
    if api.views.is_cached(request):
        return api.views.api_cacherender(request)
    data = OrderedDict()

    courses = []
    if course_id is 'all':
        courselist = api.views.get_all_courses()
        for course in courselist:
            courses.append(courselist[course]['id'])
        pass
    else:
        course = api.views.get_course(course_id)
        if course is None:
            return api.views.api_render(request, {'error': 'Unknown course code'}, status.HTTP_404_NOT_FOUND)
        courses.append(course_id)

    day_students = 0
    week_students = 0
    month_students = 0

    for course in courses:

        last_date = None
        PersonCourse._meta.db_table = 'personcourse_'+course
        for table_user in PersonCourse.objects.using("personcourse").all():
            if table_user.start_time is not None:
                if last_date is None or table_user.start_time > last_date:
                    last_date = table_user.start_time

        if last_date is not None:

            month_ago = last_date + datetime.timedelta(-30)
            week_ago = last_date + datetime.timedelta(-7)
            day_ago = last_date + datetime.timedelta(-1)

            PersonCourse._meta.db_table = 'personcourse_'+course
            for table_user in PersonCourse.objects.using("personcourse").all():
                if table_user.start_time is not None:
                    if table_user.start_time > month_ago:
                        month_students += 1
                        if table_user.start_time > week_ago:
                            week_students += 1
                            if table_user.start_time > day_ago:
                                day_students += 1

    data['last_week'] = str(week_students)
    data['last_month'] = str(month_students)
    data['last_day'] = str(day_students)

    return api.views.api_render(request, data, status.HTTP_200_OK)

@api_view(['GET'])
def meta_lastingest(request):
    """
    Returns the last time the ingested data was run, and the latest date that the ingestion data was supplied
    """
    ingests = get_latest_ingest_dates()

    return api.views.api_render(request, ingests, status.HTTP_200_OK)

def get_latest_ingest_dates():
    last_ingested_item = None
    last_clicksteam_item_date = None
    for ingest in Ingestor.objects.using("default").all():
        #if ingest.completed_date:
        if ingest.completed == 1 and ingest.completed_date:
            if last_ingested_item is None or ingest.completed_date > last_ingested_item.completed_date:
                last_ingested_item = ingest
            if ingest.service_name == 'Clickstream':
                click_date = str(ingest.meta).split('/')
                click_date = click_date[-1].split('_')
                click_date = datetime.datetime.strptime(click_date[0], "%Y-%m-%d")
                if last_clicksteam_item_date is None or click_date > last_clicksteam_item_date:
                    last_clicksteam_item_date = click_date

    data = OrderedDict()
    data['ingest_date'] = datetime.datetime.strftime(last_ingested_item.completed_date, "%Y-%m-%d")
    data['data_date'] = datetime.datetime.strftime(last_clicksteam_item_date, "%Y-%m-%d")
    return data