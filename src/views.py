from flask import render_template, request, redirect, flash, url_for
from create_db import Festival, db
from festival_is import app
from forms import *


@app.route("/", methods=["GET", "POST"])
def home():

    data = Festival.query.all()
    listofdicts = []
    for row in data:
        res = {}
        for column in row.__table__.columns:
            res[column.name] = str(getattr(row, column.name))
        listofdicts.append(res)
    return render_template("home.html", posts=listofdicts)


@app.route("/about")
def about():
    return render_template("about.html", title="About")


@app.route("/festivals")
def festivals():
    return render_template("festivals.html", title="Festivals")


@app.route("/register", methods=["GET", "POST"])
def register():
    option = request.form.getlist("options")
    form = RegistrationForm()
    if form.validate_on_submit():
        flash(f"Account created for {form.username.data}!", "success")
        return redirect(url_for("home"))
    return render_template("register.html", title="Registration", form=form)


@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        if form.email.data == "admin@blog.com" and form.password.data == "1111":
            flash("You have been logged in!", "success")
            return redirect(url_for("home"))
        else:
            flash("Log in failed! Check email and password", "danger")
    return render_template("login.html", title="Login", form=form)
