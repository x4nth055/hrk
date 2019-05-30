import base64
from flask import redirect, request, url_for, session
from passlib.hash import pbkdf2_sha256
from functools import wraps
from flask_dance.contrib.facebook import facebook


import time
import os


def get_query(tablename, fields):
    query = f"CREATE TABLE IF NOT EXISTS {tablename.upper()} ("
    for name, datatype in fields.items():
        query += f"{name} {datatype}, "
    return query.rstrip(", ") + ")"


def get_unique_id(length=8):
    """Generates random secure unique ID that is urlsafe ( i.e can be on url )"""
    return base64.urlsafe_b64encode(os.urandom(length)).decode().strip('=')


def is_pw_correct(password, hashed_password):
    """Test whether `password` that is not hashed is the same as `hashed_password`"""
    return pbkdf2_sha256.verify(password, hashed_password)


def hash_pw(password):
    """Returns hashed version of `password`"""
    return pbkdf2_sha256.hash(password)



def redirect_previous_url(default='home'):
    return redirect(request.args.get('next') or request.referrer or url_for(default))



def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kws):
        name = session.get("name")
        if name is None:
            # if not logged in, get back from where you came!
            # if the first time, go register
            return redirect_previous_url(default="user.register")
        else:
            return f(*args, **kws)            
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kws):
        name = session.get("name")
        type = session.get("type")
        if name is None:
            # if not logged in, get back from where you came!
            # if the first time, go register
            return redirect_previous_url(default='user.register')
        else:
            type = type.strip()
            if type != "admin":
                return redirect_previous_url(default='index')
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
    items = get_function(id)
    print(items)
    return '|'.join([ f"{item_id}__{item}" for item_id, item in items])

