from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo
from wtforms.fields import *
from wtforms import ValidationError
import re
import phonenumbers
from flask import request


# class AcountForm(FlaskForm):
#    email = StringField("Email", validators=[DataRequired(), Email()])
#    firstname = StringField("First name", validators=[DataRequired(), Length(max=50)])
#    lastname = StringField("Last name", validators=[DataRequired(), Length(max=50)])
#    Password = PasswordField(
#        "Password", validators=[DataRequired(), Length(min=2, max=20)]
#    )
#    Password2 = PasswordField(
#        "Password Confirmation",
#        validators=[DataRequired(), Length(min=2, max=20), EqualTo("Password")],
#    )
#    submit = SubmitField("Update profile")


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

    if not re.search(r"^[0-9]+:[0-9]+$", str(password)):
        # raise ValidationError("Invalid phone number.")
        print("BLYAT, RAUL!")

    # phone = StringField("Phone", validators=[DataRequired()])

    phonenumber = StringField("Phone number")

    def validate_phone(self, form, field):
        if len(field.data) > 16:
            raise ValidationError("Invalid phone number.")
        try:
            input_number = phonenumbers.parse(field.data)
            if not (phonenumbers.is_valid_number(input_number)):
                raise ValidationError("Invalid phone number.")
        except:
            input_number = phonenumbers.parse("+1" + field.data)
            if not (phonenumbers.is_valid_number(input_number)):
                raise ValidationError("Invalid phone number.")


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
    band_logo = StringField("Logo", default="No logo")
    band_scores = IntegerField("Scores", validators=[DataRequired()])
    band_genre = StringField("Genre", validators=[DataRequired()]) # TODO: issue #47
    band_tags = StringField("Tags", validators=[DataRequired()]) # TODO: issue #47