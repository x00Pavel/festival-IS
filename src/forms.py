from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, ValidationError
from wtforms.validators import DataRequired, Length, Email, EqualTo
from wtforms.fields import *
from flask import request


class RegistrationForm(FlaskForm):
    username = StringField(
        "Username", validators=[DataRequired(), Length(min=2, max=20)]
    )
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField(
        "Password", validators=[DataRequired(), Length(min=2, max=20)]
    )
    passwordC = PasswordField(
        "Password Confirmation",
        validators=[DataRequired(), Length(min=2, max=20), EqualTo("password")],
    )

    submit = SubmitField("Sign up")
    firstname = StringField("First name", validators=[DataRequired(), Length(max=50)])
    lastname = StringField("Last name", validators=[DataRequired(), Length(max=50)])
    city = StringField("City", validators=[Length(max=80)])
    street = StringField("Street", validators=[Length(max=80)])
    streeta = StringField("Street (additional)", validators=[Length(max=80)])
    homenum = StringField("Home/Flat number", validators=[Length(max=80)])
    phonenumber = StringField("Phone number", validators=[DataRequired()])


class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField(
        "Password", validators=[DataRequired(), Length(min=2, max=20)]
    )
    remember = BooleanField("Remember me")
    submit = SubmitField("Log in up")


class TicketForm(FlaskForm):
    submit = SubmitField("Reserve")
    user_name = StringField("Name", validators=[DataRequired()])
    user_surname = StringField("Surname", validators=[DataRequired()])
    user_email = StringField("Email", validators=[DataRequired()])


class BandForm(FlaskForm):
    band_name = StringField("Name", validators=[DataRequired()])
    band_scores = IntegerField("Scores", validators=[DataRequired()])
    band_genre = StringField("Genre", validators=[DataRequired()])
    band_tags = StringField("Tags", validators=[DataRequired()])
    band_logo = HiddenField("LOGO")
    
class FestivalForm(FlaskForm):
    fest_name = StringField("Name", validators=[DataRequired()])
    fest_tags = StringField("Tags", default="Change ME!!!!!")
    fest_description=StringField("Description", default="No description")
    fest_style=StringField("Style", validators=[DataRequired()])
    fest_cost = IntegerField("Cost", validators=[DataRequired()])
    fest_time_from = DateTimeField("From", validators=[DataRequired()], format='%d-%m-%Y %H:%M')
    fest_time_to = DateTimeField("To", validators=[DataRequired()], format='%d-%m-%Y %H:%M')
    fest_address = StringField("Address", validators=[DataRequired()])
    fest_max_capacity = IntegerField("Max capacity", validators=[DataRequired()])
    fest_age_restriction = IntegerField("Age restriction", default=16)
    fest_sale = IntegerField("Sale", default=0)
    fest_org_id = HiddenField(validators=[DataRequired()])
    fest_status = IntegerField("Status", default=0)
    fest_logo = HiddenField("LOGO")


class RoleForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired()])
    name = StringField("Name", validators=[DataRequired()])
    surname = StringField("Surname", validators=[DataRequired()])
    address = StringField("Address", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Add role")
