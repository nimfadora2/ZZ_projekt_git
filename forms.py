from flask_wtf import FlaskForm
from wtforms import TextAreaField, SubmitField, DecimalField, SelectMultipleField, RadioField, PasswordField, StringField, IntegerField, SelectField
from wtforms.fields.html5 import EmailField, DateField
from wtforms.validators import DataRequired, Email, NumberRange, Length, EqualTo, ValidationError, Optional

import pypyodbc

food_choices = []
connection = pypyodbc.connect('Driver={SQL Server};Server=DESKTOP-5G79BTM;Database=projekt')
cursor = connection.cursor()
cursor.execute("SELECT id, name FROM wyzyw")
for row in cursor:
	food_choices.append((int(row[0]),row[1]))

atractions_all = []
cursor.execute("SELECT id, name FROM atrakcje")
for row in cursor:
	atractions_all.append((int(row[0]),row[1]))

flights = []
cursor.execute("SELECT l.id, l.name FROM lotniska l, panstwa p, miasta m WHERE l.id_miasta=m.id AND m.id_panstwa=p.id AND p.name='Polska'")
for row in cursor:
	flights.append((int(row[0]),row[1]))

def country():
	countries = []
	cursor.execute("SELECT id, name FROM panstwa")
	for row in cursor:
		countries.append((int(row[0]), row[1]))
	return countries

def city():
	cities = []
	cursor.execute("SELECT id, name FROM miasta")
	for row in cursor:
		cities.append((int(row[0]), row[1]))
	return cities

airs = []
cursor.execute("SELECT id, name FROM lotniska")
for row in cursor:
	airs.append((int(row[0]),row[1]))

hotels = []
cursor.execute("SELECT id, name FROM hotele")
for row in cursor:
	hotels.append((int(row[0]),row[1]))


class Kontakt(FlaskForm):
	email = EmailField("Twój adres e-mail",validators=[DataRequired(), Email()], render_kw ={'placeholder':"Wpisz swój adres e-mail..."})
	text = TextAreaField("Wiadomość", validators=[DataRequired()], render_kw = {'placeholder': "Uzupełnij..."})
	submit = SubmitField("Wyślij")

class Ogranicz_szukanie(FlaskForm):

	price_lower = DecimalField("Cena minimalna", validators=[Optional()])
	price_upper = DecimalField("Cena maksymalna", validators=[Optional()])
	food        = SelectMultipleField("Wyżywienie", choices=food_choices, coerce=int)
	atractions  = SelectMultipleField("Atrakcje", choices=atractions_all, coerce=int)
	flight_from = SelectMultipleField("Wylot z...", choices=flights, coerce=int)
	date_from   = DateField("Najwcześniejsza data wylotu:",format='%Y-%m-%d', validators=[Optional()])
	date_for = DateField("Najpóźniejsza data powrotu:", format='%Y-%m-%d', validators=[Optional()])
	people       = DecimalField("Ilość osób", validators=[Optional()])
	search = SubmitField("Szukaj")

class Logowanie(FlaskForm):
	email = EmailField("Adres e-mail:", validators=[DataRequired(), Email()])
	password = PasswordField("Hasło:", validators=[DataRequired()])
	submit = SubmitField("Zaloguj się")

class Rejestracja(FlaskForm):

	def validate_email_add(form,field):
		cursor = connection.cursor()
		cursor.execute("SELECT * FROM users WHERE email='%s'" % field.data)
		if len(cursor.fetchall())>0:
			raise ValidationError('Użytkownik o takim adresie e-mail jest już w bazie!')

	email = EmailField("Adres e-mail:", validators=[DataRequired(), Length(5), validate_email_add])
	email_repeat = EmailField("Powtórz adres e-mail:", validators=[DataRequired(), EqualTo('email', 'Adresy e-mail muszą się zgadzać!')])
	password = PasswordField("Wpisz swoje hasło:", validators=[DataRequired(), Length(5)])
	password_repeat = PasswordField("Wpisz hasło ponownie", validators=[DataRequired(), EqualTo('password','Hasła muszą się zgadzać!'), Length(5)])
	submit = SubmitField("Zarejestruj")

class Dane(FlaskForm):
	name = StringField("Imię:", validators=[DataRequired(), Length(5)])
	surname = StringField("Nazwisko:", validators=[DataRequired(), Length(5)])
	street = StringField("Ulica:")#, validators=[DataRequired(), Length(5)])
	number = StringField("Numer domu/mieszkania:")#, validators=[DataRequired()])
	city = StringField("Miasto:")#, validators=[DataRequired()])
	postcode = StringField("Kod pocztowy")#, validators=[DataRequired(), Length(6,6)])
	submit = SubmitField("Zapisz")

class Edycja(FlaskForm):
	submit = SubmitField("Edytuj")

class AddOffer(FlaskForm):
	def validate_dates(form,field):
		if form.date_from.data > form.date_for.data:
			raise ValidationError("Data powrotu musi być póżniejsza niż data wylotu.")
	hotel = SelectField("Hotel:", choices=hotels, coerce=int)
	date_from = DateField("Data wylotu:", format='%Y-%m-%d', validators=[DataRequired(), validate_dates])
	date_for = DateField("Data powrotu:", format='%Y-%m-%d', validators=[DataRequired(), validate_dates])
	flight_from = SelectField("Wylot z:", choices=flights, coerce=int, validators=[DataRequired()])
	flight_to = SelectField("Lot do:", choices=airs, coerce=int, validators=[DataRequired()])
	food = SelectField("Typ wyżywienia:", choices=food_choices, coerce=int, validators=[DataRequired()])
	people = DecimalField("Ilość osób:", validators=[DataRequired()])
	price = DecimalField("Cena za osobę:", validators=[DataRequired()])
	submit = SubmitField("Dodaj")

class AddCountry(FlaskForm):
	def validate_country_name(form,field):
		query = ("SELECT * FROM panstwa WHERE name='%s'" % field.data)
		cursor = connection.cursor()
		cursor.execute(query)
		if len(cursor.fetchall())>0:
			raise ValidationError('Państwo o takiej nazwie jest już w bazie!')
	country_name = StringField("Podaj nazwę państwa:", validators=[DataRequired()])
	submit = SubmitField("Zapisz")

class AddCity(FlaskForm):
	city_name = StringField("Podaj nazwę miasta:", validators=[DataRequired()])
	country_name = SelectField("Wybierz państwo:", choices=country(), coerce=int)
	submit = SubmitField("Zapisz")

class AddFood(FlaskForm):
	def validate_food_name(form,field):
		query = ("SELECT * FROM wyzyw WHERE name='%s'" % field.data)
		cursor = connection.cursor()
		cursor.execute(query)
		if len(cursor.fetchall())>0:
			raise ValidationError('Taka forma wyzywienia jest już w bazie!')
	food_name = StringField("Podaj formę wyżywienia:", validators=[DataRequired()])
	submit = SubmitField("Zapisz")

class AddAttr(FlaskForm):
	def validate_attr_name(form,field):
		query = ("SELECT * FROM atrakcje WHERE name='%s'" % field.data)
		cursor = connection.cursor()
		cursor.execute(query)
		if len(cursor.fetchall())>0:
			raise ValidationError('Taka forma atrakcji jest już w bazie!')
	attr_name = StringField("Podaj nazwę atrakcji:", validators=[DataRequired()])
	submit = SubmitField("Zapisz")

class AddAir(FlaskForm):
	def validate_air_name(form,field):
		query = ("SELECT * FROM lotniska WHERE name='%s'" % field.data)
		cursor = connection.cursor()
		cursor.execute(query)
		if len(cursor.fetchall())>0:
			raise ValidationError('Taka forma atrakcji jest już w bazie!')
	air_name = StringField("Podaj nazwę lotniska:", validators=[DataRequired()])
	city_name = SelectField("Wybierz miasto:", choices=city(), coerce=int)
	submit = SubmitField("Zapisz")

class AddHotel(FlaskForm):
	hotel_name = StringField("Podaj nazwę hotelu:", validators=[DataRequired()])
	city = SelectField("Miasto:", validators=[DataRequired()], choices=city(), coerce=int)
	attr = SelectMultipleField("Atrakcje:", validators=[DataRequired()], choices=atractions_all, coerce=int)
	submit = SubmitField("Zapisz")

class EditCountry(FlaskForm):
	country_name = StringField("Podaj nazwę państwa:", validators=[DataRequired()])
	submit = SubmitField("Zapisz")

class EditCity(FlaskForm):
	city_name = StringField("Podaj nazwę miasta:", validators=[DataRequired()])
	country_name = SelectField("Wybierz państwo:", choices=country(), coerce=int)
	submit = SubmitField("Zapisz")

class EditAir(FlaskForm):
	air_name = StringField("Podaj nazwę lotniska:", validators=[DataRequired()])
	city_name = SelectField("Wybierz miasto:", choices=city(), coerce=int)
	submit = SubmitField("Zapisz")

class EditAttr(FlaskForm):
	attr_name = StringField("Podaj nazwę atrakcji:", validators=[DataRequired()])
	submit = SubmitField("Zapisz")

class EditFood(FlaskForm):
	food_name = StringField("Podaj formę wyżywienia:", validators=[DataRequired()])
	submit = SubmitField("Zapisz")

class EditHotel(FlaskForm):
	hotel_name = StringField("Podaj nazwę hotelu:", validators=[DataRequired()])
	city = SelectField("Miasto:", choices=city(), coerce=int)
	attr = SelectMultipleField("Atrakcje:", validators=[DataRequired()], choices=atractions_all, coerce=int)
	submit = SubmitField("Zapisz")

class EditOffer(FlaskForm):
	def validate_dates(form,field):
		if form.date_from.data > form.date_for.data:
			raise ValidationError("Data powrotu musi być póżniejsza niż data wylotu.")
	hotel = SelectField("Hotel:", choices=hotels, coerce=int)
	date_from = DateField("Data wylotu:", format='%Y-%m-%d', validators=[DataRequired(), validate_dates])
	date_for = DateField("Data powrotu:", format='%Y-%m-%d', validators=[DataRequired(), validate_dates])
	flight_from = SelectField("Wylot z:", choices=flights, coerce=int, validators=[DataRequired()])
	flight_to = SelectField("Lot do:", choices=airs, coerce=int, validators=[DataRequired()])
	food = SelectField("Typ wyżywienia:", choices=food_choices, coerce=int, validators=[DataRequired()])
	people = DecimalField("Ilość osób:", validators=[DataRequired()])
	price = DecimalField("Cena za osobę:", validators=[DataRequired()])
	submit = SubmitField("Dodaj")