from flask import Flask, request, url_for, redirect, flash, session, render_template
from config import FACEBOOK_APP_ID, FACEBOOK_APP_SECRET
from flask_dance.contrib.facebook import make_facebook_blueprint, facebook
from models.users.views import user_blueprint
from models.admins.views import admin_blueprint
from common.database import Database
from common.utils import login_required, admin_required

import os
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
    json = facebook.get("/me").json()
    user_id = json['id']
    name = json['name']
    return f"Hello {user_id}|{name} !"



@app.route("/admin")
@admin_required
def admin():
    return render_template("admin/index.html")



app.run(port=3001, debug=True)