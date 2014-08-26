import json
import urllib2
import api.views
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from api.models import UserProfile, UserEnrol, Log, StudentModule, PersonCourse
from collections import OrderedDict
import datetime
from rest_framework.permissions import AllowAny
import random
import dateutil

# Logging
import logging
logger = logging.getLogger(__name__)

@api_view(['GET'])
@permission_classes((AllowAny, ))
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
    gender = OrderedDict()
    gender['Male'] = 0
    gender['Female'] = 0
    gender['Other'] = 0
    gender['Unspecified'] = 0
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
@permission_classes((AllowAny, ))
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

    age = OrderedDict()
    age["Less than 12"] = 0
    age["12-15"] = 0
    age["16-18"] = 0
    age["19-22"] = 0
    age["23-25"] = 0
    age["26-30"] = 0
    age["31-40"] = 0
    age["31-40"] = 0
    age["41-50"] = 0
    age["Over 50"] = 0
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
@permission_classes((AllowAny, ))
def student_fullages(request, course_id='all'):
    """
    Lists all ages for the enrolled students
    """
    max_age = 100
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

    age = OrderedDict()
    for i in range(0, max_age):
        age[str(i)] = 0
    for course in courses:
        pass
        for user in UserProfile.objects.using(course).all():
            if user.year_of_birth == 'NULL':
                user.year_of_birth = "Unknown"
            else:
                theage = 0
                try:
                    theage = (2014 - int(user.year_of_birth))
                    if theage <= max_age:
                        theage = str(theage)
                        if theage not in age:
                            age[theage] = 0
                        age[theage] += 1
                except ValueError:
                    logger.error("Age is not a year")

    data = age
    return api.views.api_render(request, data, status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes((AllowAny, ))
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
    education = OrderedDict()
    education['Primary school'] = 0
    education['Middle school'] = 0
    education['Secondary school'] = 0
    education['Associate'] = 0
    education['Bachelor'] = 0
    education['Masters'] = 0
    education['Doctorate'] = 0
    education['Other'] = 0

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
@permission_classes((AllowAny, ))
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
@permission_classes((AllowAny, ))
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
    total = 0
    for course_id in courses:
        course = api.views.get_course(course_id)
        coursedata = Log.countcountryenrolments('clickstream', course['mongoname'])
        for countrydata in coursedata:
            if countrydata['country'] not in data:
                data[countrydata['country']] = {'count': 0, 'percentage': 0}
            data[countrydata['country']]['count'] += countrydata['count']
            total += countrydata['count']
    for country in data:
        data[country]['percentage'] = float(data[country]['count']) / float(total)*100
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

    data = OrderedDict(sorted(data.items()))

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


@api_view(['GET'])
def student_activity(request, course_id='all'):
    starttime = datetime.datetime.now()
    grouptypes = True
    if api.views.is_cached(request):
        return api.views.api_cacherender(request)
    course = api.views.get_course(course_id)
    if course is None:
        return api.views.api_render(request, {'error': 'Unknown course code'}, status.HTTP_404_NOT_FOUND)

    #Course Structure Read
    filename = course['dbname'].replace("_", "-")
    courseurl = 'https://tools.ceit.uq.edu.au/datasources/course_structure/'+filename+'.json'
    validelements = []
    structure = {}
    try:
        data = urllib2.urlopen(courseurl).read().replace('<script','').replace('</script>','')
    except:
        return api.views.api_render(request, {'error': 'Could not find course file'}, status.HTTP_404_NOT_FOUND)
    print "Loading structure"
    structure = json.loads(data)
    weeknumber = 1
    for week in structure['children']:
        seqnumber = 1
        for sequential in week['children']:
            uid = 'Week '+str(weeknumber)+"."+str(seqnumber)
            element = {
                'week': str(weeknumber),
                'tag': sequential['tag'],
                'url_name': sequential['url_name'],
                'uid': uid+" Sequence"+"_url_"+sequential['url_name']
            }
            validelements.append(element)
            for vertical in sequential['children']:
                probnumber = 1
                for problem in vertical['children']:
                    if problem['tag'] != 'html' and problem['tag'] != 'discussion' and problem['tag'] != 'lti':
                        element = {
                            'week': str(weeknumber),
                            'tag': problem['tag'],
                            'url_name': problem['url_name'],
                            'uid': uid+" "+problem['tag']+" "+str(probnumber)+"_url_"+problem['url_name']
                        }
                        if 'display_name' in problem:
                            element['display_name'] = problem['display_name']
                        validelements.append(element)
                        probnumber += 1
            seqnumber += 1
        weeknumber += 1
        #break
    start_date = dateutil.parser.parse(structure['start'])
    print "Loaded structure"
    weeks = []
    weeks.append(start_date)
    print "Working out weeks"
    last_date = start_date
    for i in range(0,10):
        last_date = last_date+datetime.timedelta(days=7)
        weeks.append(last_date)
    print "Worked out weeks"

    #clickstreamdata = Log.find_events('clickstream_hypers_301x_sample', course['mongoname'])
    #print clickstreamdata


    data = []
    print "Starting elements"
    elcount = 0
    for element in validelements:
        print "starting element "+str(elcount)+"/"+str(len(validelements))+ " time difference is "+str(datetime.datetime.now() - starttime)+" seconds"
        activity = OrderedDict()
        activity['Activity'] = {'url': element['url_name'], 'tag': element['tag'], 'uid': element['uid']}
        if 'week' in element:
            activity['Activity']['week'] = element['week']
        i = 1
        for week in weeks:
            nextweek = week+datetime.timedelta(days=7)
            activity['Week '+str(i)] = StudentModule.objects.using(course_id).filter(module_id__contains=element['url_name'], created__range=[week, nextweek]).values('student_id').distinct().count()
            i += 1
        data.append(activity)
        elcount += 1
    print "Finished elements"
    print "TIME DIFFERENCE "+str(datetime.datetime.now() - starttime)+" SECONDS"
    return api.views.api_render(request, data, status.HTTP_200_OK)


@api_view(['GET'])
def student_personcourse(request, course_id='all'):
    """
    Lists all genders for the enrolled students
    """
    #Disable cache for the time being
    #if api.views.is_cached(request):
    #    return api.views.api_cacherender(request)
    fields = None
    if 'fields' in request.GET:
        fields = request.GET['fields'].split(',')
    courses = []
    if course_id is 'all':
        courselist = api.views.get_all_courses()
        for course in courselist:
            if 'mongoname' in courselist[course]:
                courses.append(courselist[course]['mongoname'])
        pass
    else:
        course = api.views.get_course(course_id)
        if course is None:
            return api.views.api_render(request, {'error': 'Unknown course code'}, status.HTTP_404_NOT_FOUND)
        courses.append(course['mongoname'])
    data = []
    for course in courses:
        for table_user in PersonCourse.objects.using("personcourse").filter(course_id=course):
            data.append(table_user.to_dict(fields))
    return api.views.api_render(request, data, status.HTTP_200_OK)
