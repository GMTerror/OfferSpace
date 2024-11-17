from markupsafe import escape
from flask import Flask, render_template, redirect, url_for, flash, request, abort
import os
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
import sqlite3
import datetime as dt

app = Flask(__name__)
app.config['SECRET_KEY'] = 'dsoedyewyfgsydjsf7hgf'

##CONNECT TO DB
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///offers.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


##CONFIGURE TABLES
class OfferWeb(db.Model):
    __tablename__ = "offer_list"
    id = db.Column(db.Integer, primary_key=True)
    store = db.Column(db.String(250), nullable=False)
    offer_title = db.Column(db.String(250), nullable=False)
    valid = db.Column(db.Integer, nullable=False)
    s_date = db.Column(db.String(250), nullable=False)
    e_date = db.Column(db.String(250), nullable=False)
    featured = db.Column(db.Integer, nullable=False)
    fe_date = db.Column(db.String(250), nullable=False)
    img_url = db.Column(db.String(250), nullable=False)
    file_src = db.Column(db.String(250), unique=True, nullable=False)

with app.app_context():
    db.create_all()

def validity():
    format = '%d-%m-%Y'
    for offer in db.session.execute(db.select(OfferWeb)).scalars():
        date_e = dt.datetime.strptime(offer.e_date, format).date()
        date_s = dt.datetime.strptime(offer.s_date, format).date()
        date_fe = dt.datetime.strptime(offer.fe_date, format).date()
        today = dt.datetime.today().date()
        if date_s > today or date_e < today:
            offer.valid = 0
        else:
            offer.valid = 1
            if date_fe < today:
                offer.featured = 0
    db.session.commit()



@app.route("/")
def home():
    validity()
    feature = [fe_off for fe_off in db.session.execute(db.Select(OfferWeb)).scalars() if fe_off.featured == 1 and fe_off.valid == 1]
    stores = {store.store for store in db.session.execute(db.Select(OfferWeb)).scalars()}
    return render_template("home.html", featured=feature, stores=stores, year=dt.date.today().year)

@app.route("/about")
def about():
    return render_template("about.html", year=dt.date.today().year)

@app.route("/contact")
def contact():
    return render_template("contact.html", year=dt.date.today().year, phone="+91xxxxxxxxxx", email="lakshmysairam@gmail.com")

@app.route("/store/<name>")
def store(name):
    validity()
    offer_store = [offers for offers in db.session.execute(db.Select(OfferWeb)).scalars() if offers.valid == 1 and offers.store == name]
    e_offer = [offers for offers in db.session.execute(db.Select(OfferWeb)).scalars() if offers.valid != 1 and offers.store == name]
    return render_template("store.html", name=name, val=offer_store, exp=e_offer, year=dt.date.today().year)

@app.route("/offer/<off_title>")
def offer(off_title):
    validity()
    offer = [offer for offer in db.session.execute(db.Select(OfferWeb)).scalars() if offer.valid == 1 and offer.offer_title == off_title][0]
    return render_template("offer.html", offer=offer, year=dt.date.today().year)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)