from flask import Blueprint, render_template, request, session, redirect, url_for
from models.users.user import User
from flask_dance.contrib.facebook import make_facebook_blueprint, facebook
from common.database import Database
import common.utils as utils

import time
import json

get_all_universities = Database.get_all_universities
get_faculties = Database.get_faculties
get_departments = Database.get_departments
get_specialities = Database.get_specialities
get_years = Database.get_years
get_groups = Database.get_groups

user_blueprint = Blueprint("user", __name__)

# some utilities

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
    user = User(**user)
    session['id'] = user.id
    session['name'] = user.name
    session['fb_info'] = user.fb_info
    session['university'] = (user.university, Database.get_university_name(user.university))
    session['faculty'] = (user.faculty, Database.get_faculty_name(user.faculty))
    session['department'] = (user.department, Database.get_department_name(user.department))
    session['speciality'] = (user.speciality, Database.get_speciality_name(user.speciality))
    session['year'] = (user.year, Database.get_year_name(user.year))
    session['group'] = (user.group, Database.get_group_name(user.group))
    session['type'] = user.type
    session['score'] = user.score



@user_blueprint.route("/register", methods=["POST", "GET"])
@utils.not_logged_in_required
def register():
    # total steps
    n_steps = 7
    if request.method == "GET":    
        step = 1
        universities = get_all_universities()
        return render_template("register.html", error=False, step=step, n_steps=n_steps, universities=universities)
    elif request.method == "POST":
        step = int(request.form.get("step"))
        print(step)
        if step == 2:
            session['university'] = request.form.get("university")
            university_id = session['university']
            faculties = get_faculties(university_id)
            return render_template("register.html", step=step, n_steps=n_steps, faculties=faculties)
        elif step == 3:
            session['faculty'] = request.form.get("faculty")
            faculty_id = session['faculty']
            departments = get_departments(faculty_id)
            return render_template("register.html", step=step, n_steps=n_steps, departments=departments)
        elif step == 4:
            session['department'] = request.form.get("department")
            department_id = session['department']
            specialities = get_specialities(department_id)
            print(specialities)
            return render_template("register.html", step=step, n_steps=n_steps, specialities=specialities)
        elif step == 5:
            session['speciality'] = request.form.get("speciality")
            speciality_id = session['speciality']
            years = get_years(speciality_id)
            print(years)
            return render_template("register.html", step=step, n_steps=n_steps, years=years)
        elif step == 6:
            session['year'] = request.form.get("year")
            year_id = session['year']
            groups = get_groups(year_id)
            return render_template("register.html", step=step, n_steps=n_steps, groups=groups)
        elif step == 7:
            session['group'] = request.form.get("group")
            # university > faculty > department  > speciality > year > group
            # oauth with facebook
            if not facebook.authorized:
                return redirect(url_for("facebook.login"))

            # get facebook account info
            json = facebook.get("/me").json()
            user_id = json['id']
            name = json['name']
            fb_info = user_id + "|" + name
            session['fb_info'] = fb_info
            return render_template("register.html", step=step, n_steps=n_steps)
        elif step == 8:
            session['name'] = request.form.get("first_name").strip().capitalize() + " " + request.form.get("last_name").strip().capitalize()
            name = session.get("name")
            fb_info = session.get("fb_info")
            university = session.get("university")
            faculty = session.get("faculty")
            department = session.get("department")
            speciality = session.get("speciality")
            year = session.get("year")
            group = session.get("group")
            type = "normal"
            session["type"] = type
            score = 0

            user = User(name=name, fb_info=fb_info, university=university, faculty=faculty, department=department,
                        speciality=speciality, year=year, groupe=group, type=type, score=score)
            user.save()
            
            return redirect(url_for("index"))


@user_blueprint.route("/login", methods=['GET', 'POST'])
@utils.not_logged_in_required
def login():
    # oauth with facebook
    if not facebook.authorized:
        return redirect(url_for("facebook.login"))
    # get facebook account info
    user = _get_user_info()
    if not user:
        # not registered in database, redirect to register
        return redirect(url_for("user.register"))

    _save_user_info(user)

    return redirect(url_for("index"))

@user_blueprint.route("/logout")
@utils.login_required
def logout():
    # clear the session
    session.clear()
    return redirect(url_for('user.register'))


@user_blueprint.route("/vote", methods=['GET', 'POST'])
@utils.login_required
def vote():
    if request.method == 'POST':
        # add new vote
        voted_id = request.form.get("voted_id")
        action = request.form.get("action")
        score = str(Database.add_vote(voter_id=session['id'], voted_id=voted_id, action=action))
        return score
    elif request.method == "GET":
        voted_id = request.args.get("voted_id")
        action = Database.get_vote_action(session['id'], voted_id)
        if action is None:
            return "None"
        return action[0]

@user_blueprint.route("/voters")
@utils.login_required
def voters():
    my_voters = Database.get_user_voters(session['id'], get_usernames=True)
    # get not viewed votes
    # convert voter_id to facebook user names by setting get_usernames to True
    not_viewed_voters = Database.get_not_viewed_voters(session['id'], get_usernames=True)
    # set votes to viewed
    Database.view_vote(session['id'])
    return render_template("votes.html", votes=my_voters, not_viewed_voters=not_viewed_voters,
                            len=len, relative_date=utils.pretty_date, who="My Voters", voters=my_voters)

@user_blueprint.route("/votes")
@utils.login_required
def votes():
    my_votes = Database.get_user_votes(session['id'], get_usernames=True)
    voters = Database.get_user_voters(session['id'], get_usernames=True)
    # get not viewed votes
    # convert voter_id to facebook user names by setting get_usernames to True
    not_viewed_voters = Database.get_not_viewed_voters(session['id'], get_usernames=True)
    return render_template("votes.html", votes=my_votes, not_viewed_voters=not_viewed_voters,
                            len=len, relative_date=utils.pretty_date, who="My Votes", voters=voters)




@user_blueprint.route("/group/<id>")
# @utils.login_required
def users_by_group(id):
    users = Database.get_users_by_group(id)
    return json.dumps(users)

@user_blueprint.route("/speciality/<id>")
@utils.login_required
def users_by_speciality(id):
    users = Database.get_users_by_speciality(id)
    return json.dumps(users)

@user_blueprint.route("/year/<id>")
@utils.login_required
def users_by_year(id):
    users = Database.get_users_by_year(id)
    return json.dumps(users)


@user_blueprint.route("/department/<id>")
@utils.login_required
def users_by_department(id):
    users = Database.get_users_by_department(id)
    return json.dumps(users)

@user_blueprint.route("/faculty/<id>")
@utils.login_required
def users_by_faculty(id):
    users = Database.get_users_by_faculty(id)
    return json.dumps(users)


@user_blueprint.route("/university/<id>")
@utils.login_required
def users_by_university(id):
    users = Database.get_users_by_university(id)
    return json.dumps(users)