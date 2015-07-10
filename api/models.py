from django.db import models
from mongoengine import *
from bson import Code
from mongoengine.connection import _get_db

import MySQLdb
import config

import pymongo

from django.db import connections
from datetime import date, datetime, timedelta


# Logging
import logging
logger = logging.getLogger(__name__)

connect('logs')

class Log(Document):
    status = StringField(required=True)
    request_header_referer = StringField(required=True)
    remote_user = StringField()
    request_header_user_agent__is_mobile = BooleanField()
    request_header_user_agent__browser__version_string = StringField()
    time_recieved_isoformat = StringField()
    request_header_user_agent = StringField()
    request_http_ver = StringField()
    request_header_user_agent__os__version_string = StringField()
    remote_logname = StringField()
    request_first_line = StringField()
    request_header_user_agent__browser__family = StringField()
    time_recieved = StringField()
    response_bytes_clf = StringField()
    request_header_user_agent__os__family = StringField()
    request_method = StringField()
    request_url = StringField()
    remote_host = StringField()
    time_recieved_datetimeobj = DateTimeField()
    country = StringField()


    @staticmethod
    def countfield(field, withpercentages=False, collectionname="log"):
        total = 0
        reducer = Code("""
             function(cur, result) { result.count += 1 }
        """)
        results = _get_db()[collectionname].group(key={field: 1}, condition={},
                                      initial={"count": 0}, reduce=reducer)
        if withpercentages:
            for result in results:
                total += result['count']

        for result in results:
            result['name'] = result[field]
            if withpercentages:
                result['percentage'] = float(float(result['count'])/float(total))*100
            del result[field]
        return results


    @staticmethod
    def countcountryenrolments(collectionname, course_id):
        #DO db.clickstream.ensureIndex({country:1})
        #DO db.clickstream.ensureIndex( {event_type: 1,"context.course_id": 1} )
        #DO db.clickstream.ensureIndex({"context.course_id": 1})
        #db.clickstream_tmp.aggregate(    [      { $match : {'context.course_id':'UQx/Think101x/1T2014','event_type':'edx.course.enrollment.activated'} },      { $group : { _id : "$country", thecount: { $sum: 1 } } }    ] )
        results = _get_db()[collectionname].aggregate([ {"$match":{'context.course_id':course_id,
                                                                   'event_type':'edx.course.enrollment.activated'}},{"$group":{"_id": "$country", "thecount": { "$sum": 1 } }} ])
        results = results['result']
        countries = []
        total = 0
        for result in results:
            total += result['thecount']
        for result in results:
            country = {'country': result['_id'], 'count': result['thecount'], 'percentage': (float(result['thecount'])*100/float(total))}
            countries.append(country)
        return countries

    @staticmethod
    def find_events(collection_name, course_id):
        results = _get_db()[collection_name].aggregate([ {"$match":{'context.course_id':course_id}},{"$group": {"_id": "$username", "events":{"$addToSet":"$event_type"}}}])
        return results

    @staticmethod
    def activeusersdaily(collectionname, course_id):
        results = _get_db()[collectionname].aggregate([ {"$match":{'context.course_id':course_id}},{"$group":{"_id": {"$substr":["$time",0,10]}, "users":{"$addToSet":"$username"} }}, {"$unwind":"$users"}, {"$group":{"_id":"$_id","userCount":{"$sum":1}}} ])
        results = results['result']
        for user in results:
            user['date'] = user['_id']
        return results

    @staticmethod
    def activeusersweekly(collectionname, course_id):
        results = _get_db()[collectionname].aggregate([ {"$match":{'context.course_id':course_id, "time_date": {"$exists": True}}},{"$group":{"_id": {"$concat":[  {"$substr":[{"$year":['$time_date']},0,4]} ,"_",{"$substr":[{"$week":['$time_date']},0,2]}]}, "users":{"$addToSet":"$username"} }}, {"$unwind":"$users"}, {"$group":{"_id":"$_id","userCount":{"$sum":1}}} ])
        results = results['result']
        return results

    @staticmethod
    def eventtypes(collectionname, course_id):
        results = _get_db()[collectionname].aggregate([ {"$match":{'context.course_id':course_id}},{"$group":{"_id":{"type":"$event_type","date":{"$concat":[  {"$substr":[{"$year":['$time_date']},0,4]} ,"_",{"$substr":[{"$week":['$time_date']},0,2]}]}},"users":{"$addToSet":"$username"} }}, {"$unwind":"$users"}, {"$group":{"_id":"$_id","userCount":{"$sum":1}}}])
        results = results['result']
        return results


class UserDetail(models.Model):
    id = models.IntegerField(primary_key=True)
    username = models.CharField(max_length=255)
    email = models.CharField(max_length=255)

    class Meta:
        db_table = 'auth_user'


class UserProfile(models.Model):
    user_id = models.CharField(max_length=255)

    name = models.CharField(max_length=255)
    language = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    meta = models.CharField(max_length=255)
    mailing_address = models.CharField(max_length=255)
    goals = models.CharField(max_length=255)
    country = models.CharField(max_length=255)
    city = models.CharField(max_length=255)

    gender = models.CharField(max_length=255)
    year_of_birth = models.CharField(max_length=255)
    level_of_education = models.CharField(max_length=255)


    class Meta:
        db_table = 'auth_userprofile'


class CourseProfile(models.Model):


    course = models.CharField(max_length=255)
    dbname = models.CharField(max_length=255)
    mongoname = models.CharField(max_length=255)
    discussiontable = models.CharField(max_length=255)
    registration_open_date = models.DateField()
    course_launch_date = models.DateField()
    course_close_date = models.DateField()
    nregistered_students = models.IntegerField()
    nviewed_students = models.IntegerField()
    nexplored_students = models.IntegerField()
    ncertified_students = models.IntegerField()
    nhonor_students = models.IntegerField()
    naudit_students = models.IntegerField()
    nvertified_students = models.IntegerField()
    course_effort = models.FloatField()
    course_length = models.IntegerField()
    nchapters = models.IntegerField()
    nvideos = models.IntegerField()
    nhtmls = models.IntegerField()
    nassessments = models.IntegerField()
    nsummative_assessments = models.IntegerField()
    nformative_assessments = models.IntegerField()
    nincontent_discussions = models.IntegerField()
    nactivities = models.IntegerField()
    best_assessment = models.CharField(max_length=255)
    worst_assessment = models.CharField(max_length=255)

    class Meta:
        db_table = 'courseprofile'

    def to_dict(self, fields):
        if fields is None:
            pass
        return {
            'course': self.course,
            'dbname': self.dbname,
            'mongoname': self.mongoname,
            'discussiontable': self.discussiontable,
            'registration_open_date': self.registration_open_date,
            'course_launch_date': self.course_launch_date,
            'course_close_date': self.course_close_date,
            'nregistered_students': self.nregistered_students,
            'nviewed_students': self.nviewed_students,
            'nexplored_students': self.nexplored_students,
            'ncertified_students': self.ncertified_students,
            'nhonor_students': self.nhonor_students,
            'naudit_students': self.naudit_students,
            'nvertified_students': self.nvertified_students,
            'course_effort': self.course_effort,
            'course_length': self.course_length,
            'nchapters': self.nchapters,
            'nvideos': self.nvideos,
            'nhtmls': self.nhtmls,
            'nassessments': self.nassessments,
            'nsummative_assessments': self.nsummative_assessments,
            'nformative_assessments': self.nformative_assessments,
            'nincontent_discussions': self.nincontent_discussions,
            'nactivities': self.nactivities,
            'best_assessment': self.best_assessment,
            'worst_assessment': self.worst_assessment,
        }


class PersonCourse(models.Model):
    course_id = models.CharField(max_length=255)
    user_id = models.CharField(max_length=255)
    registered = models.IntegerField()
    viewed = models.IntegerField()
    explored = models.IntegerField()
    certified = models.IntegerField()
    final_cc_cname = models.CharField(max_length=255)
    LoE = models.CharField(max_length=255)
    YoB = models.DateField()
    gender = models.CharField(max_length=255)
    mode = models.CharField(max_length=255)
    grade = models.FloatField()
    start_time = models.DateField()
    last_event = models.DateField()
    nevents = models.IntegerField()
    ndays_act = models.IntegerField()
    nplay_video = models.IntegerField()
    nchapters = models.IntegerField()
    nforum_posts = models.IntegerField()
    roles = models.CharField(max_length=255)
    attempted_problems = models.IntegerField()
    inconsistent_flag = models.IntegerField()

    def to_dict(self, fields):
        if fields is None:
            return {
                'course_id': self.course_id,
                'user_id': self.user_id,
                'registered': self.registered,
                'viewed': self.viewed,
                'explored': self.explored,
                'certified': self.certified,
                'final_cc_cname': self.final_cc_cname,
                'LoE': self.LoE,
                'YoB': self.YoB,
                'gender': self.gender,
                'mode': self.mode,
                'grade': self.grade,
                'start_time': self.start_time,
                'last_event': self.last_event,
                'nevents': self.nevents,
                'ndays_act': self.ndays_act,
                'nplay_video': self.nplay_video,
                'nchapters': self.nchapters,
                'nforum_posts': self.nforum_posts,
                'roles': self.roles,
                'attempted_problems': self.attempted_problems,
                'inconsistent_flag': self.inconsistent_flag,
            }
        else:
            sub_dict = {}
            for field in fields:
                if hasattr(self, field):
                    sub_dict[field] = getattr(self, field)
            return sub_dict

    class Meta:
        db_table = 'personcourse'


class UserEnrol(models.Model):
    user_id = models.CharField(max_length=255)
    course_id = models.CharField(max_length=255)
    created = models.DateTimeField()
    is_active = models.CharField(max_length=255)
    mode = models.CharField(max_length=255)

    class Meta:
        db_table = 'student_courseenrollment'


class UserCertificate(models.Model):
    user_id = models.CharField(max_length=255)
    download_url = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    grade = models.CharField(max_length=255)
    course_id = models.CharField(max_length=255)
    distinction = models.CharField(max_length=255)
    status = models.CharField(max_length=255)

    created_date = models.DateTimeField()
    modified_date = models.DateTimeField()
    mode = models.CharField(max_length=255)


    class Meta:
        db_table = 'certificates_generatedcertificate'


class StudentModule(models.Model):
    module_type = models.CharField(max_length=255)
    module_id = models.CharField(max_length=255)
    student_id = models.CharField(max_length=255)
    created = models.CharField(max_length=255)

    class Meta:
        db_table = 'courseware_studentmodule'


class Ingestor(models.Model):
    service_name = models.CharField(max_length=255)
    type = models.CharField(max_length=255)
    meta = models.CharField(max_length=255)
    started = models.IntegerField()
    completed = models.IntegerField()
    started_date = models.DateField()
    completed_date = models.DateField()

    class Meta:
        db_table = 'ingestor'


class CourseEvent(object):
    def __init__(self, db_name, table_name, course_start):
        self.db_name = db_name
        self.table_name = table_name
        self.course_start = course_start
        print course_start
        cursor = connections[db_name].cursor()

        self.events = []
        cursor.execute('desc %s' % table_name)
        for col in cursor.fetchall():
            if col[0] not in ['id', 'course_id', 'event_date']:
                self.events.append(col[0])
        #print self.events

        self.event_start = None
        self.event_end = None
        cursor.execute('SELECT MIN(%s) FROM %s' % ('event_date', table_name))
        self.event_start = cursor.fetchone()[0]
        if self.course_start is None:
            self.course_start = self.event_start
        cursor.execute('SELECT MAX(%s) FROM %s' % ('event_date', table_name))
        self.event_end = cursor.fetchone()[0]
        print self.event_start
        #print type(self.event_start)
        print self.event_end

        cursor.close()

    def counts_group_by_week(self):
        #str_events = ', ' . join('SUM(%s)' % e for e in self.events)
        #query = 'SELECT ' + str_events + ' From ' + self.table_name
        #result = cursor.execute(query).fetchone()

        eventcount = {}
        sum_events = []
        for event in self.events:
            sum_field = 's_' + event[2::].replace("$", ".")
            sum_events.append(sum_field)
            eventcount[sum_field] = {}

        str_events = ', ' . join('SUM(%s)' % e for e in self.events)

        cursor = connections[self.db_name].cursor()
        query = 'SELECT ' + str_events + ' From ' + self.table_name + ' WHERE event_date BETWEEN "%s" AND "%s"'

        d1 = self.course_start
        d2 = self.course_start + timedelta(days=6)
        while d2 < self.event_end:
            #sum_query = query % (d1, d2)
            #print d1
            #print d2
            #print sum_query
            cursor.execute(query % (d1, d2))
            row = cursor.fetchone()
            for index, sum_field in enumerate(sum_events):
                eventcount[sum_field][str(d1)] = row[index]
            d1 = d2 + timedelta(days=1)
            d2 = d1 + timedelta(days=6)

        return eventcount


class DiscussionForum(object):
    mongo_client = None

    @staticmethod
    def connect_to_mongo():
        try:
            DiscussionForum.mongo_client = pymongo.MongoClient('localhost', 27017)
        except pymongo.errors.ConnectionFailure, e:
            logger.error("Could not connect to MongoDB: %s" % e)


    @staticmethod
    def min_date(col_df):
        try:
            min_date_post = col_df.find().sort("created_at", 1).limit(1)[0]
            return min_date_post['created_at'].date()
        except IndexError:
            return None

    @staticmethod
    def max_date(col_df):
        try:
            max_date_post = col_df.find().sort("created_at", -1).limit(1)[0]
            return max_date_post['created_at'].date()
        except IndexError:
            return None

    @staticmethod
    def category_group_by_date(col_def, category_id):
        ccomment_datecounts = {}
        comment_datecounts = {}
        thread_datecounts = {}
        threads = []

        for thread in col_def.find({"commentable_id": category_id}):
            thread_date = thread['created_at'].date()
            threads.append(thread['_id'])
            if thread_date not in thread_datecounts:
                thread_datecounts[thread_date] = 0
            thread_datecounts[thread_date] += 1

        for post in col_def.find({"comment_thread_id": {"$in": threads}}):
            post_date = post['created_at'].date()
            if "parent_id" in post:
                # comment for comment
                if post_date not in ccomment_datecounts:
                    ccomment_datecounts[post_date] = 0
                ccomment_datecounts[post_date] += 1
            else:
                # comment
                if post_date not in comment_datecounts:
                    comment_datecounts[post_date] = 0
                comment_datecounts[post_date] += 1

        return {"thread": thread_datecounts, "comment": comment_datecounts, "ccomment": ccomment_datecounts}


    @staticmethod
    def thread_of_category(col_def, category_id):
        threads = {}
        for thread in col_def.find({"commentable_id": category_id}):
            threads[thread['_id']] = thread['body'].replace("\n", "  ").replace("\r", "")+" "
        return threads

    @staticmethod
    def category_sort_by_answer(col_def, category_id, popular_number):
        popular_threads = []

        zone_dict = {
            'equal 0': 0,
            '1 - 3': 0,
            '4 - 10': 0,
            '11 - 30': 0,
            '31 - 100': 0,
            'more than 100': 0,
        }

        threads = DiscussionForum.thread_of_category(col_def, category_id)

        popular_thread_ids = col_def.aggregate([
            {"$match": {"_type": "Comment", "comment_thread_id": {"$in": threads.keys()}}},
            {"$group": {"_id": "$comment_thread_id", "totalComm": {"$sum": 1}}},
            {"$sort": {"totalComm": -1}},
        ])['result']

        zone_dict['equal 0'] = len(threads) - len(popular_thread_ids)

        i = 0
        for item in popular_thread_ids:
            total = item['totalComm']

            if i < popular_number:
                i += 1
                ccomm_num = col_def.find({"_type": "Comment", "comment_thread_id": item['_id'], "parent_id": {"$exists": True}}).count()
                comm_num = total - ccomm_num
                popular_threads.append({"id": "No " + str(i), "thread_id": str(item['_id']), "body": threads[item['_id']], "comm_num": comm_num, "ccomm_num": ccomm_num})

            if total <= 3:
                zone_dict['1 - 3'] += 1
            elif total <= 10:
                zone_dict['4 - 10'] += 1
            elif total <= 30:
                zone_dict['11 - 30'] += 1
            elif total <= 100:
                zone_dict['31 - 100'] += 1
            else:
                zone_dict['more than 100'] += 1

        zone_list = []
        zone_list.append({'label': '0 comment', 'number': zone_dict['equal 0']})
        zone_list.append({'label': '1 - 3 comments', 'number': zone_dict['1 - 3']})
        zone_list.append({'label': '4 - 10 comments', 'number': zone_dict['4 - 10']})
        zone_list.append({'label': 'more than 10 comments', 'number': zone_dict['11 - 30'] + zone_dict['31 - 100'] + zone_dict['more than 100']})

        return {'popular_threads': popular_threads, 'zones': zone_list}


    @staticmethod
    def sort_by_votes(course, top_number, up_down='up'):
        # Decide the sorting field
        if up_down == "up":
            sort_field = "votes.up_count"
        elif up_down == "down":
            sort_field = "votes:down_count"
        else:
            sort_field = "_id"

        db_df = DiscussionForum.mongo_client['discussion_forum']
        col_df = db_df[course['discussiontable']]

        top_thread = []
        for post in col_df.find({"_type": "CommentThread"}).sort(sort_field, -1).limit(top_number):
            post['id'] = str(post.pop('_id'))
            top_thread.append(post)


        top_comment = []
        for post in col_df.find({"_type": "Comment"}).sort(sort_field, -1).limit(top_number):
            post['id'] = str(post.pop('_id'))
            thread = col_df.find({"_id": post['comment_thread_id']})
            post['comment_thread_body'] = thread[0]['body']
            post['comment_thread_id'] = str(post.pop('comment_thread_id'))
            if post['parent_ids']:
                parent = col_df.find({"_id": post['parent_id']})
                post['parent_body'] = parent[0]['body']
                post['parent_id'] = str(post.pop('parent_id'))
                post['parent_ids'] = [post['parent_id']]
            top_comment.append(post)

        return {"threads": top_thread, "comments": top_comment}


    @staticmethod
    def sort_by_answer(course, answer_num):
        db_df = DiscussionForum.mongo_client['discussion_forum']
        col_df = db_df[course['discussiontable']]

        popular_threads = []

        threads = col_df.aggregate([
            {"$match": {"_type": "Comment"}},
            {"$group": {"_id": "$comment_thread_id", "totalComm": {"$sum": 1}}},
            {"$sort": {"totalComm": -1}},
            {"$limit": answer_num}
        ])['result']

        for item in threads:
            thread = col_df.find({"_id": item['_id']})[0]
            thread['totalComm'] = item['totalComm']
            thread['id'] = str(thread.pop('_id'))
            popular_threads.append(thread)

        return popular_threads

    @staticmethod
    def group_by_date(course):
        db_df = DiscussionForum.mongo_client['discussion_forum']
        col_df = db_df[course['discussiontable']]

        min_date = DiscussionForum.min_date(col_df)
        max_date = DiscussionForum.max_date(col_df)

        comment_datecounts = {}
        comment_thread_datecounts = {}

        for post in col_df.find():
            post_date = post['created_at'].date()
            if post['_type'] == "Comment":
                if post_date not in comment_datecounts:
                    comment_datecounts[post_date] = 0
                comment_datecounts[post_date] += 1
            if post['_type'] == "CommentThread":
                if post_date not in comment_thread_datecounts:
                    comment_thread_datecounts[post_date] = 0
                comment_thread_datecounts[post_date] += 1
                
        return {"comment": comment_datecounts, "comment_thread": comment_thread_datecounts, 'min_date': min_date, 'max_date': max_date}

    @staticmethod
    #changed
    def posts_gb_users(course):
        db_df = DiscussionForum.mongo_client['discussion_forum']
        col_df_name = course['discussiontable']
        col_df = db_df[col_df_name]

        posts_gb_uid = col_df.aggregate([
            {"$group": {"_id": "$author_id", "postSum": {"$sum": 1}}},
        ])['result']

        user_post_dict = {}
        for item in posts_gb_uid:
            user_post_dict[int(item['_id'])] = item['postSum']
        return user_post_dict

    @staticmethod
    #changed
    def users_gb_countries(course):
        db_logs = DiscussionForum.mongo_client['logs']
        col_logs = db_logs['clickstream']

        users_gb_countries = col_logs.aggregate([
            {"$match": {"context.course_id": course['mongoname'], 'event_type':'edx.course.enrollment.activated'}},
            {"$group": {"_id": "$country", "userSum": {"$sum": 1}}}
        ])['result']

        return users_gb_countries

    @staticmethod
    #changed
    def user_2_country(course, uid_list):
        db_logs = DiscussionForum.mongo_client['logs']
        col_logs = db_logs['clickstream']

        user_2_country = col_logs.aggregate([
            {"$match": {"context.course_id": course['mongoname'], "context.user_id": {"$in": uid_list}, "country": {"$ne": None}}},
            {"$group": {"_id": "$context.user_id", "countrySet": {"$addToSet": "$country"}}},
        ])['result']
        return user_2_country

    @staticmethod
    #changed
    def post_user_country(course):
        user_post_dict = DiscussionForum.posts_gb_users(course)
        if user_post_dict:
            user_2_country = DiscussionForum.user_2_country(course, user_post_dict.keys())

            country_dict = {}
            for item in user_2_country:
                # ignore users of more than one countries
                if len(item['countrySet']) == 1:
                    country = item['countrySet'][0]
                    if country in country_dict:
                        country_dict[country] += user_post_dict[item['_id']]
                    else:
                        country_dict[country] = user_post_dict[item['_id']]
        else:
            country_dict = {}

        country_enrol = DiscussionForum.users_gb_countries(course)

        #return {"country_post": country_list, "post_max": post_max, "country_post_enrol": country_post_enrol_list, "post_enrol_max": post_enrol_max}
        return {"country_dict": country_dict, "country_enrol": country_enrol}





























