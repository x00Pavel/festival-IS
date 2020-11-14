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
        "Password", validators=[DataRequired(), Length(min=6)]
    )
    passwordC = PasswordField(
        "Password Confirmation",
        validators=[DataRequired(), Length(min=6), EqualTo("password")],
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
        "Password", validators=[DataRequired(), Length(min=6)]
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
    band_tags = StringField("Tags")
    band_logo = HiddenField("LOGO")


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
