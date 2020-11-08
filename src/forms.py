from flask_wtf import FlaskForm
from wtforms import (
    DateTimeField,
    HiddenField,
    IntegerField,
    StringField,
    PasswordField,
    SubmitField,
    BooleanField,
    ValidationError,
)
from wtforms.validators import DataRequired, Length, Email, EqualTo, Regexp, NumberRange
from flask import request


class RegistrationForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField(
        "Password", validators=[DataRequired(), Length(min=2, max=20)]
    )
    passwordC = PasswordField(
        "Password Confirmation",
        validators=[DataRequired(), Length(min=2, max=20), EqualTo("password")],
    )

    submit = SubmitField("Sign up")
    firstname = StringField(
        "First name",
        validators=[
            DataRequired(),
            Regexp(r"^[a-zA-Z]{2,}[a-zA-Z-]*$"),
            Length(max=50),
        ],
    )
    lastname = StringField(
        "Last name",
        validators=[
            DataRequired(),
            Regexp(r"^[a-zA-Z]{2,}[a-zA-Z-]*$"),
            Length(max=50),
        ],
    )
    city = StringField("City", validators=[Length(max=80)])
    street = StringField("Street", validators=[Length(max=80)])
    streeta = StringField("Street (additional)", validators=[Length(max=80)])
    homenum = StringField(
        "Home/Flat number", validators=[Length(max=80), Regexp(r"^\d[\d-]*$")]
    )
    phonenumber = StringField(
        "Phone number", validators=[DataRequired(), Regexp(r"^\+?\d[\d-]{6,}$")]
    )


class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField(
        "Password", validators=[DataRequired(), Length(min=2, max=20)]
    )
    remember = BooleanField("Remember me")
    submit = SubmitField("Log in up")


class TicketForm(FlaskForm):
    submit = SubmitField("Reserve")
    user_name = StringField(
        "Name", validators=[DataRequired(), Regexp(r"^[a-zA-Z]{2,}[a-zA-Z\- ]*$")]
    )
    user_surname = StringField(
        "Surname", validators=[DataRequired(), Regexp(r"^[a-zA-Z]{2,}[a-zA-Z\- ]*$")]
    )
    user_email = StringField("Email", validators=[DataRequired(), Email()])


class BandForm(FlaskForm):
    band_name = StringField(
        "Name", validators=[DataRequired(), Regexp(r"^[a-zA-Z]{2,}[a-zA-Z-]*$")]
    )
    band_scores = IntegerField("Scores", validators=[DataRequired(), Regexp(r"^\d+")])
    band_genre = StringField(
        "Genre", validators=[DataRequired(), Regexp(r"^[a-zA-Z]{2,}[a-zA-Z-]*$")]
    )
    band_tags = StringField("Tags", validators=[DataRequired()])
    band_logo = HiddenField("LOGO")


class FestivalForm(FlaskForm):
    logo = StringField(
        "Logo",
        default="https://festival-static.s3-eu-west-1.amazonaws.com/def_fest_logo.png",
    )
    fest_name = StringField(
        "Name", validators=[DataRequired(), Regexp(r"^[a-zA-Z]{2,}[a-zA-Z\- ]*$")]
    )
    fest_tags = StringField("Tags", default="No tags")
    description = StringField(
        "Description", default="No description", validators=[Regexp(r"^[\d\w\,\. ]*$", message="Invalid format of description")]
    )
    style = StringField("Style", validators=[DataRequired()])
    cost = IntegerField("Cost", validators=[DataRequired(), NumberRange(min=0)])
    time_from = DateTimeField(
        "From", validators=[DataRequired()], format="%d-%m-%Y %H:%M"
    )
    time_to = DateTimeField("To", validators=[DataRequired()], format="%d-%m-%Y %H:%M")
    address = StringField("Address", validators=[DataRequired()])
    max_capacity = IntegerField("Max capacity", validators=[DataRequired()])
    age_restriction = IntegerField(
        "Age restriction", default=16, validators=[NumberRange(min=0)]
    )
    sale = IntegerField("Sale", default=0, validators=[NumberRange(min=0)])
    org_id = HiddenField(validators=[DataRequired()])
    status = IntegerField("Status", default=0)
    current_ticket_count = IntegerField("Ticket count", default=0)
    submit = SubmitField()


class RoleForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    name = StringField(
        "Name", validators=[DataRequired(), Regexp(r"^[a-zA-Z]{2,}[a-zA-Z\- ]*$")]
    )
    surname = StringField(
        "Surname", validators=[DataRequired(), Regexp(r"^[a-zA-Z]{2,}[a-zA-Z\- ]*$")]
    )
    address = StringField("Address", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Add role")
