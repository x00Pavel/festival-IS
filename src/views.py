from flask import render_template, request, redirect, flash, url_for
from create_db import *
from festival_is import app, login_manager
from forms import *
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_required, logout_user, current_user, login_user
import json, boto3
import os
import urllib.parse

ROLES = {
    4: ("User", User),
    3: ("Seller", Seller),
    2: ("Organizer", Organizer),
    1: ("Admin", Admin),
    0: ("RootAdmin", RootAdmin),
}


@login_manager.user_loader
def user_loader(user_id):
    """Given *user_id*, return the associated User object.
    :param unicode user_id: user_id (email) user to retrieve
    """
    return User.query.get(user_id)


# @login_manager.request_loader
# def request_loader(request):
#     email = request.form.get("email")
#     user = User.query.get(email)

#     # DO NOT ever store passwords in plaintext and always compare password
#     # hashes using constant-time comparison!
#     user.is_authenticated = user.check_passwd(request.form.get("password"))
#     return user


@app.route("/", methods=["GET", "POST"])
def home():
    data = Festival.query.all()
    list_of_dicts = []
    for row in data:
        res = {}
        for column in row.__table__.columns:
            res[column.name] = str(getattr(row, column.name))
        list_of_dicts.append(res)
    if current_user.is_authenticated:
        user_image = (
            User.query.with_entities(User.avatar)
            .filter_by(user_email=current_user.user_email)
            .first()
        )
        return render_template(
            "festivals.html", user_image=user_image, posts=list_of_dicts
        )
    print(data, flush=True)
    return render_template("festivals.html", posts=list_of_dicts)


@app.route("/about")
def about():
    return render_template("about.html", title="About")


@app.route("/user")
def user():
    return render_template("festivals.html", title="User")


@app.route("/organizer")
def organizer():
    return render_template("festivals.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        role, table = ROLES[int(request.form["options"])]
        print(role, table)
        email = form.email.data
        existing_user = User.find_by_email(email)
        if existing_user is None:
            name = form.firstname.data
            surname = form.lastname.data
            passwd_hash = generate_password_hash(form.password.data)
            address = f"{form.city.data}, {form.street.data} ({form.streeta.data if form.streeta is not None else 'No additional street' }), {form.homenum.data}"
            new_user = table(email, name, surname, role, passwd_hash, address, None)
            db.session.add(new_user)
            db.session.commit()
            flash(f"Account created for {form.username.data}!", "success")
            return login(user=new_user)
        else:
            flash(f"Email {email} is alredy registered!", "danger")
            return render_template("register.html", title="Registration", form=form)
    return render_template("register.html", title="Registration", form=form)


@app.route("/login", methods=["GET", "POST"])
def login(user=None):
    form = LoginForm()
    if form.validate_on_submit():
        user = User.find_by_email(form.email.data)
        if user is not None:

            remember = True if request.form.get("remember") else False
            if user.check_passwd(form.password.data):
                user.is_authenticated = True
                if login_user(user, remember=remember):
                    user.is_active = True
                flash("You have been logged in!", "success")
                return redirect(url_for("protected"))
                # return redirect(url_for('home'))
            else:
                flash("Log in failed! Check email and password", "danger")
        else:
            flash("Account for this email doesn't exist", "warning")

    return render_template("login.html", title="Login", form=form)


# Listen for GET requests to yourdomain.com/account/
@app.route("/account")
@login_required
def account():
    # Show the account-edit HTML page:
    user = User.query.filter_by(user_email=current_user.user_email).first()
    user_columns = {}
    for column in user.__table__.columns:
        if column.name not in ["passwd", "perms"]:
            user_columns[column.name] = str(getattr(user, column.name))
    return render_template("account.html", user_columns=user_columns)


# Listen for POST requests to yourdomain.com/submit_form/
@app.route("/submit-form/", methods=["POST"])
@login_required
def submit_form():

    new_psswd1 = request.form["new_psswd1"]
    new_psswd2 = request.form["new_psswd2"]

    print(request.form["avatar_url"], flush = True)
    #setattr(current_user, 'user_email', request.form["user_email"]) TODO: solve problem with foreign keys need to talk with xyadlo00
    setattr(current_user, 'name', request.form["name"])
    setattr(current_user, 'surname', request.form["surname"])
    setattr(current_user, 'address', request.form["address"])
    setattr(current_user, 'avatar', request.form["avatar_url"])

    #if new_psswd1 == new_psswd2:
    #   TODO: solve psswd change - xaghay00 mb add validation into the form? 
    db.session.commit()

    # Redirect to the user's profile page, if appropriate
    return redirect("/account")


# Listen for GET requests to yourdomain.com/sign_s3/
@app.route("/sign-s3/")
@login_required
def sign_s3():
    # Load necessary information into the application
    S3_BUCKET = os.environ.get("S3_BUCKET")

    # Load required data from the request
    file_name = request.args.get("file-name")
    file_type = request.args.get("file-type")

    # Initialise the S3 client
    s3 = boto3.client("s3")

    # Generate and return the presigned URL
    presigned_post = s3.generate_presigned_post(
        Bucket=S3_BUCKET,
        Key=file_name,
        Fields={"acl": "public-read", "Content-Type": file_type},
        Conditions=[{"acl": "public-read"}, {"Content-Type": file_type}],
        ExpiresIn=3600,
    )

    # Return the data to the client
    return json.dumps(
        {
            "data": presigned_post,
            "url": f"https://{S3_BUCKET}.s3.amazonaws.com/{file_name}",
        }
    )


@app.route("/protected")
@login_required
def protected():
    return redirect("/")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect("/")
