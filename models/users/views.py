from flask import Blueprint, render_template, request, session, redirect, url_for
from models.users.user import User
from flask_dance.contrib.facebook import make_facebook_blueprint, facebook
from common.database import Database
import common.utils as utils

get_all_universities = Database.get_all_universities
get_faculties = Database.get_faculties
get_departments = Database.get_departments
get_specialities = Database.get_specialities
get_years = Database.get_years
get_groups = Database.get_groups

user_blueprint = Blueprint("user", __name__)

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
            session['name'] = request.form.get("first_name").strip() + " " + request.form.get("last_name").strip()
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
                        speciality=speciality, year=year, group=group, type=type, score=score)
            user.save()
            
            return redirect(url_for("index"))


@user_blueprint.route("/login", methods=['GET', 'POST'])
@utils.not_logged_in_required
def login():
    # oauth with facebook
    if not facebook.authorized:
        return redirect(url_for("facebook.login"))
    # get facebook account info
    json = facebook.get("/me").json()
    user_id = json['id']
    name = json['name']
    fb_info = user_id + "|" + name
    print("[*]", fb_info, "logged")
    user = Database.get_user_by_fb_info(fb_info)
    if not user:
        # not registered in database, redirect to register
        return redirect(url_for("user.register"))
    user = User(**user)
    session['id'] = user.id
    session['name'] = user.name
    session['fb_info'] = user.fb_info
    session['university'] = Database.get_university_name(user.university)
    session['faculty'] = Database.get_faculty_name(user.faculty)
    session['department'] = Database.get_department_name(user.department)
    session['speciality'] = Database.get_speciality_name(user.speciality)
    session['year'] = Database.get_year_name(user.year)
    session['group'] = Database.get_group_name(user.group)
    session['type'] = user.type
    session['score'] = user.score
    
    return redirect(url_for("index"))


@user_blueprint.route("/logout")
@utils.login_required
def logout():
    # clear the session
    session.clear()
    return utils.redirect_previous_url(default="index")