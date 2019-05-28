from common.database import Database as database
import common.utils as utils


class User:
    def __init__(self, name, fb_info, university, faculty, department, speciality, year, group, type, score, id=None):
        self.name = name
        self.fb_info = fb_info
        self.university = university
        self.faculty = faculty
        self.department = department
        self.speciality = speciality
        self.year = year
        self.group = group
        self.type = type
        self.score = score
        self.id = id

    def exists(self):
        """Whether this user exists in the database"""
        return database.get_user_by_fb_info(self.fb_info)

    def is_admin(self):
        """This methods verifies whether this user is an admin."""
        user_data = self.exists()
        if user_data:
            return user_data['type'] == "admin"
        else:
            return False

    def is_moderator(self):
        """This methods verifies whether this user is an moderator."""
        user_data = self.exists()
        if user_data:
            return user_data['type'] == "moderator"
        else:
            return False

    def load(self):
        """Loads the user data if its valid"""
        user = self.exists()
        if user:
            self.id = user['id']
            self.name = user['name']
            self.fb_info = user['fb_info']
            self.university = user['university']
            self.faculty = user['faculty']
            self.department = user['department']
            self.speciality = user['speciality']
            self.year = user['year']
            self.group = user['group']
            self.type = user['type']
            self.score = user['score']
        else:
            # if user does not exist, generate unique id
            self.id = utils.get_unique_id()
            self.new = True

    def save(self):
        """Saves the user data if email doesn't exist and returns True.
            otherwise does nothing and return False"""
        if not self.exists():
            if not self.id:
                self.id = utils.get_unique_id()
            database.save_user(**self.json())
            self.new = True
            return True
        else:
            return False

    def json(self):
        return {
            "id": self.id,
            "name": self.name,
            "fb_info": self.fb_info,
            "university": self.university,
            "faculty": self.faculty,
            "department": self.department,
            "speciality": self.speciality,
            "year": self.year,
            "group": self.group,
            "type": self.type,
            "score": self.score
        }

    def __str__(self):
        return f"<User name={self.name} type={type}>"

    def __repr__(self):
        return self.__str__()


# Quick utilities

def get_user_by_id(id):
    return User(**database.get_user_by_id(id))

def get_user_fields():
    return [ field.capitalize() for field in database.USER_FIELDS ]

def get_number_of_users():
    return database.get_number_of_users()

def get_all_users(formalize=True):
    return database.get_all_users(formalize=formalize)

def set_admin(user_id):
    return database.edit_user(user_id, type="admin")

def set_moderator(user_id):
    return database.edit_user(user_id, type="moderator")