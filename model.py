from flask_login import UserMixin, AnonymousUserMixin, login_manager

class User(UserMixin):

	def __init__(self,email,password, name=None,surname=None,role_id=0,street=None,number=None,city=None,postcode=None, id=None):
		self.id = id
		self.name = name
		self.surname = surname
		self.email = email
		self.password = password
		self.role_id = role_id
		self.street = street
		self.number = number
		self.city = city
		self.postcode = postcode

	def is_administrator(self):
		return (self.role_id is not None and self.role_id==1)

# Klasa użytkownika anonimowego, nie ma żadnych uprawnień
class AnonymousUser(AnonymousUserMixin):

	def is_administrator(self, *args):
		return False