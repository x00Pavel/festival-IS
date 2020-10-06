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
        role, table = ROLES[int(request.form["options"])]
        email = form.email.data
        existing_user = User.find_by_email(email)
        if existing_user is None:
            name = form.firstname.data
            surname = form.lastname.data
            passwd_hash = generate_password_hash(form.password.data, method="sha256")
            address = f"{form.city.data}, {form.street.data} ({form.streeta.data if form.streeta is not None else 'No additional street' }), {form.homenum.data}"
            new_user = table(email, name, surname, role, passwd_hash, address, None)
            db.session.add(new_user)
            db.session.commit()
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
@app.route("/account/")
@login_required
def account():
    # Show the account-edit HTML page:
    user = User.query.filter_by(user_id=current_user.user_id).first()
    print(f"Type of -------------------> {type(user)}")
    return render_template("account.html", user_columns=user)


# Listen for POST requests to yourdomain.com/submit_form/
@login_required
@app.route("/submit-form/", methods=["POST"])
def submit_form():

    new_psswd1 = request.form["new_psswd1"]
    new_psswd2 = request.form["new_psswd2"]

    print(request.form["avatar_url"], flush=True)
    # setattr(current_user, 'user_email', request.form["user_email"]) TODO: solve problem with foreign keys need to talk with xyadlo00
    setattr(current_user, "name", request.form["name"])
    setattr(current_user, "surname", request.form["surname"])
    setattr(current_user, "address", request.form["address"])
    setattr(current_user, "avatar", request.form["avatar_url"])

    # if new_psswd1 == new_psswd2:
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


@app.route("/festival/<fest_id>")
def festival_page(fest_id):
    fest = Festival.query.filter_by(fest_id=fest_id).first()
    return render_template("festival_page.html", fest=fest)


@app.route("/festival/<fest_id>/ticket", methods=["GET", "POST"])
def ticket(fest_id):
    fest = Festival.query.filter_by(fest_id=fest_id).first()
    form = (
        TicketForm()
        if current_user.is_anonymous
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
            current_user.reserve_ticket(fest_id)
        except ValueError as e:
            flash(e, type="error")

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
@app.route("/my_tickets")
def my_tickets():
    tickets = current_user.get_tickets()
    return render_template("ticket_page.html", tickets=tickets)


@login_required
@app.route("/manage_tickets")
def manage_tickets():
    pass


@login_required
@app.route("/manage_sellers")
def manage_sellers():
    return "<h2>TODO</h2> function manage_sellers"


@login_required
@app.route("/manage_festivals")
def manage_festivals():
    return "<h2>TODO</h2> function manage_festivals"


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
