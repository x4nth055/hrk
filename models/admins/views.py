from flask import Blueprint, render_template, request, session, current_app as app
from flask import redirect, url_for
from common.database import Database
from common.utils import get_items_from_ajax, redirect_previous_url, admin_required

add_university = Database.add_university
add_faculty = Database.add_faculty
add_department = Database.add_department
add_speciality = Database.add_speciality
add_year = Database.add_year
add_group = Database.add_group

get_all_users = Database.get_all_users
get_all_universities = Database.get_all_universities
get_all_faculties = Database.get_all_faculties
get_all_departments = Database.get_all_departments
get_all_specialities = Database.get_all_specialities
get_all_years = Database.get_all_years
get_all_groups = Database.get_all_groups

get_departments = Database.get_departments
get_faculties = Database.get_faculties
get_specialities = Database.get_specialities
get_years = Database.get_years
get_groups = Database.get_groups

admin_blueprint = Blueprint("admin", __name__)

@admin_blueprint.route("/")
@admin_required
def home():
    n_users = Database.get_number_of_users()
    n_universities = len(get_all_universities())
    n_faculties = len(get_all_faculties())
    n_departments = len(get_all_departments())
    return render_template("admin/index.html", n_users=n_users, n_universities=n_universities,
                            n_faculties=n_faculties, n_departments=n_departments)

@admin_blueprint.route("new_university", methods=['GET', 'POST'])
@admin_required
def new_university():
    if request.method == 'GET':
        return render_template("admin/new_university.html")
    elif request.method == 'POST':
        university = request.form.get("university")
        # add university to the db
        add_university(university)
        return render_template("admin/new_university.html", message="University added successfully.")


@admin_blueprint.route("new_faculty", methods=['GET', 'POST'])
@admin_required
def new_faculty():
    universities = get_all_universities()
    if request.method == 'GET':
        return render_template("admin/new_faculty.html", universities=universities)
    elif request.method == 'POST':
        university_id = request.form.get("university")
        faculty = request.form.get("faculty")
        # add faculty to the db
        add_faculty(faculty, university_id)
        return render_template("admin/new_university.html", universities=universities, message="Faculty added successfully.")


@admin_blueprint.route("new_department", methods=['GET', 'POST'])
@admin_required
def new_department():
    universities = get_all_universities()
    if request.method == 'GET':
        return render_template("admin/new_department.html", universities=universities)
    elif request.method == 'POST':
        department = request.form.get("department")
        faculty_id = request.form.get("faculty")
        # add department to the db
        add_department(department, faculty_id)
        return render_template("admin/new_department.html", universities=universities, message="Department added successfully.")


@admin_blueprint.route("new_speciality", methods=['GET', 'POST'])
@admin_required
def new_speciality():
    universities = get_all_universities()
    if request.method == 'GET':
        return render_template("admin/new_speciality.html", universities=universities)
    elif request.method == 'POST':
        department_id = request.form.get("department")
        speciality = request.form.get("speciality")
        # add speciality to the db
        add_speciality(speciality, department_id)
        return render_template("admin/new_speciality.html", universities=universities, message="Speciality added successfully.")


@admin_blueprint.route("new_year", methods=['GET', 'POST'])
@admin_required
def new_year():
    universities = get_all_universities()
    if request.method == 'GET':
        return render_template("admin/new_year.html", universities=universities)
    elif request.method == 'POST':
        speciality_id = request.form.get("speciality")
        year = request.form.get("year")
        # add year to the db
        add_year(year, speciality_id)
        return render_template("admin/new_year.html", universities=universities, message="Year added successfully.")


@admin_blueprint.route("new_group", methods=['GET', 'POST'])
@admin_required
def new_group():
    universities = get_all_universities()
    if request.method == 'GET':
        return render_template("admin/new_group.html", universities=universities)
    elif request.method == 'POST':
        year_id = request.form.get("year")
        group = request.form.get("group")
        # add group to the db
        add_group(group, year_id)
        return render_template("admin/new_group.html", universities=universities, message="Group added successfully.")


@admin_blueprint.route("users")
@admin_required
def user():
    users = [ (data['id'], data['fb_info'].split("|")[0], data['fb_info'].split("|")[1], data['type'], data['score']) for data in get_all_users(formalize=True) ]
    fields = ["ID", "Facebook ID", "Facebook Name", "User Type", "Reputation/Score"]
    return render_template("admin/items.html", items=users, fields=fields, name="users", len=len)


@admin_blueprint.route("universities")
@admin_required
def university():
    universities = get_all_universities()
    # fields = [ field.lower() for field in Database.UNIVERSITY_FIELDS ]
    fields = ["University ID", "University Name"]
    return render_template("admin/items.html", items=universities, fields=fields, name="universities", len=len)

@admin_blueprint.route("faculties")
@admin_required
def faculty():
    faculties = get_all_faculties(all_fields=True)
    # fields = [ field.lower() for field in Database.FACULTY_FIELDS ]
    fields = ["Faculty ID", "Faculty Name", "University"]
    return render_template("admin/items.html", items=faculties, fields=fields, name="faculties", len=len)


@admin_blueprint.route("departments")
@admin_required
def department():
    departments = get_all_departments(all_fields=True)
    # fields = [ field.lower() for field in Database.DEPARTMENT_FIELDS ]
    fields = ["Department ID", "Department Name", "Faculty", "University"]
    return render_template("admin/items.html", items=departments, fields=fields, name="departments", len=len)


@admin_blueprint.route("specialities")
@admin_required
def speciality():
    specialities = get_all_specialities(all_fields=True)
    # fields = [ field.lower() for field in Database.SPECIALITY_FIELDS ]
    fields = ["Speciality ID", "Speciality Name", "Department", "Faculty", "University"]
    return render_template("admin/items.html", items=specialities, fields=fields, name="specialities", len=len)


@admin_blueprint.route("years")
@admin_required
def year():
    years = get_all_years(all_fields=True)
    # fields = [ field.lower() for field in Database.YEAR_FIELDS ]
    fields = ["Year ID", "Year", "Speciality", "Department", "Faculty", "University"]
    return render_template("admin/items.html", items=years, name="years", fields=fields, len=len)


@admin_blueprint.route("groups")
@admin_required
def group():
    groups = get_all_groups(all_fields=True)
    # fields = [ field.lower() for field in Database.GROUP_FIELDS ]
    fields = ["Group ID", "Group Number", "Year", "Speciality", "Department", "Faculty", "University"]
    return render_template("admin/items.html", items=groups, name="groups", fields=fields, len=len)

## Below are for AJAX calls

@admin_blueprint.route("fac", methods=['POST'])
@admin_required
def faculties():
    return get_items_from_ajax(get_faculties)

@admin_blueprint.route("dep", methods=['POST'])
@admin_required
def departments():
    return get_items_from_ajax(get_departments)

@admin_blueprint.route("spec", methods=['POST'])
@admin_required
def specialities():
    return get_items_from_ajax(get_specialities)

@admin_blueprint.route("year", methods=['POST'])
@admin_required
def years():
    return get_items_from_ajax(get_years)

@admin_blueprint.route("group", methods=['POST'])
@admin_required
def groups():
    return get_items_from_ajax(get_groups)

## Item Deletions

@admin_blueprint.route("delete_users/<id>")
@admin_required
def delete_users(id):
    Database.delete_user(id)
    return redirect_previous_url()

@admin_blueprint.route("delete_university/<id>")
@admin_required
def delete_universities(id):
    Database.delete_university(id)
    return redirect_previous_url()

@admin_blueprint.route("delete_faculty/<id>")
@admin_required
def delete_faculties(id):
    Database.delete_faculty(id)
    return redirect_previous_url()

@admin_blueprint.route("delete_department/<id>")
@admin_required
def delete_departments(id):
    Database.delete_department(id)
    return redirect_previous_url()

@admin_blueprint.route("delete_speciality/<id>")
@admin_required
def delete_specialities(id):
    Database.delete_speciality(id)
    return redirect_previous_url()

@admin_blueprint.route("delete_year/<id>")
@admin_required
def delete_years(id):
    Database.delete_year(id)
    return redirect_previous_url()

@admin_blueprint.route("delete_group/<id>")
@admin_required
def delete_groups(id):
    Database.delete_group(id)
    return redirect_previous_url()

# Item editions
@admin_blueprint.route("edit_user/")
@admin_required
def edit_user():
    id = request.args.get("id")
    type = request.args.get("type")
    print(id)
    print(type)
    Database.edit_user(id, type=type)
    return redirect_previous_url()