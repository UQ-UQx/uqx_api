import api.views
from rest_framework import status
from rest_framework.decorators import api_view
import uqx_api.courses
from collections import OrderedDict
from api.models import UserProfile, UserEnrol, Log, StudentModule, PersonCourse, UserDetail
from django.db.models import Q

from datetime import datetime, timedelta
import httplib2
import os
import sys

from apiclient.discovery import build
from oauth2client.file import Storage
from oauth2client.client import OAuth2WebServerFlow
from oauth2client.tools import run
from uqx_api import settings
from optparse import OptionParser

# Logging
import logging
logger = logging.getLogger(__name__)

@api_view(['GET'])
def person_profile(request, user_id):
    """
    Lists the demographic for a specific student
    """
    data = {'status': 'error', 'message': 'No information for ID '+str(user_id)}

    courses = []
    profiles = {}
    personcourse = {}
    for db in uqx_api.courses.EDX_DATABASES:
        if db == 'default' or db == 'personcourse':
            continue
        print db
        try:
            users = UserProfile.objects.using(db).filter(user_id=user_id)
            if len(users) > 0:
                courses.append(db)
                profile = {}
                profile['name'] = users[0].name
                profile['language'] = users[0].language
                profile['location'] = users[0].location
                profile['mailing_address'] = users[0].mailing_address
                profile['gender'] = users[0].gender
                profile['meta'] = users[0].meta
                profile['goals'] = users[0].goals
                profile['city'] = users[0].city
                profile['country'] = users[0].country
                profile['year_of_birth'] = users[0].year_of_birth
                profile['level_of_education'] = users[0].level_of_education



                profiles = profile
            else:
                print "NO users for "+db
        except Exception as e:
            print "ECCC"+str(e)
            pass

    for course_id in courses:
        PersonCourse._meta.db_table = 'personcourse_'+course_id
        pc_exists = api.views.db_table_exists('personcourse',PersonCourse._meta.db_table)
        if pc_exists:
            person = PersonCourse.objects.using("personcourse").filter(user_id=user_id)
            print "----"
            print person
            print "===="
            person_object = {}
            person_object['registered'] = person[0].registered
            person_object['viewed'] = person[0].viewed
            person_object['explored'] = person[0].explored
            person_object['certified'] = person[0].certified
            person_object['final_cc_cname'] = person[0].final_cc_cname
            person_object['LoE'] = person[0].LoE
            person_object['YoB'] = person[0].YoB
            person_object['gender'] = person[0].gender
            person_object['mode'] = person[0].mode
            person_object['grade'] = person[0].grade
            person_object['start_time'] = person[0].start_time
            person_object['last_event'] = person[0].last_event
            person_object['nevents'] = person[0].nevents
            person_object['ndays_act'] = person[0].ndays_act
            person_object['nplay_video'] = person[0].nplay_video
            person_object['nchapters'] = person[0].nchapters
            person_object['nforum_posts'] = person[0].nforum_posts
            person_object['roles'] = person[0].roles
            person_object['attempted_problems'] = person[0].attempted_problems
            personcourse[course_id] = person_object

    if len(courses) > 0:
        data = {}
        data['profile'] = profile
        data['courses'] = courses
        data['person_course'] = personcourse


    return api.views.api_render(request, data, status.HTTP_200_OK)


@api_view(['GET'])
def person_lookup(request, details):
    """
    Lists the demographic for a specific student
    """
    data = {'status': 'error', 'message': 'No information for '+str(details)}

    profiles = {}
    for db in uqx_api.courses.EDX_DATABASES:
        if db == 'default' or db == 'personcourse':
            continue
        print db
        try:

            userdetails = UserDetail.objects.using(db).filter(Q(username=details) | Q(email=details))
            print "$$$"
            extrausers = []
            for userdetail in userdetails:
                extrausers.append(str(userdetail.id))

            users = UserProfile.objects.using(db).filter(Q(name__contains=details) | Q(user_id__in=extrausers))
            for user in users:
                if user.user_id not in profiles:
                    profile = {}
                    profile['user_id'] = user.user_id
                    profile['name'] = user.name
                    profile['location'] = user.location
                    profile['country'] = user.country
                    profile['year_of_birth'] = user.year_of_birth
                    profile['level_of_education'] = user.level_of_education
                    profile['courses'] = [db]
                    profiles[user.user_id] = profile
                else:
                    if db not in profiles[user.user_id]['courses']:
                        profiles[user.user_id]['courses'].append(db)
            else:
                print "NO users for "+db
        except Exception as e:
            print "ECCC"+str(e)
            pass

    if len(profiles) > 0:
        data = profiles


    return api.views.api_render(request, data, status.HTTP_200_OK)