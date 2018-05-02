import pypyodbc


connection = pypyodbc.connect('Driver={SQL Server};Server=DESKTOP-5G79BTM;Database=projekt')

def food():
	food_choices = []
	cursor = connection.cursor()
	cursor.execute("SELECT id, name FROM wyzyw")
	for row in cursor:
		food_choices.append((int(row[0]),row[1]))
	return food_choices

def attractions_all():
	atraction_all = []
	cursor = connection.cursor()
	cursor.execute("SELECT id, name FROM atrakcje")
	for row in cursor:
		atraction_all.append((int(row[0]),row[1]))
	return atraction_all

def flight():
	flights = []
	cursor = connection.cursor()
	cursor.execute("SELECT l.id, l.name FROM lotniska l, panstwa p, miasta m WHERE l.id_miasta=m.id AND m.id_panstwa=p.id AND p.name='Polska'")
	for row in cursor:
		flights.append((int(row[0]),row[1]))
		return flights

def country():
	countries = []
	cursor = connection.cursor()
	cursor.execute("SELECT id, name FROM panstwa")
	for row in cursor:
		countries.append((int(row[0]), row[1]))
	return countries

def city():
	cities = []
	cursor = connection.cursor()
	cursor.execute("SELECT id, name FROM miasta")
	for row in cursor:
		cities.append((int(row[0]), row[1]))
	return cities

def air():
	airs = []
	cursor = connection.cursor()
	cursor.execute("SELECT id, name FROM lotniska")
	for row in cursor:
		airs.append((int(row[0]),row[1]))
	return airs

def hotel():
	hotels = []
	cursor = connection.cursor()
	cursor.execute("SELECT id, name FROM hotele")
	for row in cursor:
		hotels.append((int(row[0]),row[1]))
		return hotels