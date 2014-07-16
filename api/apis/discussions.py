import api.views
import json
import urllib2
from rest_framework import status
from rest_framework.decorators import api_view
from api.models import DiscussionForum

# Logging
import logging
logger = logging.getLogger(__name__)

@api_view(['GET'])
def discussion_countries(request, course_id='all'):
    if api.views.is_cached(request):
        return api.views.api_cacherender(request)
    courses = {}
    if course_id == 'all':
        courses = api.views.get_all_courses()
    else:
        course = api.views.get_course(course_id)
        if course is None:
            return api.views.api_render(request, {'error': 'Unknown course code'}, status.HTTP_404_NOT_FOUND)
        courses[course_id] = course
    #print courses
    DiscussionForum.connect_to_mongo()
    data = {}
    data['country_dict'] = {}
    data['country_enrol'] = {}
    data['post_total'] = 0
    #data['user_total'] = 0
    for course in courses.values():
        df_map = DiscussionForum.post_user_country(course)
        for country, num in df_map['country_dict'].items():
            data['post_total'] += num
            if country in data['country_dict']:
                data['country_dict'][country] += num
            else:
                data['country_dict'][country] = num

        #remove duplicate of user?
        for item in df_map['country_enrol']:
            #data['user_total'] += item['userSum']
            if item['_id'] in data['country_enrol']:
                data['country_enrol'][item['_id']] += item['userSum']
            else:
                data['country_enrol'][item['_id']] = item['userSum']

    data['country_post'] = []
    data['post_max'] = 0
    for country, num in data['country_dict'].items():
        post_percentage = round(num * 100 / float(data['post_total']), 2)
        data['country_post'].append([country, num, post_percentage])
        if post_percentage > data['post_max']:
            data['post_max'] = post_percentage

    data['country_post_enrol'] = []
    data['post_enrol_max'] = 0
    for country, userSum in data['country_enrol'].items():
        if country in data['country_dict']:
            pe_percentage = round(data['country_dict'][country] * 100 / float(userSum), 2)
            post_enrol = [country, data['country_dict'][country], userSum, pe_percentage]
            if pe_percentage > data['post_enrol_max']:
                data['post_enrol_max'] = pe_percentage
        else:
            post_enrol = [country, 0, userSum, 0]
        data['country_post_enrol'].append(post_enrol)

    return api.views.api_render(request, data, status.HTTP_200_OK)


@api_view(['GET'])
def discussion_dates(request, course_id='all'):
    if api.views.is_cached(request):
        return api.views.api_cacherender(request)
    courses = {}
    if course_id == 'all':
        courses = api.views.get_all_courses()
    else:
        course = api.views.get_course(course_id)
        if course is None:
            return api.views.api_render(request, {'error': 'Unknown course code'}, status.HTTP_404_NOT_FOUND)
        courses[course_id] = course
    DiscussionForum.connect_to_mongo()
    data = {}
    # Data for the chart based on daily posts
    data['comments'] = {}
    data['threads'] = {}
    for course in courses.values():
        group_by_date = DiscussionForum.group_by_date(course)
        for date, postNum in group_by_date['comment'].items():
            str_date = str(date)
            if str_date in data['comments']:
                data['comments'][str_date] += postNum
            else:
                data['comments'][str_date] = postNum
        for date, postNum in group_by_date['comment_thread'].items():
            str_date = str(date)
            if str_date in data['threads']:
                data['threads'][str_date] += postNum
            else:
                data['threads'][str_date] = postNum

    data['comment_datecounts'] = sorted(data['comments'].iteritems())
    data['thread_datecounts'] = sorted(data['threads'].iteritems())

    comment_datecountsaggregate = {}
    count = 0
    for key, value in data['comment_datecounts']:
        count += value
        comment_datecountsaggregate[key] = count
    data['comment_datecountsaggregate'] = sorted(comment_datecountsaggregate.iteritems())

    thread_datecountsaggregate = {}
    count = 0
    for key, value in data['thread_datecounts']:
        count += value
        thread_datecountsaggregate[key] = count
    data['thread_datecountsaggregate'] = sorted(thread_datecountsaggregate.iteritems())
    return api.views.api_render(request, data, status.HTTP_200_OK)


@api_view(['GET'])
def discussion_popular(request, course_id='all'):
    if api.views.is_cached(request):
        return api.views.api_cacherender(request)
    courses = {}
    if course_id == 'all':
        courses = api.views.get_all_courses()
    else:
        course = api.views.get_course(course_id)
        if course is None:
            return api.views.api_render(request, {'error': 'Unknown course code'}, status.HTTP_404_NOT_FOUND)
        courses[course_id] = course

    DiscussionForum.connect_to_mongo()
    popular_num = 10
    data = {}
    for course_id, course in courses.items():
        data[course_id] = DiscussionForum.sort_by_answer(course, popular_num)

    return api.views.api_render(request, data, status.HTTP_200_OK)


@api_view(['GET'])
def discussion_top(request, course_id='all'):
    if api.views.is_cached(request):
        return api.views.api_cacherender(request)
    courses = {}
    if course_id == 'all':
        courses = api.views.get_all_courses()
    else:
        course = api.views.get_course(course_id)
        if course is None:
            return api.views.api_render(request, {'error': 'Unknown course code'}, status.HTTP_404_NOT_FOUND)
        courses[course_id] = course

    DiscussionForum.connect_to_mongo()
    up_num = 10
    data = {}
    for course_id, course in courses.items():
        data[course_id] = DiscussionForum.sort_by_votes(course, up_num)

    return api.views.api_render(request, data, status.HTTP_200_OK)


@api_view(['GET'])
def discussion_category(request, course_id):
    if api.views.is_cached(request):
        return api.views.api_cacherender(request)
    course = api.views.get_course(course_id)
    if course is None:
        return api.views.api_render(request, {'error': 'Unknown course code'}, status.HTTP_404_NOT_FOUND)

    json_file = course['dbname'].replace("_", "-") + '.json'
    courseinfo = loadcourseinfo(json_file)

    if courseinfo is None:
        return api.views.api_render(request, {'error': 'Can not find course info'}, status.HTTP_404_NOT_FOUND)

    data = {}

    discussions = []
    data['categories'] = get_discussions(courseinfo, discussions)

    DiscussionForum.connect_to_mongo()
    db_df = DiscussionForum.mongo_client['discussion_forum']
    col_df = db_df[course['discussiontable']]
    data['min_date'] = DiscussionForum.min_date(col_df)
    data['max_date'] = DiscussionForum.max_date(col_df)
    data['popular_number'] = 20

    for category in data['categories']:
        category_id = category['discussion_id']
        data[category_id] = {}
        category_group_by_date = DiscussionForum.category_group_by_date(col_df, category_id)
        data[category_id]['thread_datecount'] = sorted(category_group_by_date['thread'].iteritems())
        data[category_id]['comment_datecounts'] = sorted(category_group_by_date['comment'].iteritems())
        data[category_id]['ccomment_datecounts'] = sorted(category_group_by_date['ccomment'].iteritems())

        category_sort_by_answer = DiscussionForum.category_sort_by_answer(col_df, category_id, data['popular_number'])
        data[category_id]['popular_threads'] = category_sort_by_answer['popular_threads']
        data[category_id]['zones'] = category_sort_by_answer['zones']

    return api.views.api_render(request, data, status.HTTP_200_OK)


def loadcourseinfo(json_file):
    courseurl = 'https://tools.ceit.uq.edu.au/datasources/course_structure/'+json_file
    courseinfofile = urllib2.urlopen(courseurl)
    if courseinfofile:
        courseinfo = json.load(courseinfofile)
        return courseinfo
    return None


def get_discussions(obj, found=[]):
    if obj['tag'] == 'discussion' and 'discussion_category' in obj:
        found.append(obj)
    for child in obj['children']:
        found = get_discussions(child, found)
    return found



















