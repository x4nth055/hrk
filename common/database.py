import sqlite3
from common.db_utils import get_query, get_unique_id
from config import ADMIN_VOTE_AMOUNT, MODERATOR_VOTE_AMOUNT, NORMAL_VOTE_AMOUNT, MINIMUM_REQUIRED_SCORE
from config import SCORE_TO_DELETE

class Database:
    URL = "db/db.sqlite3"
    DATABASE = None

    # all models' (i.e tables') fields should be listed here
    USER_FIELDS = {
        "ID": "VARCHAR",
        "NAME": "VARCHAR",
        "FB_INFO": "VARCHAR UNIQUE",
        "UNIVERSITY": "VARCHAR",
        "FACULTY": "VARCHAR",
        "DEPARTMENT": "VARCHAR",
        "SPECIALITY": "VARCHAR",
        "YEAR": "VARCHAR",
        "GROUPE": "VARCHAR",
        "TYPE": "VARCHAR",
        "SCORE": "INTEGER"
    }

    # university > faculty > department > speciality > year > group
    UNIVERSITY_FIELDS = {
        "ID": "VARCHAR UNIQUE",
        "NAME": "VARCHAR",
    }

    FACULTY_FIELDS = {
        "ID": "VARCHAR UNIQUE",
        "NAME": "VARCHAR",
        "UNIVERSITY_ID": "VARCHAR",
        "FACEBOOK_GROUP_URL": "VARCHAR"
    }

    DEPARTMENT_FIELDS = {
        "ID": "VARCHAR UNIQUE",
        "NAME": "VARCHAR",
        "FACULTY_ID": "VARCHAR"        
    }

    SPECIALITY_FIELDS = {
        "ID": "VARCHAR UNIQUE",
        "NAME": "VARCHAR",
        "DEPARTMENT_ID": "VARCHAR"
    }

    YEAR_FIELDS = {
        "ID": "VARCHAR UNIQUE",
        "NAME": "VARCHAR",
        "SPECIALITY_ID": "VARCHAR",
    }

    GROUP_FIELDS = {
        "ID": "VARCHAR UNIQUE",
        "NAME": "VARCHAR",
        "YEAR_ID": "VARCHAR"
    }

    VOTE_FIELDS = {
        "VOTER_ID": "VARCHAR",
        "VOTED_ID": "VARCHAR",
        "ACTION": "VARCHAR",
        "VIEWED": "INTEGER",
        "VOTED_AT": "DATETIME DEFAULT CURRENT_TIMESTAMP",
        "PRIMARY KEY": "(VOTER_ID, VOTED_ID)"
    }

    # all table queries need to be added here
    TABLE_QUERIES = [
        get_query("USER", USER_FIELDS),
        get_query("UNIVERSITY", UNIVERSITY_FIELDS),
        get_query("FACULTY", FACULTY_FIELDS),
        get_query("DEPARTMENT", DEPARTMENT_FIELDS),
        get_query("SPECIALITY", SPECIALITY_FIELDS),
        get_query("YEAR", YEAR_FIELDS),
        get_query("GROUPE", GROUP_FIELDS),
        get_query("VOTE", VOTE_FIELDS)
    ]

    @classmethod
    def init(cls):
        cls.DATABASE = sqlite3.connect(cls.URL, check_same_thread=False)
        # create tables
        for query in cls.TABLE_QUERIES:
            print(query)
            cls.DATABASE.execute(query)

    ### User Entity ###

    @classmethod
    def get_number_of_users(cls):
        cursor = cls.DATABASE.execute("SELECT COUNT(*) FROM USER")
        return cursor.fetchone()[0]

    @classmethod
    def save_user(cls, **kwargs):
        """Saves user to the database"""
        id = kwargs.get("id")
        name = kwargs.get("name")
        fb_info = kwargs.get("fb_info")
        university = kwargs.get("university")
        faculty = kwargs.get("faculty")
        department = kwargs.get("department")
        speciality = kwargs.get("speciality")
        year = kwargs.get("year")
        group = kwargs.get("group")
        type = kwargs.get("type")
        score = kwargs.get("score")
        # using the secure Python DB-API 2.0’s parameter substitution 
        # for preventing SQL Injection
        parameters = (id, name, fb_info, university, faculty, department, speciality, year, group, type, score)
        cls.DATABASE.execute("INSERT INTO USER VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", parameters)
        cls.DATABASE.commit()

    @classmethod
    def delete_user(cls, id):
        cls.DATABASE.execute("DELETE FROM USER WHERE ID=?", (id,))
        cls.DATABASE.commit()
        return True

    @classmethod
    def edit_user(cls, id, commit=True, **kwargs):
        """Changes USER attribute using `kwargs`"""
        query = "UPDATE USER SET"
        parameters = []
        for field, value in kwargs.items():
            field = field.replace("group", "groupe")
            if field not in [ f.lower() for f in cls.USER_FIELDS ]:
                raise TypeError("Table Column not found:" + field)
            if field == "university" and value is not None:
                # if university is edited, set FACULTY, DEPARTMENT,
                # YEAR, SPECIALITY, GROUP to NULL
                cls.edit_user(id, commit=False, faculty=None, department=None, year=None, speciality=None, group=None)
            elif field == "faculty" and value is not None:
                # if university is edited, set DEPARTMENT, YEAR
                # SPECIALITY, GROUP to NULL
                cls.edit_user(id, commit=False, department=None, year=None, speciality=None, group=None)
            elif field == "department" and value is not None:
                cls.edit_user(id, commit=False, speciality=None, year=None, group=None)
            elif field == "speciality" and value is not None:
                cls.edit_user(id, commit=False, year=None, group=None)
            elif field == "year" and value is not None:
                cls.edit_user(id, commit=False, group=None)
            query += f" {field} = ?,"
            parameters.append(value)
        query = query.rstrip(",")
        query += " WHERE ID=?"
        parameters.append(id)
        cls.DATABASE.execute(query, parameters)
        if commit:
            cls.DATABASE.commit()
        return True

    @classmethod
    def _get_user_by(cls, key, value):
        cursor = cls.DATABASE.execute(f"SELECT * FROM USER WHERE {key}=?", (value,))
        returned_data = cursor.fetchone()
        if returned_data is None:
            return None
        data = {}
        for i, field in enumerate(cls.USER_FIELDS):
            data[field.lower()] = returned_data[i]
        return data

    @classmethod
    def get_user_by_id(cls, id):
        """Get user data from its id.
            The returned dict is in the format:
            {'ID': id, 'NAME': name, 'EMAIL': email, 'PASSWORD': password}
            Returns None when user is not found
                """
        return cls._get_user_by("ID", id)

    @classmethod
    def get_user_by_name(cls, name):
        """Get user data from his/her name"""
        return cls._get_user_by("NAME", name)

    @classmethod
    def get_user_by_fb_info(cls, fb_info):
        return cls._get_user_by("FB_INFO", fb_info)

    @classmethod
    def get_users_like_name(cls, name, formalize=True):
        cursor = cls.DATABASE.execute("SELECT * FROM USER WHERE NAME LIKE ? OR FB_INFO LIKE ?", (f"%{name}%",))
        returned_data = cursor.fetchall()
        if not returned_data:
            return None
        if not formalize:
            return returned_data
        data = []
        for item in returned_data:
            d = {}
            for i, field in enumerate(cls.USER_FIELDS):
                d[field.lower()] = item[i]
            data.append(d)
        return data

    @classmethod
    def _get_users_by(cls, key, value, formalize=True):
        cursor = cls.DATABASE.execute(f"SELECT * FROM USER WHERE {key}=? ORDER BY SCORE DESC ", (value,))
        returned_data = cursor.fetchall()
        if not formalize:
            return returned_data
        data = []
        for item in returned_data:
            d = {}
            for i, field in enumerate(cls.USER_FIELDS):
                d[field.lower()] = item[i]
            data.append(d)
        return data

    @classmethod
    def get_users_by_name(cls, name, formalize=True):
        """Get a list of users by name"""
        return cls._get_users_by("NAME", name, formalize)

    @classmethod
    def get_users_by_fb(cls, fb_info, formalize=True):
        """Get a list of users by FB_INFO"""
        return cls._get_users_by("FB_INFO", fb_info, formalize)

    @classmethod
    def get_users_by_university(cls, university, formalize=True):
        return cls._get_users_by("UNIVERSITY", university, formalize)

    @classmethod
    def get_users_by_department(cls, department, formalize=True):
        return cls._get_users_by("DEPARTMENT", department, formalize)

    @classmethod
    def get_users_by_speciality(cls, speciality, formalize=True):
        return cls._get_users_by("SPECIALITY", speciality, formalize)

    @classmethod
    def get_users_by_faculty(cls, faculty, formalize=True):
        return cls._get_users_by("FACULTY", faculty, formalize)

    @classmethod
    def get_users_by_year(cls, year, formalize=True):
        return cls._get_users_by("YEAR", year, formalize)

    @classmethod
    def get_users_by_group(cls, group, formalize=True):
        return cls._get_users_by("GROUPE", group, formalize)

    @classmethod
    def get_users_by_fields(cls, fields, formalize=True):
        """Retrieves users by many fields
        e.g. 
        fields = {
            'name': 'mohammed',
            'department': 'computer science'    
        }
        this will retrieve all rows that have name of 'mohammed'
        and department of 'computer science'"""
        users = None
        for key, value in fields.items():
            if users:
                # intersection
                users &= set(cls._get_users_by(key.upper(), value, formalize))
            else:
                users = set(cls._get_users_by(key.upper(), value, formalize))

    @classmethod
    def get_all_users(cls, formalize=True):
        cursor = cls.DATABASE.execute("SELECT * FROM USER")
        returned_data = cursor.fetchall()
        if not formalize:
            return returned_data
        data = []
        for item in returned_data:
            d = {}
            for i, field in enumerate(cls.USER_FIELDS):
                d[field.lower()] = item[i]
            data.append(d)
        return data

    @classmethod
    def add_user_score(cls, id, amount):
        cls.DATABASE.execute(f"UPDATE USER SET SCORE = SCORE + {amount} WHERE ID = ?", (id,))
        cls.DATABASE.commit()
        return True

    ### Vote entity ###
    
    @classmethod
    def get_user_votes(cls, voter_id, get_usernames=False):
        cursor = cls.DATABASE.execute("SELECT VOTED_ID, ACTION, VOTED_AT FROM VOTE WHERE VOTER_ID = ? ORDER BY VOTED_AT DESC", (voter_id,))
        returned_data = cursor.fetchall()
        data = []
        for item in returned_data:
            d = {}
            for i, field in enumerate(["id", "action", "voted_at"]):
                if i == 0 and get_usernames:
                    try:
                        d[field] = cls.get_user_by_id(item[i])['fb_info'].split("|")[1]
                    except TypeError as e:
                        d[field.lower()] = item[i]
                    continue
                d[field.lower()] = item[i]
            data.append(d)
        return data

    @classmethod
    def get_user_voters(cls, voted_id, get_usernames=False):
        cursor = cls.DATABASE.execute("SELECT VOTER_ID, ACTION, VOTED_AT FROM VOTE WHERE VOTED_ID = ? ORDER BY VOTED_AT DESC", (voted_id,))
        returned_data = cursor.fetchall()
        data = []
        for item in returned_data:
            d = {}
            for i, field in enumerate(["id", "action", "voted_at"]):
                if i == 0 and get_usernames:
                    d[field] = cls.get_user_by_id(item[i])['fb_info'].split("|")[1]
                    continue
                d[field.lower()] = item[i]
            data.append(d)
        return data

    @classmethod
    def get_vote_action(cls, voter_id, voted_id):
        return cls.DATABASE.execute("SELECT ACTION FROM VOTE WHERE VOTER_ID = ? AND VOTED_ID = ?", (voter_id, voted_id)).fetchone()

    @classmethod
    def delete_vote(cls, voter_id, voted_id):
        cls.DATABASE.execute("DELETE FROM VOTE WHERE VOTER_ID = ? AND VOTED_ID = ?", (voter_id, voted_id))
        cls.DATABASE.commit()

    @classmethod
    def view_vote(cls, voted_id):
        """Views all the votes for `voted_id` ( set all the rows VIEWED = 1 )
        This function is useful when removing user notifications"""
        cls.DATABASE.execute("UPDATE VOTE SET VIEWED = 1 WHERE VOTED_ID = ?", (voted_id,))
        cls.DATABASE.commit()

    @classmethod
    def get_not_viewed_voters(cls, voted_id, get_usernames=False):
        """This function returns all non-viewed votes ( i.e where VIEWED = 0 )"""
        cursor = cls.DATABASE.execute("SELECT * FROM VOTE WHERE VOTED_ID = ? AND VIEWED = 0 ORDER BY VOTED_AT DESC", (voted_id,))
        returned_data = cursor.fetchall()
        data = []
        for item in returned_data:
            d = {}
            for i, field in enumerate(['voter_id', 'voted_id', 'action', 'viewed', 'voted_at']):
                if i == 0 and get_usernames:
                    user = cls.get_user_by_id(item[i])
                    user_name = user['fb_info']
                    d[field.lower()] = user_name.split("|")[1]
                    continue
                d[field.lower()] = item[i]
            data.append(d)
        return data
        

    @classmethod
    def add_vote(cls, voter_id, voted_id, action):
        """Add a new vote.
        - if voter is the voted, does nothing and returns "Cannot vote your self."
        - if voter's score is not enough, does nothing and returns "Not enough reputation to vote.".
        - if no existing vote before is available, register a new vote based on `action` and returns the updated score
        - if there are already an existing vote with that `voter_id` and `voted_id`, there are 3 cases:
            1. if the previous action (vote) is same as the new `action`, just returns score.
            2. if the previous action is 'down' and new `action` is 'up',
                insert a new vote and add `2*amount` ( cancel the previous and add current ) 
                to the `voted_id`'s score and returns the updated score
            3. if the previous action is 'up' and new `action` is 'down',
                insert a new vote and subtract `2*amount` to the `voted_id`'s score
                and returns the updated score"""
        if voter_id == voted_id:
            return "You cannot vote your self."
        score = None
        action = action.lower()
        voter = cls.get_user_by_id(voter_id)
        if voter['score'] < MINIMUM_REQUIRED_SCORE:
            # if voter does not enough score to vote, just return False
            return f"You do not have enough reputation to vote, minimum required is {MINIMUM_REQUIRED_SCORE}."
        # get score to be added depends on voter type
        if voter['type'] == 'admin':
            amount = ADMIN_VOTE_AMOUNT
        elif voter['type'] == 'moderator':
            amount = MODERATOR_VOTE_AMOUNT
        elif voter['type'] == 'normal':
            amount = NORMAL_VOTE_AMOUNT
        # get previous vote if available
        existing_action = cls.get_vote_action(voter_id, voted_id)
        if existing_action is None:
        #     "VOTER_ID": "VARCHAR",
            # "VOTED_ID": "VARCHAR",
            # "ACTION": "VARCHAR",
            # "VIEWED": "VARCHAR",
            # "VOTED_AT": "DATETIME DEFAULT CURRENT_TIMESTAMP",
            # "PRIMARY KEY": "(VOTER_ID, VOTED_ID)"
            # no existing action before
            cls.DATABASE.execute("INSERT INTO VOTE (VOTER_ID, VOTED_ID, ACTION, VIEWED ) VALUES ( ?, ?, ?, 0 )", (voter_id, voted_id, action))
            if action == "up":
                cls.add_user_score(voted_id, amount)
            elif action == "down":
                cls.add_user_score(voted_id, -amount)
                score = cls.get_user_by_id(voted_id)['score']
                if score <= SCORE_TO_DELETE:
                    # if score is below -5 or so, delete the user
                    cls.delete_user(voted_id)

            return score if score else cls.get_user_by_id(voted_id)['score']
        else:
            existing_action = existing_action[0].lower()
            if existing_action == action:
                # already did that action
                return cls.get_user_by_id(voted_id)['score']
            else:
                # delete previous vote
                cls.delete_vote(voter_id, voted_id)
                # insert new vote
                cls.DATABASE.execute("INSERT INTO VOTE (VOTER_ID, VOTED_ID, ACTION, VIEWED ) VALUES ( ?, ?, ?, 0 )", (voter_id, voted_id, action))
                if existing_action == "down" and action == "up":
                    cls.add_user_score(voted_id, 2*amount)
                else:
                    # existing_action = "up" and new_action = "down"
                    cls.add_user_score(voted_id, -2*amount)
                    score = cls.get_user_by_id(voted_id)['score']
                    if score <= SCORE_TO_DELETE:
                        # if score is below -5 or so, delete the user
                        cls.delete_user(voted_id)
                return score if score else cls.get_user_by_id(voted_id)['score']


    ## Utilities

    @classmethod
    def _delete(cls, class_name, id):
        cls.DATABASE.execute(f"DELETE FROM {class_name} WHERE ID = ?", (id,))
        return cls.DATABASE.commit()

    @classmethod
    def _get_name(cls, class_name, id):
        name = cls.DATABASE.execute(f"SELECT NAME FROM {class_name.upper()} WHERE ID = ?", (id,)).fetchone()
        return name[0] if name else None

    ### Univerity entity ###

    @classmethod
    def add_university(cls, name):
        """Insert a new university to the database. Note that the id will be generated automatically"""
        id = get_unique_id(length=8)
        cls.DATABASE.execute("INSERT INTO UNIVERSITY VALUES ( ?, ? )", (id, name,))
        cls.DATABASE.commit()

    @classmethod
    def delete_university(cls, id):
        return cls._delete("UNIVERSITY", id)

    @classmethod
    def get_university_name(cls, id):
        return cls._get_name("UNIVERSITY", id)

    ### Faculty entity ###
    
    @classmethod
    def add_faculty(cls, name, university_id, facebook_group_url):
        id = get_unique_id(length=8)
        cls.DATABASE.execute("INSERT INTO FACULTY VALUES ( ?, ?, ?, ? )", (id, name, university_id, facebook_group_url))
        cls.DATABASE.commit()

    @classmethod
    def delete_faculty(cls, id):
        return cls._delete("FACULTY", id)

    @classmethod
    def get_faculty_name(cls, id):
        return cls._get_name("FACULTY", id)

    @classmethod
    def get_faculty_fbgroup(cls, id):
        return cls.DATABASE.execute("SELECT FACEBOOK_GROUP_URL FROM FACULTY WHERE FACULTY.ID = ?", (id,)).fetchone()

    ### Department entity ###

    @classmethod
    def add_department(cls, name, faculty_id):
        """Adds a new department to the database, `name` is the name of the new department"""
        id = get_unique_id(length=8)
        cls.DATABASE.execute("INSERT INTO DEPARTMENT VALUES ( ?, ?, ? )", (id, name, faculty_id))
        cls.DATABASE.commit()

    @classmethod
    def delete_department(cls, id):
        return cls._delete("DEPARTMENT", id)

    @classmethod
    def get_department_name(cls, id):
        return cls._get_name("DEPARTMENT", id)


    ### Speciality entity ###

    @classmethod
    def add_speciality(cls, name, department_id):
        """Adds a new speciality to a `year` of a `department`"""
        id = get_unique_id(length=8)
        cls.DATABASE.execute("INSERT INTO SPECIALITY VALUES ( ?, ?, ? )", (id, name, department_id))
        cls.DATABASE.commit()

    @classmethod
    def delete_speciality(cls, id):
        return cls._delete("SPECIALITY", id)

    @classmethod
    def get_speciality_name(cls, id):
        return cls._get_name("SPECIALITY", id)

    ### Year entity ###

    @classmethod
    def add_year(cls, name, speciality_id):
        """Adds a new year row to the database, `name` is the name of the year"""
        id = get_unique_id(length=8)
        cls.DATABASE.execute("INSERT INTO YEAR VALUES ( ?, ?, ? )", (id, name, speciality_id))
        cls.DATABASE.commit()

    @classmethod
    def delete_year(cls, id):
        return cls._delete("YEAR", id)

    @classmethod
    def get_year_name(cls, id):
        return cls._get_name("YEAR", id)

    ### Group entity ###

    @classmethod
    def add_group(cls, name, year_id):
        """Adds a new group to a `year` of a `speciality`"""
        id = get_unique_id(length=8)
        cls.DATABASE.execute("INSERT INTO GROUPE VALUES ( ?, ?, ? )", (id, name, year_id))
        cls.DATABASE.commit()

    @classmethod
    def delete_group(cls, id):
        return cls._delete("GROUPE", id)

    @classmethod
    def get_group_name(cls, id):
        return cls._get_name("GROUPE", id)

    ## Joins ##

    @classmethod
    def get_all_universities(cls):
        cursor = cls.DATABASE.execute(f"SELECT ID, NAME FROM UNIVERSITY")
        return cursor.fetchall()

    @classmethod
    def get_all_faculties(cls, all_fields=False):
        if all_fields:
            cursor = cls.DATABASE.execute("""SELECT FACULTY.ID, FACULTY.NAME, UNIVERSITY.NAME, FACULTY.FACEBOOK_GROUP_URL
                                            FROM FACULTY, UNIVERSITY
                                            WHERE UNIVERSITY.ID = FACULTY.UNIVERSITY_ID""")
        else:
            cursor = cls.DATABASE.execute("SELECT ID, NAME FROM FACULTY")
        return cursor.fetchall()

    @classmethod
    def get_all_departments(cls, all_fields=False):
        if all_fields:
            cursor = cls.DATABASE.execute("""SELECT DEPARTMENT.ID, DEPARTMENT.NAME, FACULTY.NAME, UNIVERSITY.NAME
                                            FROM DEPARTMENT, FACULTY, UNIVERSITY
                                            WHERE DEPARTMENT.FACULTY_ID = FACULTY.ID
                                            AND FACULTY.UNIVERSITY_ID = UNIVERSITY.ID""")
        else:
            cursor = cls.DATABASE.execute("SELECT ID, NAME FROM DEPARTMENT")
        return cursor.fetchall()

    @classmethod
    def get_all_specialities(cls, all_fields=False):
        if all_fields:
            cursor = cls.DATABASE.execute("""SELECT SPECIALITY.ID, SPECIALITY.NAME, DEPARTMENT.NAME, FACULTY.NAME, UNIVERSITY.NAME
                                            FROM SPECIALITY, DEPARTMENT, FACULTY, UNIVERSITY
                                            WHERE SPECIALITY.DEPARTMENT_ID = DEPARTMENT.ID
                                            AND DEPARTMENT.FACULTY_ID = FACULTY.ID
                                            AND FACULTY.UNIVERSITY_ID = UNIVERSITY.ID""")
        else:
            cursor = cls.DATABASE.execute("SELECT ID, NAME FROM SPECIALITY")
        return cursor.fetchall()

    @classmethod
    def get_all_years(cls, all_fields=False):
        if all_fields:
            cursor = cls.DATABASE.execute("""SELECT YEAR.ID, YEAR.NAME, SPECIALITY.NAME, DEPARTMENT.NAME, FACULTY.NAME, UNIVERSITY.NAME
                                            FROM YEAR, SPECIALITY, DEPARTMENT, FACULTY, UNIVERSITY
                                            WHERE YEAR.SPECIALITY_ID = SPECIALITY.ID
                                            AND SPECIALITY.DEPARTMENT_ID = DEPARTMENT.ID
                                            AND DEPARTMENT.FACULTY_ID = FACULTY.ID
                                            AND FACULTY.UNIVERSITY_ID = UNIVERSITY.ID""")
        else:
            cursor = cls.DATABASE.execute("SELECT ID, NAME FROM YEAR")
        return cursor.fetchall()

    @classmethod
    def get_all_groups(cls, all_fields=False):
        if all_fields:
            cursor = cls.DATABASE.execute("""SELECT GROUPE.ID, GROUPE.NAME, YEAR.NAME, SPECIALITY.NAME, DEPARTMENT.NAME, FACULTY.NAME, UNIVERSITY.NAME
                                            FROM GROUPE, YEAR, SPECIALITY, DEPARTMENT, FACULTY, UNIVERSITY
                                            WHERE GROUPE.YEAR_ID = YEAR.ID
                                            AND YEAR.SPECIALITY_ID = SPECIALITY.ID
                                            AND SPECIALITY.DEPARTMENT_ID = DEPARTMENT.ID
                                            AND DEPARTMENT.FACULTY_ID = FACULTY.ID
                                            AND FACULTY.UNIVERSITY_ID = UNIVERSITY.ID""")
        else:
            cursor = cls.DATABASE.execute("SELECT ID, NAME FROM YEAR")
        return cursor.fetchall()

    @classmethod
    def get_faculties(cls, university_id):
        cursor = cls.DATABASE.execute("SELECT ID, NAME FROM FACULTY WHERE FACULTY.UNIVERSITY_ID = ?", (university_id,))
        return cursor.fetchall()

    @classmethod
    def get_departments(cls, faculty_id):
        cursor = cls.DATABASE.execute("""SELECT ID, NAME FROM DEPARTMENT WHERE DEPARTMENT.FACULTY_ID = ?""", (faculty_id,))
        return cursor.fetchall()

    @classmethod
    def get_specialities(cls, department_id):
        cursor = cls.DATABASE.execute("SELECT ID, NAME FROM SPECIALITY WHERE SPECIALITY.DEPARTMENT_ID = ?", (department_id,))
        return cursor.fetchall()

    @classmethod
    def get_years(cls, speciality_id):
        cursor = cls.DATABASE.execute("SELECT ID, NAME FROM YEAR WHERE YEAR.SPECIALITY_ID = ?", (speciality_id,))
        return cursor.fetchall()

    @classmethod
    def get_groups(cls, year_id):
        cursor = cls.DATABASE.execute("SELECT ID, NAME FROM GROUPE WHERE GROUPE.YEAR_ID = ?", (year_id,))
        return cursor.fetchall()

    