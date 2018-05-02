from flask import abort
from flask_login import current_user
from functools import wraps
from flask import flash,redirect,url_for


def admin_required(f):
	@wraps(f)
	def decorated_function(*args,**kwargs):
		if not current_user.is_administrator():
			flash('Nie masz wystarczających uprawnień!')
			return redirect(url_for('index'))
		return f(*args,**kwargs)
	return decorated_function