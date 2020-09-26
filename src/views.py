from flask import render_template, request, redirect, flash, url_for
from create_db import Festival, db, User
from festival_is import app, login_manager
from forms import *
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_required, logout_user, current_user, login_user


@login_manager.user_loader
def user_loader(user_id):
    """Given *user_id*, return the associated User object.

    :param unicode user_id: user_id (email) user to retrieve

    """
    return User.query.get(user_id)


@app.route("/", methods=["GET", "POST"])
def home():

    data = Festival.query.all()
    list_of_dicts = []
    for row in data:
        res = {}
        for column in row.__table__.columns:
            res[column.name] = str(getattr(row, column.name))
        list_of_dicts.append(res)
    return render_template("festivals.html", posts=list_of_dicts)


@app.route("/about")
def about():
    return render_template("about.html", title="About")


# @app.route("/festivals")
# def festivals():
#     return render_template("festivals.html", title="Festivals")


@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        existing_user = User.find_by_email(form.email.data)
        if existing_user is None:
            permissions = int(request.form["options"])
            email = form.email.data
            name = form.firstname.data
            surname = form.lastname.data
            passwd_hash = generate_password_hash(form.password.data)
            address = f"{form.city.data}, {form.street.data} ({form.streeta.data if form.streeta is not None else 'No additional street' }), {form.homenum.data}"
            new_user = User(
                email, name, surname, permissions, passwd_hash, address, None
            )
            db.session.add(new_user)
            db.session.commit()

            flash(f"Account created for {form.username.data}!", "success")
            return redirect(url_for("home"))
        flash("A user already exists with that email address.")
    return render_template("register.html", title="Registration", form=form)


@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.find_by_email(form.email.data)
        if user.check_passwd(form.password.data):
            login_user(user)  # TODO: add @login_manager.user_loader to
            next_page = request.args.get("next")  # Get next page after login
            flash("You have been logged in!", "success")
            return redirect(next_page or url_for("home"))
        else:
            flash("Log in failed! Check email and password", "danger")
    return render_template("login.html", title="Login", form=form)
