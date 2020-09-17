from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo
from wtforms.fields import *
from wtforms import ValidationError
import phonenumbers
from flask import request
class RegistrationForm(FlaskForm):
	username = StringField('Username', 
							validators=[DataRequired(), Length(min=2,max=20)])
	email = StringField('Email', validators=[DataRequired(), Email()])
	password = PasswordField('Password', validators=[DataRequired(), Length(min=2,max=20)])
	passwordC = PasswordField('Password Confirmation',
				validators=[DataRequired(), Length(min=2,max=20), EqualTo('password')])

	submit = SubmitField('Sign up')
	firstname = StringField('First name', validators=[DataRequired(), Length(max=50)])
	lastname= StringField('Last name', validators=[DataRequired(), Length(max=50)])
	city= StringField('City', validators=[Length(max=80)])
	street= StringField('Street', validators=[Length(max=80)])
	streeta= StringField('Street (additional)', validators=[Length(max=80)])
	homenum = StringField('Home/Flat number', validators=[Length(max=80)])


	phone = StringField('Phone', validators=[DataRequired()])
	phonenumber = IntegerField('Phone number')
	def validate_phonenumber(self,phonenumbers):
		try:
			p = phonenumbers.parse(phone.data)
			if not phonenumbers.is_valid_number(p):
				raise ValueError()
		except(phonenumbers.phonenumberutil.NumberParseException, ValueError):
			raise ValidationError('Invalid phone number')


		

class LoginForm(FlaskForm):
	email = StringField('Email', validators=[DataRequired(), Email()])
	password = PasswordField('Password', validators=[DataRequired(), Length(min=2,max=20)])
	remember = BooleanField('Remember me')
	submit = SubmitField('Log in up')