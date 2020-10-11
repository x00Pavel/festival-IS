from flask import render_template, request, redirect, flash, url_for
from create_db import *
from festival_is import app, login_manager
from forms import *
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_required, logout_user, current_user, login_user
import json, boto3
import os
import urllib.parse
from werkzeug.datastructures import MultiDict


@login_manager.user_loader
def user_loader(user_id):
    """Given *user_id*, return the associated User object.
    :param unicode user_id: user_id (email) user to retrieve
    """
    return User.query.get(user_id)


@app.route("/", methods=["GET", "POST"])
def home():
    data = Festival.query.all()
    list_of_dicts = [row for row in data]

    if current_user.is_authenticated:
        return render_template(
            "festivals.html", user_columns=current_user, posts=list_of_dicts
        )
    return render_template("festivals.html", posts=list_of_dicts)


@app.route("/about")
def about():
    if current_user.is_authenticated:
        return render_template("about.html", user_columns=current_user, title="About")
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
        perms = int(request.form["options"])
        _, role = ROLES[perms]
        email = form.email.data
        existing_user = User.find_by_email(email)
        if existing_user is None:
            new_user = User.register(form, perms)
            flash(f"Account created for {form.username.data}!", "success")
            return login(user=new_user)
        else:
            flash(f"Email {email} is already registered!", "danger")
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
@login_required
@app.route("/account/", methods=["GET", "POST"])
def account():
    user = User.query.filter_by(user_id=current_user.user_id).first()
    return render_template("account.html", user_columns=user)


# Listen for POST requests to yourdomain.com/submit_form/
@login_required
@app.route("/submit-form/", methods=["GET", "POST"])
def submit_form():

    new_psswd1 = request.form["new_psswd1"]
    new_psswd2 = request.form["new_psswd2"]
    new_user_email = request.form["user_email"]

    users_email = (
        db.session.query(User.user_email)
        .filter(current_user.user_email != User.user_email)
        .all()
    )

    for i in users_email:
        if i[0] == new_user_email:
            flash("Email already exists", "warning")
            return redirect("/account")

    setattr(current_user, "user_email", request.form["user_email"])
    setattr(current_user, "name", request.form["name"])
    setattr(current_user, "surname", request.form["surname"])
    setattr(current_user, "address", request.form["address"])
    setattr(current_user, "avatar", request.form["avatar_url"])

    if new_psswd1 is not None and new_psswd2 is not None:
        if new_psswd1 == new_psswd2:
            current_user.set_password(new_psswd1)
        else:
            flash("Wrong password", "warning")
            return redirect("/account")

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
    folder_name = current_user.user_id
    file_name = request.args.get("file-name")
    file_type = request.args.get("file-type")

    # Initialise the S3 client
    s3 = boto3.client("s3")

    # Generate and return the presigned URL
    presigned_post = s3.generate_presigned_post(
        Bucket=S3_BUCKET,
        Key=f"{folder_name}/{file_name}",
        Fields={"acl": "public-read", "Content-Type": file_type},
        Conditions=[{"acl": "public-read"}, {"Content-Type": file_type}],
        ExpiresIn=3600,
    )

    # Return the data to the client
    return json.dumps(
        {
            "data": presigned_post,
            "url": f"https://{S3_BUCKET}.s3.amazonaws.com/{folder_name}/{file_name}",
        }
    )


@app.route("/protected")
@login_required
def protected():
    return redirect("/")


@login_required
@app.route("/logout")
def logout():
    logout_user()
    return redirect("/")


@app.route("/festival/<fest_id>")
def festival_page(fest_id):
    fest = Festival.get_festival(fest_id)
    return render_template("festival_page.html", fest=fest)


@app.route("/festival/<fest_id>/ticket", methods=["GET", "POST"])
def ticket(fest_id):
    fest = Festival.get_festival(fest_id)
    anonim = current_user.is_anonymous
    form = (
        TicketForm()
        if anonim
        else TicketForm(
            formdata=MultiDict(
                {
                    "user_name": current_user.name,
                    "user_surname": current_user.surname,
                }  # For autofill if user is logged in
            )
        )
    )

    if form.is_submitted():
        try:
            if anonim:
                BaseUser.reserve_ticket(form, fest_id)
            else:
                current_user.reserve_ticket(fest_id)
        except ValueError as e:
            flash(f'{e}', "warning")

        # if current_user.is_anonymous:>?
        flash("Ticket is successfully reserved", category="message")
        return redirect("/")

    return render_template(
        "reserve_ticket.html",
        form=form,
        fest=fest,
        anonym=current_user.is_anonymous,
    )


@login_required
@app.route("/my_tickets", methods=["GET", "POST"])
def my_tickets():
    tickets = current_user.get_tickets()
    return render_template(
        "ticket_page.html",
        actual_tickets=tickets[0],
        outdated_tickets=tickets[1],
    )


@login_required
@app.route("/manage_tickets")
def manage_tickets():
    tickets = current_user.get_tickets()
    return "TODO"


@login_required
@app.route("/manage_sellers", methods=["GET", "POST"])
def manage_sellers():
    form = RegistrationForm()
    if form.validate_on_submit():
        existing_user = User.find_by_email(form.email.data)
        if existing_user is None:
            current_user.add_seller(form)
            flash(f"Seller {form.username.data} successfully added!", "success")
        else:
            flash(f"Email {email} is already registered!", "danger")

    return render_template("sellers_page.html", sellers=current_user.get_sellers(), form=form)


@login_required
@app.route("/manage_sellers/<seller_id>", methods=["GET", "POST"])
def seller_info(seller_id):
    return "<h2>TODO</h2> function seller_info"


@login_required
@app.route("/manage_festivals")
def manage_festivals():
    fests = current_user.get_all_festivals()
    return render_template("manage_festival_page.html", fests=fests)


@login_required
@app.route("/manage_festivals/<fest_id>/del")
def cancel_fest(fest_id):
    current_user.cancel_fest(fest_id)
    return redirect("/manage_festivals")

@login_required
@app.route("/manage_organizers")
def manage_organizers():
    return "<h2>TODO</h2> function manage_organizers"


@login_required
@app.route("/manage_users")
def manage_users():
    return "<h2>TODO</h2> function manage_users"


@login_required
@app.route("/manage_admins")
def manage_admins():
    return "<h2>TODO</h2> function manage_admins"
