
from flask import redirect, request, url_for, session
from passlib.hash import pbkdf2_sha256
from functools import wraps
from flask_dance.contrib.facebook import facebook
from common.database import Database
from datetime import datetime
import time
import json


def is_pw_correct(password, hashed_password):
    """Test whether `password` that is not hashed is the same as `hashed_password`"""
    return pbkdf2_sha256.verify(password, hashed_password)


def hash_pw(password):
    """Returns hashed version of `password`"""
    return pbkdf2_sha256.hash(password)



def redirect_previous_url(default='home'):
    return redirect(request.args.get('next') or request.referrer or url_for(default))


def _get_user_info():
    """Gets user's info from facebook, then query db to extract various fields."""
    # get facebook account info
    
    json = facebook.get("/me").json()
    user_id = json['id']
    name = json['name']
    fb_info = user_id + "|" + name

    # some logging
    date_now = time.strftime("%Y-%m-%d")
    time_now = time.strftime("%Y-%m-%d_%H%M%S")
    print(f"[*] {time_now} -", fb_info, "logged", file=open(f"logs/{date_now}.log", "a"))
    print(f"[*] {time_now} -", fb_info, "logged")
    user = Database.get_user_by_fb_info(fb_info)
    return user
    

def _save_user_info(user):
    """Saves user fields into the session"""
    session['id'] = user['id']
    session['name'] = user['name']
    session['fb_info'] = user['fb_info']
    session['university'] = (user['university'], Database.get_university_name(user['university']))
    session['faculty'] = (user['faculty'], Database.get_faculty_name(user['faculty']))
    session['department'] = (user['department'], Database.get_department_name(user['department']))
    session['speciality'] = (user['speciality'], Database.get_speciality_name(user['speciality']))
    session['year'] = (user['year'], Database.get_year_name(user['year']))
    session['group'] = (user['groupe'], Database.get_group_name(user['groupe']))
    session['type'] = user['type']
    session['score'] = user['score']


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kws):
        user = _get_user_info()
        if not user:
            # not registered in database, redirect to register
            return redirect_previous_url(default="user.register")
        _save_user_info(user)
        return f(*args, **kws)            
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kws):
        # name = session.get("name")
        # type = session.get("type")
        # if name is None:
        #     # if not logged in, get back from where you came!
        #     # if the first time, go register
        #     return redirect_previous_url(default='user.register')
        # else:
        #     type = type.strip()
        #     if type != "admin":
        #         return redirect_previous_url(default='index')
        return f(*args, **kws)
    return decorated_function

def not_logged_in_required(f):
    @wraps(f)
    def decorated_function(*args, **kws):
        name = session.get("name")
        if name is not None:
            # if already logged in, go to index
            return redirect(url_for("index"))
        return f(*args, **kws)
    return decorated_function
        


def get_items_from_ajax(get_function):
    id = request.form.get('id')
    print("called", get_function.__name__, "with id of", id)
    items = get_function(id)
    return json.dumps(items)


def pretty_date(datetime_format):
    """
    Get a datetime object or a int() Epoch timestamp and return a
    pretty string like 'an hour ago', 'Yesterday', '3 months ago',
    'just now', etc
    """

    t = time.strptime(datetime_format, "%Y-%m-%d %H:%M:%S")
    # convert to datetime
    t = datetime.fromtimestamp(time.mktime(t))
    now = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
    now = time.strptime(now, "%Y-%m-%d %H:%M:%S")
    now = datetime.fromtimestamp(time.mktime(now))
    diff = now - t
    second_diff = diff.seconds
    day_diff = diff.days

    if day_diff < 0:
        return ''

    if day_diff == 0:
        if second_diff < 10:
            return "just now"
        if second_diff < 60:
            result = str(second_diff).split(".")[0]
            if result == "1":
                return "a second ago"
            return str(second_diff).split(".")[0]  + " seconds ago"
        if second_diff < 120:
            return "a minute ago"
        if second_diff < 3600:
            result = str(second_diff / 60).split(".")[0]
            if result == "1":
                return "a minute ago"
            return str(second_diff / 60).split(".")[0]  + " minutes ago"
        if second_diff < 7200:
            return "an hour ago"
        if second_diff < 86400:
            result = str(second_diff / 3600).split(".")[0]
            if result == "1":
                return "an hour ago"
            return str(second_diff / 3600).split(".")[0]  + " hours ago"
    if day_diff == 1:
        return "Yesterday"
    if day_diff < 7:
        result = str(day_diff).split(".")[0]
        if result == "1":
            return "a day ago"
        return str(day_diff).split(".")[0]  + " days ago"
    if day_diff < 31:
        result = str(day_diff / 7).split(".")[0]
        if result == "1":
            return "a week ago"
        return str(day_diff / 7).split(".")[0]  + " weeks ago"
    if day_diff < 365:
        result = str(day_diff / 30).split(".")[0]
        if result == "1":
            return "a month ago"
        return result + " months ago"
    return str(day_diff / 365) + " years ago"

