from flask import render_template, request, redirect, flash, url_for
from classes import *
from festival_is import app, login_manager
from forms import *
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_required, logout_user, current_user, login_user
import json, boto3
import os
import urllib.parse
import itertools
from werkzeug.datastructures import MultiDict


# @app.errorhandler(500)
# def undef_error(e):
#     flash("Undefined error is raised on client side. Please, contact admin.", "warning")
#     flash(f"Debug {e}.", "warning")
#     return redirect("/")


# @app.errorhandler(404)
# def undef_error(e):
#     flash("Error 404 raised", "warning")
#     flash(f"Debug {e}.", "warning")
#     return redirect("/")


# @app.errorhandler(Exception)
# def undef_error(e):
#     flash("Exception is raised", "warning")
#     flash(f"Debug {e}.", "warning")
#     return redirect("/")


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
    recommendations = None
    if current_user.is_authenticated:
        recommendations = list(current_user.get_recomendations())
        recommendations_count = len(recommendations)
        return render_template(
            "festivals.html",
            user_columns=current_user,
            fests=list_of_dicts,
            recommendations=recommendations,
            recommendations_count=recommendations_count,
        )
    return render_template("festivals.html", fests=list_of_dicts)


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
        email = form.email.data
        existing_user = User.find_by_email(email)
        if existing_user is None:
            new_user, msg, status = BaseUser.register(form, perms)
            print(msg, status)
            flash(msg, status)
            if new_user:
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
            if not user.active:
                flash("Your user is removed by admin", "warning")
                return redirect("/")
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
@app.route("/account/", methods=["GET"])
def account():
    user = User.query.filter_by(user_id=current_user.user_id).first()
    return render_template("account.html", user_columns=user)


# Listen for POST requests to yourdomain.com/submit_form/
@login_required
@app.route("/submit-form/", methods=["POST"])
def submit_form():
    msg, status = current_user.change_account(request.form)
    print(msg, status)
    flash(msg, status)
    return redirect("/account")


# Listen for GET requests to yourdomain.com/sign_s3/
@app.route("/sign-s3/<folder>/<_id>/")
@login_required
def sign_s3(folder, _id):
    # Load necessary information into the application
    S3_BUCKET = os.environ.get("S3_BUCKET")

    # Load required data from the request
    folder_name = f"{folder}/{_id}"
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


@app.route("/festival/<fest_id>", methods=["GET", "POST"])
def festival_page(fest_id):
    fest = Festival.get_festival(fest_id)
    anonim = current_user.is_anonymous
    perfs = Performance.query.filter_by(fest_id=fest_id).all()
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
            flash(f"{e}", "warning")
            return redirect("/")
        flash("Ticket is successfully reserved", "success")
        return redirect("/")
    return render_template(
        "festival_page.html",
        fest=fest,
        user_columns=current_user,
        form=form,
        anonym=current_user.is_anonymous,
        perfs=perfs,
    )


@login_required
@app.route("/my_tickets", methods=["GET", "POST"])
def my_tickets():
    tickets = current_user.get_tickets()
    if not tickets:
        return redirect("/")
    return render_template(
        "ticket_page.html",
        actual_tickets=tickets[0],
        outdated_tickets=tickets[1],
        user_columns=current_user,
    )


@login_required
@app.route("/my_tickets/<ticket_id>/cancel")
def cancel_ticket(ticket_id):
    current_user.cancel_ticket(ticket_id)
    return redirect("/my_tickets")


@login_required
@app.route("/my_festivals")
def my_festivals():
    planed_fests, outdated_fests = current_user.get_festivals()
    return render_template(
        "my_festivals.html",
        actual_fests=planed_fests,
        outdated_fests=outdated_fests,
        user_columns=current_user,
        source="/my_festivals",
    )
@login_required
@app.route("/<source>/<fest_id>/update_fest", methods=["POST"])
def update_fest(fest_id, source):
    msg, status = current_user.update_fest(request.form, fest_id)
    flash(msg, status)
    return redirect(f"/my_festivals/{fest_id}/edit")


@login_required
@app.route("/<source>/<fest_id>/edit", methods=["GET"])
def edit_festival(fest_id, source):
    seller_form = RoleForm()

    fest = Festival.query.filter_by(fest_id=fest_id).first()

    perfs = current_user.get_perf(fest_id=fest_id)
    sellers = current_user.get_sellers(fest_id)
    return render_template(
        "edit_festival.html",
        fest=fest,
        seller_form=seller_form,
        perfs=perfs,
        user_columns=current_user,
        sellers=sellers,
        org=None,
    )


@login_required
@app.route("/my_festivals/add", methods=["GET", "POST"])
def add_festival():
    seller_form = RoleForm()
    if request.method == "POST":
        form = request.form
        fest = current_user.add_fest(form)
        
        if request.form["fest_logo"] == "https://festival-static.s3-eu-west-1.amazonaws.com/def_fest_logo.png":
            pass
        else:
            print(request.form["fest_logo"], flush=True)
            S3_BUCKET = os.environ.get("S3_BUCKET")

            s3 = boto3.resource("s3")
            copy_source = {
                "Bucket": S3_BUCKET,
                "Key": form["fest_logo"].split(".com/")[-1],
            }
            bucket = s3.Bucket(S3_BUCKET)
            bucket.copy(copy_source, f"fest/{fest.fest_id}/{form['fest_name']}.png")
        
            fest.fest_logo = f'{form["fest_logo"].split(".com/")[0]}.com/fest/{fest.fest_id}/{form["fest_name"]}.png'
            
        db.session.commit()
        return redirect(f"/my_festivals/{fest.fest_id}/edit")
    return render_template(
        "edit_festival.html",
        fest=None,
        seller_form=seller_form,
        org=current_user,
        perfs=None,
        sellers=None,
        user_columns=current_user,
    )

    return redirect("/manage_bands")


@login_required
@app.route("/<source>/<fest_id>/cancel_festival")
def cancel_fest(fest_id, source):
    msg, status = current_user.cancel_fest(fest_id)
    flash(msg, status)
    return redirect(f"/{source}")


@login_required
@app.route("/<source>/<fest_id>/add_perf", methods=["POST"])
def fest_add_perf(fest_id, source):
    form = request.form
    msg, status = current_user.fest_add_perf(form, fest_id)
    flash(msg, status)
    return redirect(f"/my_festivals/{fest_id}/edit")


@login_required
@app.route("/<source>/<fest_id>/del_perf/<perf_id>")
def fest_del_perf(fest_id, perf_id, source):
    current_user.fest_del_perf(perf_id)
    flash(f"Performance {perf_id} canceled", "success")
    return redirect(f"/my_festivals/{fest_id}/edit")


@login_required
@app.route("/<source>/<fest_id>/add_seller", methods=["POST"])
def fest_add_seller(fest_id, source):
    form = request.form
    msg, status = current_user.fest_add_seller(form, fest_id)
    flash(msg, status)
    return redirect(f"/my_festivals/{fest_id}/edit")


@login_required
@app.route("/<source>/<fest_id>/del_seller/<seller_id>")
def fest_del_seller(fest_id, seller_id, source):
    current_user.fest_del_seller(fest_id, seller_id)
    flash(f"Seller {seller_id} removed from festival {fest_id}", "success")
    return redirect(f"/my_festivals/{fest_id}/edit")


@login_required
@app.route("/<source>/<fest_id>/create_seller", methods=["POST"])
def create_seller(fest_id, source):
    form = request.form
    msg, status = current_user.create_seller(form, fest_id)
    flash(msg, status)
    return redirect(f"/my_festivals/{fest_id}/edit")


@login_required
@app.route("/<source>/<fest_id>/manage_tickets")
def manage_tickets(fest_id, source):
    tickets, fest, actuality = current_user.get_sellers_tickets(fest_id)
    return render_template(
        "manage_tickets.html",
        tickets=tickets,
        user_columns=current_user,
        actuality=actuality,
        fest=fest,
    )


@login_required
@app.route(
    "/<source>/<fest_id>/manage_tickets/<ticket_id>/<action>",
    methods=["GET", "POST"],
)
def manage_ticket_seller(fest_id, ticket_id, action, source):
    reason = request.form["reason"]
    current_user.manage_ticket_seller(ticket_id, action, reason)
    return redirect(f"/{source}/{fest_id}/manage_tickets")


@login_required
@app.route("/manage_sellers")
def manage_sellers():
    form = RegistrationForm()
    if form.validate_on_submit():
        existing_user = User.find_by_email(form.email.data)
        if existing_user is None:
            current_user.add_seller(form)
            flash(f"Seller {form.username.data} successfully added!", "success")
        else:
            flash(f"Email {email} is already registered!", "danger")

    return render_template(
        "sellers_page.html", sellers=current_user.get_sellers(), form=form
    )


@login_required
@app.route("/manage_festivals")
def manage_festivals():
    planed_fests, outdated_fests = current_user.manage_festivals()
    return render_template(
        "my_festivals.html",
        actual_fests=planed_fests,
        outdated_fests=outdated_fests,
        user_columns=current_user,
        source="/manage_festivals",
    )


@login_required
@app.route("/manage_users")
def manage_users():
    users = current_user.get_all_users()
    admin_form = RoleForm()
    return render_template(
        "users_page.html", users=users, admin_form=admin_form, user_columns=current_user
    )


@login_required
@app.route("/manage_users/add_admin", methods=["POST"])
def add_admin():
    response, status = current_user.add_admin(request.form)
    flash(response, status)
    return redirect("/manage_users")


@login_required
@app.route("/manage_users/<user_id>/remove_role")
def remove_role(user_id):
    msg, status = current_user.remove_role(user_id)
    flash(msg, status)
    return redirect("/manage_users")


@login_required
@app.route("/manage_users/<user_id>/remove_user")
def remove_user(user_id):
    response, status = current_user.remove_user(user_id)
    flash(response, status)
    return redirect("/manage_users")


@login_required
@app.route("/manage_bands", methods=["GET", "POST"])
def manage_bands():
    form = BandForm()
    if form.validate_on_submit():
        current_user.add_band(form)
    bands = current_user.get_bands()
    return render_template(
        "bands_page.html", bands=bands, form=form, user_columns=current_user
    )


@login_required
@app.route("/manage_bands/add", methods=["POST"])
def add_band():
    form = BandForm()
    band = current_user.add_band(form)

    if request.form["fest_logo"] == "https://festival-static.s3-eu-west-1.amazonaws.com/defaut_band_logo.png":
        pass
    else:
        S3_BUCKET = os.environ.get("S3_BUCKET")

        s3 = boto3.resource("s3")
        copy_source = {
            "Bucket": S3_BUCKET,
            "Key": request.form["band-logo"].split(".com/")[-1],
        }
        bucket = s3.Bucket(S3_BUCKET)
        bucket.copy(copy_source, f"band/{band.band_id}/{form.band_name.data}.png")

        band.logo = f'{request.form["band-logo"].split(".com/")[0]}.com/band/{band.band_id}/{form.band_name.data}.png'
    db.session.commit()

    return redirect("/manage_bands")


@login_required
@app.route("/manage_bands/<band_id>/delete")
def delete_band(band_id):
    current_user.delete_band(band_id)
    return redirect("/manage_bands")


@login_required
@app.route("/manage_stages")
def manage_stages():
    stages = current_user.get_all_stages()
    return render_template("stages_page.html", stages=stages)


@login_required
@app.route("/manage_stages/add_stage", methods=["POST"])
def add_stage():
    form = request.form
    msg, status = current_user.add_stage(form)
    return redirect("/manage_stages")
