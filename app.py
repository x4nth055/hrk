from flask import Flask, request, url_for, redirect, flash, session, render_template
from config import FACEBOOK_APP_ID, FACEBOOK_APP_SECRET, MINIMUM_UNCHANGEABLE_SCORE
from flask_dance.contrib.facebook import make_facebook_blueprint, facebook
from models.users.views import user_blueprint
from models.users.user import User
from models.admins.views import admin_blueprint
from common.database import Database
from common.utils import login_required, admin_required, get_items_from_ajax


import time
import os
import json

os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = "1" 

app = Flask(__name__)
app.secret_key = "secret"
blueprint = make_facebook_blueprint(client_id=FACEBOOK_APP_ID, client_secret=FACEBOOK_APP_SECRET)
app.register_blueprint(user_blueprint, url_prefix="/user")
app.register_blueprint(blueprint, url_prefix="/login")
app.register_blueprint(admin_blueprint, url_prefix="/admin")


# this function will run initially (i.e when the app is executed)
@app.before_first_request
def init_db():
    Database.init()


@app.route("/")
@login_required
def index():
    
    users = Database.get_users_by_group(session['group'][0])
    facebook_user_id = session['fb_info'].split("|")[0]
    facebook_group_url = Database.get_faculty_fbgroup(session['faculty'][0])

    # get not viewed votes
    # convert voter_id to facebook user names by setting get_usernames to True
    not_viewed_voters = Database.get_not_viewed_voters(session['id'], get_usernames=True)
    voters = Database.get_user_voters(session['id'], get_usernames=True)
    return render_template("index.html", users=users, facebook_user_id=facebook_user_id,
                            facebook_group_url=facebook_group_url, not_viewed_voters=not_viewed_voters,
                            len=len, voters=voters)


@app.route("/profile")
@login_required
def profile():
    # get not viewed votes
    # convert voter_id to facebook user names by setting get_usernames to True
    not_viewed_voters = Database.get_not_viewed_voters(session['id'], get_usernames=True)
    voters = Database.get_user_voters(session['id'], get_usernames=True)
    votes = Database.get_user_votes(session['id'], get_usernames=True)
    # get whether the user can change his information
    changeable = Database.get_user_by_id(session['id'])['score'] < MINIMUM_UNCHANGEABLE_SCORE

    return render_template("profile.html", not_viewed_voters=not_viewed_voters,
                                len=len, voters=voters, votes=votes, changeable=changeable)


## Below are for some AJAX calls

@app.route("/university", methods=['POST'])
# @login_required
def university():
    return json.dumps(Database.get_all_universities())

@app.route("/faculty", methods=['POST'])
# @login_required
def faculty():
    return get_items_from_ajax(Database.get_faculties)

@app.route("/department", methods=['POST'])
# @login_required
def department():
    return get_items_from_ajax(Database.get_departments)

@app.route("/speciality", methods=['POST'])
# @login_required
def speciality():
    return get_items_from_ajax(Database.get_specialities)

@app.route("/year", methods=['POST'])
# @login_required
def year():
    return get_items_from_ajax(Database.get_years)

@app.route("/group", methods=['POST'])
# @login_required
def group():
    return get_items_from_ajax(Database.get_groups)


port = int(os.environ.get('PORT', 5000))
app.run(host='0.0.0.0', port=port, debug=False)