from flask import Flask, render_template, flash, redirect, url_for, request, jsonify
from flask_bootstrap import Bootstrap
from forms import Kontakt, Ogranicz_szukanie, Rejestracja, Logowanie, Edycja, Dane, AddOffer, AddCountry, AddCity, AddAttr, AddFood, AddAir, AddHotel, \
    EditCountry, EditCity, EditAir, EditAttr, EditFood, EditHotel, EditOffer
from flask_login import LoginManager, current_user, login_required, logout_user,login_user
from model import User, AnonymousUser
from datetime import datetime
from decorators import admin_required
import pypyodbc
from choices import *

app = Flask(__name__)
print("ssddf")

app.config['SECRET_KEY']='string'
bootstrap = Bootstrap(app)
login_manager = LoginManager(app)
login_manager.session_protection = 'strong'     # zapobiega zmianom sieci
login_manager.login_view = 'login'
login_manager.anonymous_user=AnonymousUser

# Strona główna - done
@app.route("/")
def index():
    return render_template("index.html")

# Kontakt - done
@app.route("/contact", methods=['GET','POST'])
def kontakt():
    form = Kontakt()
    if form.validate_on_submit():
        flash("Wiadomość została wysłana. Odpowiedź powinna nadejść w ciągu 24 h.")
        return redirect(url_for('index'))
    return render_template("kontakt.html", form=form)

# Rezerwacja - not done
@app.route("/reserve")
def rezerwacja():
    return render_template("rezerwacja.html")

# Szukaj - done all
@app.route("/find", methods=['POST','GET'])
def szukaj():
    form = Ogranicz_szukanie()
    cursor = connection.cursor()
    cursor.execute("SELECT o.id, h.name, o.data_od, o.data_do, w.name, o.cena, o.ilosc_miejsc, l.name, l2.name \
                    FROM oferty o, lotniska l, hotele h, wyzyw w, lotniska l2 \
                    WHERE o.id_lotn_tu=l.id AND o.id_lotn_tam = l2.id AND o.id_hotelu=h.id AND o.id_wyzyw=w.id")
    out = []
    for row in cursor:
        tmp = []
        for data in row:
            tmp.append(str(data))
        out.append(tmp)
    if form.validate_on_submit():
        params = []
        query = "SELECT DISTINCT o.id, h.name, o.data_od, o.data_do, w.name, o.cena, o.ilosc_miejsc, l.name, l2.name \
                    FROM oferty o, lotniska l, hotele h, wyzyw w, lotniska l2, atrakcje_hotele ah \
                    WHERE o.id_lotn_tu=l.id AND o.id_lotn_tam = l2.id AND o.id_hotelu=h.id AND o.id_wyzyw=w.id AND ah.id_hotelu=h.id"

        ### Ceny ###
        if form.price_lower.data!=None:
            query=query+" AND o.cena>= %d"
            params.append(form.price_lower.data)
        if form.price_upper.data!=None:
            query=query+" AND o.cena<= %d"
            params.append(form.price_upper.data)

        ### Jedzenie ###
        jedzenie = form.food.data
        if jedzenie !=[]:
            foodies=""
            for i in range(len(jedzenie)):
                if i==0:
                    foodies="(o.id_wyzyw=%d"
                    params.append(jedzenie[i])
                else:
                    foodies=foodies+" OR o.id_wyzyw=%d"
                    params.append(jedzenie[i])
            foodies+=")"
            query=query + " AND "+foodies

        ### Atrakcje ###
        atrakcje = form.atractions.data
        if atrakcje !=[]:
            foodies=""
            for i in range(len(atrakcje)):
                if i==0:
                    foodies="(SELECT id_hotelu FROM atrakcje_hotele WHERE id_atrakcji=%d)"
                    params.append(atrakcje[i])
                else:
                    foodies=" (SELECT ah.id_hotelu FROM atrakcje_hotele ah, " + foodies+ " AS new where ah.id_atrakcji=%d AND ah.id_hotelu=new.id_hotelu)"
                    params.append(atrakcje[i])
            query=query + " AND o.id_hotelu in"+foodies

        ### Wyloty ###
        lotniska = form.flight_from.data
        if lotniska!=[]:
            loty=""
            for i in range(len(lotniska)):
                if i==0:
                    loty="(o.id_lotn_tu=%d"
                    params.append(lotniska[i])
                else:
                    loty=loty+" OR o.id_lotn_tu=%d"
                    params.append(lotniska[i])
            loty+=")"
            query=query + " AND "+loty

        ### Data start ###
        start = form.date_from.data
        if start!=None:
            query=query+" AND o.data_od>= '%s'"
            params.append(str(start))
        ### Data stop ###
        stop = form.date_for.data
        if stop!=None:
            query=query+" AND o.data_do<= '%s'"
            params.append(str(stop))

        ### Ilosc osob ###
        osoby = form.people.data
        if osoby!=None:
            query=query+" AND o.ilosc_miejsc = %d"
            params.append(osoby)
        #print(query % tuple(params))
        cursor = connection.cursor()
        cursor.execute(query % tuple(params))
        out = []
        for row in cursor:
            tmp = []
            for data in row:
                tmp.append(str(data))
            out.append(tmp)
        flash('Filtrowanie włączone')
        return render_template("szukanie.html", rows=out, form=form)
    return render_template("szukanie.html", rows = out, form=form)

# Login - done
@app.route("/login", methods=['POST','GET'])
def login():
    form = Logowanie()
    if form.validate_on_submit():
        cursor = connection.cursor()
        query=("SELECT * FROM users WHERE email='%s'" % form.email.data)
        cursor.execute(query)
        data = cursor.fetchall()
        if len(data)==0:
            flash("Niepoprawne dane logowania. Spróbuj ponownie")
        for row in data:
            user = User(id=row[0], name = row[1],surname =  row[2], email = row[3], password = row[4],role_id =  row[5], street = row[6],number =  row[7], city = row[8],postcode =  row[9])
            if user is not None and row[4]==form.password.data:
                login_user(user)
                flash("Witaj! Teraz możesz korzystać z pełnych funkcjonalności serwisu")
                return redirect(request.args.get('next') or url_for('index'))
            else:
                flash("Niepoprawne dane logowania. Spróbuj ponownie")
    return render_template("login.html", form = form)

# Registration - not done
@app.route("/register", methods=['POST','GET'])
def rejestracja():
    form = Rejestracja()
    if form.validate_on_submit():
        user = User(form.email.data,form.password.data, role_id=2)
        add_user(user)
        flash('Konto zostało utworzone. Zaloguj się!')
        return redirect(url_for('login'))
    return  render_template("rejestracja.html", form=form)

@app.route("/rezerwacja/<int:numer_oferty>")
@login_required
def rezerwuj(numer_oferty):
    return "Blabla"

# Podgląd oferty - done_all
@app.route("/oferta/<int:numer_oferty>")
def oferta(numer_oferty):
    cursor = connection.cursor()
    cursor.execute("SELECT h.name, m.name, p.name, a.name, w.name, o.data_od, o.data_do, l.name, l2.name, o.cena, o.ilosc_miejsc \
                    FROM oferty o, lotniska l, hotele h, wyzyw w, lotniska l2, atrakcje_hotele ah, miasta m, panstwa p, atrakcje a \
                    WHERE h.id = ah.id_hotelu AND h.id=o.id_hotelu AND h.id_miasta = m.id AND m.id_panstwa=p.id and o.id_lotn_tu=l.id \
                    and o.id_lotn_tam = l2.id AND o.id_wyzyw=w.id AND a.id=ah.id_atrakcji AND o.id=%d" % numer_oferty)
    out = cursor.fetchall()
    if len(out) == 0:
        flash("Oferta o takim numerze id nie istnieje")
        return redirect(url_for('szukaj'))
    dane = list(out[0])
    dane[3]=[dane[3]]
    if len(out)>1:
        for i in range(1,len(out)):
            dane[3].append(out[i][3])
    return render_template("oferta.html", dane=dane)

# Profile-  not done - rezervations
@app.route('/profile', methods=['GET','POST'])
@login_required
def profile():
    form = Edycja()
    if form.validate_on_submit():
        return redirect(url_for('profile_edition'))
    return render_template("profil.html", user=current_user, form=form)

# Profile edition - done (?) validators
@app.route('/profile_edit',methods=['GET','POST'])
@login_required
def profile_edition():
    form = Dane()
    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.surname = form.surname.data
        current_user.street = form.street.data
        current_user.postcode = form.postcode.data
        current_user.number = form.number.data
        current_user.city = form.city.data
        update_user(current_user)
        return redirect(url_for('profile'))
    if current_user.name != None and current_user.name != 'None':
        form.name.data =  current_user.name
    if current_user.surname != None and current_user.surname != 'None':
        form.surname.data = current_user.surname
    if current_user.street != None and current_user.street != 'None':
        form.street.data = current_user.street
    if current_user.postcode != None and current_user.postcode != 'None':
        form.postcode.data = current_user.postcode
    if current_user.number != None and current_user.number != 'None':
        form.number.data = current_user.number
    if current_user.city != 'None' and current_user.city != None:
        form.city.data = current_user.city
    return render_template("edition.html",form=form)

# Logging out - done
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('The user has been log out.')
    return redirect(url_for('index'))

# Logging out - done
@app.route('/discount')
@login_required
def discount():
    return render_template("discount.html")

# Necessary - done
@login_manager.user_loader
def load_user(user_id):
    cursor = connection.cursor()
    query = ("SELECT * FROM users WHERE id=%d" % int(user_id))
    cursor.execute(query)
    if cursor.rowcount == 0:
        return None
    for row in cursor:
        user = User(id=row[0], name = row[1],surname =  row[2], email = row[3], password = row[4],role_id =  row[5], street = row[6],number =  row[7], city = row[8],postcode =  row[9])
        return user

# Sending user data to SQL server
@login_required
def update_user(user):
    cursor = connection.cursor()
    query = ("UPDATE projekt.dbo.users SET name='%s', surname='%s', street='%s', number='%s', city='%s', postcode='%s' WHERE id=%d"
             % (user.name, user.surname, user.street, user.number, user.city, user.postcode, int(user.id)))
    cursor.execute(query)
    cursor.close()
    connection.commit()

# Adding new user to database
def add_user(user):
    cursor = connection.cursor()
    query = ("INSERT INTO projekt.dbo.users (name,email,role_id, password,surname,street,number,city,postcode) VALUES  ('%s','%s','%d',%s,'%s','%s','%s','%s','%s')"
             % (user.name, user.email, int(user.role_id), user.password, user.surname, user.street, user.number, user.city, user.postcode))
    cursor.execute(query)
    cursor.close()
    connection.commit()
    return

### Adding elements to database ###
@app.route("/add/offer", methods=['POST','GET'])
@login_required
@admin_required
def add_offer():
    form = AddOffer()
    form.food.choices=food()
    form.flight_to.choices=air()
    form.flight_from.choices=air()
    if form.validate_on_submit():
        cursor = connection.cursor()
        query = ("INSERT INTO oferty VALUES ('%d','%s','%s','%d','%d','%d','%d','%d')" \
                % (int(form.hotel.data), form.date_from.data, form.date_for.data, int(form.flight_from.data), int(form.flight_to.data), int(form.food.data), int(form.price.data), int(form.people.data)))
        cursor.execute(query)
        cursor.commit()
        flash('Oferta została dodana')
    return render_template("add/oferta.html", form = form)

@app.route("/add/country", methods=['POST','GET'])
@login_required
@admin_required
def add_country():
    form = AddCountry()
    if form.validate_on_submit():
        cursor = connection.cursor()
        query = ("INSERT INTO panstwa VALUES ('%s')" % form.country_name.data)
        cursor.execute(query)
        cursor.commit()
        flash('Panstwo zostało dodane')
    return render_template("add/country.html", form = form)

@app.route("/add/city", methods=['POST','GET'])
@login_required
@admin_required
def add_city():
    form = AddCity()
    form.country_name.choices=country()
    if form.validate_on_submit():
        cursor = connection.cursor()
        query = ("INSERT INTO miasta VALUES ('%s','%d')" % (form.city_name.data, int(form.country_name.data)))
        cursor.execute(query)
        cursor.commit()
        flash('Miasto zostało dodane')
    return render_template("add/city.html", form = form)

@app.route("/add/attr", methods=['POST','GET'])
@login_required
@admin_required
def add_attr():
    form = AddAttr()
    if form.validate_on_submit():
        cursor = connection.cursor()
        query = ("INSERT INTO atrakcje VALUES ('%s')" % (form.attr_name.data))
        cursor.execute(query)
        cursor.commit()
        flash('Atrakcja została dodana')
    return render_template("add/attr.html", form = form)

@app.route("/add/food", methods=['POST','GET'])
@login_required
@admin_required
def add_food():
    form = AddFood()
    if form.validate_on_submit():
        cursor = connection.cursor()
        query = ("INSERT INTO wyzyw VALUES ('%s')" % (form.food_name.data))
        cursor.execute(query)
        cursor.commit()
        flash('Wyzywienie zostało dodane')
    return render_template("add/food.html", form = form)

@app.route("/add/air", methods=['POST','GET'])
@login_required
@admin_required
def add_air():
    form = AddAir()
    form.city_name.choices=city()
    if form.validate_on_submit():
        cursor = connection.cursor()
        query = ("INSERT INTO lotniska VALUES ('%s','%d')" % (form.air_name.data, int(form.city_name.data)))
        cursor.execute(query)
        cursor.commit()
        flash('Lotnisko zostało dodane')
    return render_template("add/air.html", form = form)

@app.route("/add/hotel", methods=['POST','GET'])
@login_required
@admin_required
def add_hotel():
    form = AddHotel()
    form.city.choices=city()
    form.attr.choices=attractions_all()
    if form.validate_on_submit():
        cursor = connection.cursor()
        query = ("INSERT INTO hotele VALUES ('%s','%d')" % (form.hotel_name.data, int(form.city.data)))
        cursor.execute(query)
        cursor.commit()
        query = ("SELECT * FROM hotele WHERE name='%s'" % form.hotel_name.data)
        cursor.execute(query)
        out = cursor.fetchall()
        for row in out:
            for element in form.attr.data:
                query = ("INSERT INTO atrakcje_hotele VALUES ('%d','%d')" % (int(row[0]), int(element)))
                cursor.execute(query)
                cursor.commit()
        flash('Hotel został dodany')
    return render_template("add/hotel.html", form = form)


### All elements in one tables

@app.route("/see/offer", methods=['POST','GET'])
@login_required
@admin_required
def see_offer():
    cursor = connection.cursor()
    query = "SELECT o.id, h.name, o.data_od, o.data_do, w.name, o.cena, o.ilosc_miejsc, l.name, l2.name \
                    FROM oferty o, lotniska l, hotele h, wyzyw w, lotniska l2 \
                    WHERE o.id_lotn_tu=l.id AND o.id_lotn_tam = l2.id AND o.id_hotelu=h.id AND o.id_wyzyw=w.id"
    cursor.execute(query)
    data = cursor.fetchall()
    return render_template("see/offer.html", data=data)

@app.route("/see/country", methods=['POST','GET'])
@login_required
@admin_required
def see_country():
    cursor = connection.cursor()
    query = "SELECT * FROM panstwa"
    cursor.execute(query)
    data = cursor.fetchall()
    return render_template("see/country.html", data = data)

@app.route("/see/city", methods=['POST','GET'])
@login_required
@admin_required
def see_city():
    cursor = connection.cursor()
    query = "SELECT m.id, m.name, p.name FROM miasta m, panstwa p WHERE m.id_panstwa=p.id"
    cursor.execute(query)
    data = cursor.fetchall()
    return render_template("see/city.html", data = data)

@app.route("/see/attr", methods=['POST','GET'])
@login_required
@admin_required
def see_attr():
    cursor = connection.cursor()
    query = "SELECT * FROM atrakcje"
    cursor.execute(query)
    data = cursor.fetchall()
    return render_template("see/attr.html", data = data)

@app.route("/see/food", methods=['POST','GET'])
@login_required
@admin_required
def see_food():
    cursor = connection.cursor()
    query = "SELECT * FROM wyzyw"
    cursor.execute(query)
    data = cursor.fetchall()
    return render_template("see/food.html", data = data)

@app.route("/see/air", methods=['POST','GET'])
@login_required
@admin_required
def see_air():
    cursor = connection.cursor()
    query = "SELECT l.id, l.name, m.name FROM miasta m, lotniska l WHERE l.id_miasta=m.id"
    cursor.execute(query)
    data = cursor.fetchall()
    return render_template("see/air.html", data = data)

@app.route("/see/hotel", methods=['POST','GET'])
@login_required
@admin_required
def see_hotel():
    cursor = connection.cursor()
    query = "SELECT DISTINCT h.id, h.name, m.name, atrakcja = STUFF ( \
		    (SELECT ',' + aa.name FROM atrakcje aa, atrakcje_hotele ahh \
		    WHERE ahh.id_atrakcji=aa.id AND h.id = ahh.id_hotelu \
		    FOR XML PATH(''), TYPE).value('.', 'NVARCHAR(MAX)'), 1, 1, '') \
            FROM hotele h \
            JOIN miasta m ON m.id=h.id_miasta \
            JOIN atrakcje_hotele ah ON ah.id_hotelu=h.id \
            JOIN atrakcje a ON ah.id_atrakcji=a.id \
            ORDER BY h.id"
    cursor.execute(query)
    data = cursor.fetchall()
    return render_template("see/hotel.html", data = data)

@app.route("/see/user", methods=['POST','GET'])
@login_required
@admin_required
def see_user():
    cursor = connection.cursor()
    query = "SELECT u.id, u.name, u.surname, u.email, r.name FROM users u, roles r WHERE u.role_id = r.id"
    cursor.execute(query)
    data = cursor.fetchall()
    return render_template("see/user.html", data = data)

@app.route("/see/user_profile/<int:id>", methods=['POST','GET'])
@login_required
@admin_required
def see_user_profile(id):
    cursor = connection.cursor()
    query = "SELECT * FROM users u, roles r WHERE u.role_id = r.id AND u.id=%d" % id
    cursor.execute(query)
    data = cursor.fetchall()
    return render_template("see/user_profile.html", user = data[0])


# Delete rows

def delete(table,id,message):
    cursor = connection.cursor()
    query = ("DELETE FROM %s WHERE id=%d" % (table,id))
    try:
        cursor.execute(query)
        cursor.commit()
    except:
        flash("Ten obiekt nie może zostać usunięty - zależą od niego inne elementy w bazie! Usuń referencje i spróbuj ponownie")
    else:
        flash(message)

def delete_ah(table,id,message):
    cursor = connection.cursor()
    query = ("DELETE FROM %s WHERE id_hotelu=%d" % (table,id))
    try:
        cursor.execute(query)
        cursor.commit()
    except:
        flash("Ten obiekt nie może zostać usunięty - zależą od niego inne elementy w bazie! Usuń referencje i spróbuj ponownie")

@app.route("/delete/city/<int:id>", methods=['POST','GET'])
@login_required
@admin_required
def delete_city(id):
    delete('miasta',id,"Miasto zostało usunięte")
    return (redirect(url_for('see_city')))

@app.route("/delete/country/<int:id>", methods=['POST','GET'])
@login_required
@admin_required
def delete_country(id):
    delete('panstwa',id,"Państwo zostało usunięte")
    return (redirect(url_for('see_country')))

@app.route("/delete/air/<int:id>", methods=['POST','GET'])
@login_required
@admin_required
def delete_air(id):
    delete('lotniska',id,"Lotnisko zostało usunięte")
    return (redirect(url_for('see_air')))

@app.route("/delete/attr/<int:id>", methods=['POST','GET'])
@login_required
@admin_required
def delete_attr(id):
    delete('atrakcje',id,"Atrakcja została usunięta")
    return (redirect(url_for('see_attr')))

@app.route("/delete/food/<int:id>", methods=['POST','GET'])
@login_required
@admin_required
def delete_food(id):
    delete('wyzyw',id,"Wyżywienie zostało usunięte")
    return (redirect(url_for('see_food')))

@app.route("/delete/hotel/<int:id>", methods=['POST','GET'])
@login_required
@admin_required
def delete_hotel(id):
    delete_ah('atrakcje_hotele', id, "")
    delete('hotele',id,"Hotel został usunięty")
    return (redirect(url_for('see_hotel')))

@app.route("/delete/offer/<int:id>", methods=['POST','GET'])
@login_required
@admin_required
def delete_offer(id):
    delete('oferty',id,"Oferta została usunięta")
    return (redirect(url_for('see_offer')))

@app.route("/delete/user/<int:id>", methods=['POST','GET'])
@login_required
@admin_required
def delete_user(id):
    if current_user.id == id:
        flash("Nie możesz usunąć siebie!")
        return (redirect(url_for('see_user')))
    delete('users',id,"Użytkownik został usunięty")
    return (redirect(url_for('see_user')))



# Update rows
@app.route("/update/country/<int:id>", methods=['POST','GET'])
@login_required
@admin_required
def update_country(id):
    cursor = connection.cursor()
    query = ("SELECT * FROM panstwa WHERE id=%d" % id)
    cursor.execute(query)
    data = cursor.fetchall()
    if len(data) == 0:
        flash("Państwo o podanym id nie istnieje")
        return redirect(url_for('see_country'))
    else:
        form = EditCountry(country_name=data[0][1])
    if form.validate_on_submit():
        query = ("UPDATE panstwa SET name='%s' WHERE id=%d" % (form.country_name.data,id))
        cursor.execute(query)
        cursor.commit()
        return redirect(url_for('see_country'))
    return render_template("update/country.html", form=form)

@app.route("/update/city/<int:id>", methods=['POST','GET'])
@login_required
@admin_required
def update_city(id):
    cursor = connection.cursor()
    query = ("SELECT * FROM miasta WHERE id=%d" % id)
    cursor.execute(query)
    data = cursor.fetchall()
    if len(data) == 0:
        flash("Miasto o podanym id nie istnieje")
        return redirect(url_for('see_city'))
    else:
        form = EditCity(city_name=data[0][1],country_name=data[0][2])
        form.country_name.choices=country()
    if form.validate_on_submit():
        query = ("UPDATE miasta SET name='%s',id_panstwa=%d WHERE id=%d" % (form.city_name.data,form.country_name.data,id))
        cursor.execute(query)
        cursor.commit()
        return redirect(url_for('see_city'))
    return render_template("update/city.html", form=form)

@app.route("/update/air/<int:id>", methods=['POST','GET'])
@login_required
@admin_required
def update_air(id):
    cursor = connection.cursor()
    query = ("SELECT * FROM lotniska WHERE id=%d" % id)
    cursor.execute(query)
    data = cursor.fetchall()
    if len(data) == 0:
        flash("Lotnisko o podanym id nie istnieje")
        return redirect(url_for('see_air'))
    else:
        form = EditAir(air_name=data[0][1],city_name=data[0][2])
        form.city_name.choices=city()
    if form.validate_on_submit():
        query = ("UPDATE lotniska SET name='%s',id_miasta=%d WHERE id=%d" % (form.air_name.data,form.city_name.data,id))
        cursor.execute(query)
        cursor.commit()
        return redirect(url_for('see_air'))
    return render_template("update/air.html", form=form)

@app.route("/update/attr/<int:id>", methods=['POST','GET'])
@login_required
@admin_required
def update_attr(id):
    cursor = connection.cursor()
    query = ("SELECT * FROM atrakcje WHERE id=%d" % id)
    cursor.execute(query)
    data = cursor.fetchall()
    if len(data) == 0:
        flash("Atrakcja o podanym id nie istnieje")
        return redirect(url_for('see_attr'))
    else:
        form = EditAttr(attr_name=data[0][1])
    if form.validate_on_submit():
        query = ("UPDATE atrakcje SET name='%s' WHERE id=%d" % (form.attr_name.data,id))
        cursor.execute(query)
        cursor.commit()
        return redirect(url_for('see_attr'))
    return render_template("update/attr.html", form=form)

@app.route("/update/food/<int:id>", methods=['POST','GET'])
@login_required
@admin_required
def update_food(id):
    cursor = connection.cursor()
    query = ("SELECT * FROM wyzyw WHERE id=%d" % id)
    cursor.execute(query)
    data = cursor.fetchall()
    if len(data) == 0:
        flash("Wyzywienie o podanym id nie istnieje")
        return redirect(url_for('see_food'))
    else:
        form = EditFood(food_name=data[0][1])
    if form.validate_on_submit():
        query = ("UPDATE wyzyw SET name='%s' WHERE id=%d" % (form.food_name.data,id))
        cursor.execute(query)
        cursor.commit()
        return redirect(url_for('see_food'))
    return render_template("update/food.html", form=form)

@app.route("/update/hotel/<int:id>", methods=['POST','GET'])
@login_required
@admin_required
def update_hotel(id):
    cursor = connection.cursor()
    query = ("SELECT * FROM hotele h WHERE id=%d" % (id))
    cursor.execute(query)
    data = cursor.fetchall()
    query = ("SELECT * FROM atrakcje_hotele ah WHERE id_hotelu=%d" % (id))
    cursor.execute(query)
    attrakcje = cursor.fetchall()
    if not attrakcje:
        attrakcje=[]
    if len(data) == 0:
        flash("Hotel o podanym id nie istnieje")
        return redirect(url_for('see_hotel'))
    else:
        form = EditHotel(hotel_name=data[0][1], city=data[0][2], attr = attrakcje)
        form.attr.choices=attractions_all()
        form.city.choices=city()
    if form.validate_on_submit():
        query = ("UPDATE hotele SET name='%s', id_miasta=%d WHERE id=%d" % (form.hotel_name.data,form.city.data,id))
        cursor.execute(query)
        cursor.commit()
        query = ("DELETE FROM atrakcje_hotele WHERE id_hotelu=%d" % (id))
        cursor.execute(query)
        cursor.commit()
        for data_attr in form.attr.data:
            query = ("INSERT INTO atrakcje_hotele VALUES (%d,%d)" % (id,data_attr))
            cursor.execute(query)
            cursor.commit()
        return redirect(url_for('see_hotel'))
    return render_template("update/hotel.html", form=form)

@app.route("/update/offer/<int:id>", methods=['POST','GET'])
@login_required
@admin_required
def update_offer(id):
    cursor = connection.cursor()
    query = ("SELECT * FROM oferty WHERE id=%d" % id)
    cursor.execute(query)
    data = cursor.fetchall()
    if len(data) == 0:
        flash("Oferta o podanym id nie istnieje")
        return redirect(url_for('see_offer'))
    else:
        date_1 = datetime.strptime(data[0][2], '%Y-%m-%d')
        date_2 = datetime.strptime(data[0][3], '%Y-%m-%d')
        form = EditOffer(hotel=data[0][1], date_from = date_1, date_for = date_2, flight_to=data[0][5], flight_from=data[0][4], food=data[0][6], people=int(data[0][7]), price=data[0][8])
        form.hotel.choices=hotel()
        form.flight_from.choices=air()
        form.flight_to.choices=air()
        form.food.choices=food()
    if form.validate_on_submit():
        query = ("UPDATE oferty SET id_hotelu=%d, data_od='%s', data_do='%s', id_lotn_tu=%d, id_lotn_tam=%d, id_wyzyw=%d, ilosc_miejsc=%d, cena=%d WHERE id=%d" %
                 (form.hotel.data, form.date_from.data, form.date_for.data, form.flight_from.data, form.flight_to.data, form.food.data, int(form.people.data), form.price.data, id))
        cursor.execute(query)
        cursor.commit()
        return redirect(url_for('see_offer'))
    return render_template("update/offer.html", form=form)

if __name__=='__main__':
    connection = pypyodbc.connect('Driver={SQL Server};Server=DESKTOP-5G79BTM;Database=projekt')
    app.run(debug=True)