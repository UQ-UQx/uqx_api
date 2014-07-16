import api.views
from rest_framework import status
from rest_framework.decorators import api_view
from api.models import UserProfile, UserEnrol, Log
from collections import OrderedDict
from datetime import datetime

# Logging
import logging
logger = logging.getLogger(__name__)

@api_view(['GET'])
def student_genders(request, course_id='all'):
    """
    Lists all genders for the enrolled students
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
    gender_map = {'m': 'Male', 'f': 'Female', 'o': 'Other'}
    gender = {'Male': 0, 'Female': 0, 'Other': 0, 'Unspecified': 0}
    for course in courses:
        for user in UserProfile.objects.using(course).all():
            if user.gender in gender_map:
                user.gender = gender_map[str(user.gender)]
            else:
                user.gender = "Unspecified"
            if user.gender == 'm':
                user.gender = "Male"
            if user.gender == 'f':
                user.gender = "Female"
            if user.gender == 'o':
                user.gender = "Other"
            gender[str(user.gender)] += 1
    data = gender
    return api.views.api_render(request, data, status.HTTP_200_OK)


@api_view(['GET'])
def student_ages(request, course_id='all'):
    """
    Lists all ages for the enrolled students
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

    age = {}
    for course in courses:
        for user in UserProfile.objects.using(course).all():
            if user.year_of_birth == 'NULL':
                user.year_of_birth = "Unknown"
            else:
                theage = 0
                try:
                    theage = 2014 - int(user.year_of_birth)
                except ValueError:
                    logger.error("Age is not a year")
                if theage < 12:
                    user.year_of_birth = "Less than 12"
                elif theage < 16:
                    user.year_of_birth = "12-15"
                elif theage < 19:
                    user.year_of_birth = "16-18"
                elif theage < 23:
                    user.year_of_birth = "19-22"
                elif theage < 26:
                    user.year_of_birth = "23-25"
                elif theage < 31:
                    user.year_of_birth = "26-30"
                elif theage < 41:
                    user.year_of_birth = "31-40"
                elif theage < 51:
                    user.year_of_birth = "41-50"
                else:
                    user.year_of_birth = "Over 50"
            if user.year_of_birth not in age:
                age[user.year_of_birth] = 0
            age[user.year_of_birth] += 1

    data = age
    return api.views.api_render(request, data, status.HTTP_200_OK)


@api_view(['GET'])
def student_educations(request, course_id='all'):
    """
    Lists all prior education levels for the enrolled students
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
    education_map = {
        'p': 'Doctorate',
        'm': 'Masters',
        'b': 'Bachelor',
        'a': 'Associate',
        'hs': 'Secondary school',
        'jhs': 'Middle school',
        'el': 'Primary school',
        'other': 'Other',
        'p_se': 'Doctorate',
        'p_oth': 'Doctorate'
    }
    education = {}
    for course in courses:
        for user in UserProfile.objects.using(course).all():
            if user.level_of_education in education_map and user.level_of_education != '':
                user.level_of_education = education_map[user.level_of_education]
            else:
                user.level_of_education = "Unspecified"
            if user.level_of_education not in education:
                education[user.level_of_education] = 0
            education[user.level_of_education] += 1
    data = education
    return api.views.api_render(request, data, status.HTTP_200_OK)


@api_view(['GET'])
def student_modes(request, course_id='all'):
    """
    Lists all modes of enrolment for the enrolled students
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
    modes = {'audit':0,'honor':0,'verified':0}
    total = 0

    for course in courses:
        for user in UserEnrol.objects.using(course).all():
            if user.mode not in modes:
                modes[user.mode] = 0
            modes[user.mode] += 1
            total += 1

    modes['total'] = total
    data = modes
    return api.views.api_render(request, data, status.HTTP_200_OK)


@api_view(['GET'])
def student_countries(request, course_id='all'):
    """
    Lists
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
    data = OrderedDict()
    for course_id in courses:
        course = api.views.get_course(course_id)
        coursedata = Log.countcountryenrolments('clickstream', course['mongoname'])
        for countrydata in coursedata:
            if countrydata['country'] not in data:
                data[countrydata['country']] = {'count': 0, 'percentage': 0}
            data[countrydata['country']]['count'] += countrydata['count']
            data[countrydata['country']]['percentage'] += countrydata['percentage']
    return api.views.api_render(request, data, status.HTTP_200_OK)


@api_view(['GET'])
def student_dates(request, course_id='all'):
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
    data = OrderedDict()
    for course in courses:
        for user in UserEnrol.objects.using(course).all():
            thedate = user.created[:10]
            if thedate not in data:
                data[thedate] = {'enrolled': 0, 'active': 0, 'aggregate_enrolled': 0, 'aggregate_active': 0}
            data[thedate]['enrolled'] += 1
            if user.is_active == "1":
                data[thedate]['active'] += 1

        count = 0
        activecount = 0
        for date in data:
            count += data[date]['enrolled']
            activecount += data[date]['active']
            data[date]['aggregate_enrolled'] = count
            data[date]['aggregate_active'] = activecount

    return api.views.api_render(request, data, status.HTTP_200_OK)


@api_view(['GET'])
def student_active(request, course_id='all'):
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
    data = OrderedDict()
    datadays = {}
    dataweeks = {}
    data['days'] = OrderedDict()
    data['weeks'] = OrderedDict()
    for course_id in courses:
        course = api.views.get_course(course_id)
        activeusers = Log.activeusersdaily('clickstream', course['mongoname'])
        for day in activeusers:
            if day['_id'] not in data['days']:
                datadays[day['_id']] = 0
            datadays[day['_id']] += day['userCount']

        activeusersweekly = Log.activeusersweekly('clickstream', course['mongoname'])
        for week in activeusersweekly:
            theyear = week['_id'][0:4]
            theweek = week['_id'][5:].zfill(2)
            realdate = datetime.strptime(theyear+theweek+'1', '%Y%W%w')
            thedate = realdate.strftime("%Y-%m-%d")
            if thedate not in data['weeks']:
                dataweeks[thedate] = 0
            dataweeks[thedate] += week['userCount']

    for key in sorted(datadays.iterkeys()):
        data['days'][key] = datadays[key]

    for key in sorted(dataweeks.iterkeys()):
        data['weeks'][key] = dataweeks[key]



    return api.views.api_render(request, data, status.HTTP_200_OK)