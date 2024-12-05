from flask import Flask, render_template
import os
from flask_sqlalchemy import SQLAlchemy
import datetime as dt

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')

##CONNECT TO DB
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DB_URI")
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
        if offer.fe_date != 0:
            date_fe = dt.datetime.strptime(offer.fe_date, format).date()    
        else:
            date_fe = 0
        today = dt.datetime.today().date()
        if date_s > today or date_e < today:
            offer.valid = 0
        else:
            offer.valid = 1
            if date_fe < today or date_fe == 0:
                offer.featured = 0
            else:
                offer.featured = 1
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
    return render_template("contact.html", year=dt.date.today().year, phone="+91xxxxxxxxxx", email="example@gmail.com")

@app.route("/store/<name>")
def store(name):
    validity()
    offer_store = [offers for offers in db.session.execute(db.Select(OfferWeb)).scalars() if offers.valid == 1 and offers.store == name]
    e_offer = [offers for offers in db.session.execute(db.Select(OfferWeb)).scalars() if offers.valid != 1 and offers.store == name]
    return render_template("store.html", name=name, val=offer_store, exp=e_offer, year=dt.date.today().year)

@app.route("/offer/<int:off_id>")
def offer(off_id):
    validity()
    offer = [offer for offer in db.session.execute(db.Select(OfferWeb)).scalars() if offer.valid == 1 and offer.id == off_id][0]
    return render_template("offer.html", offer=offer, year=dt.date.today().year)

if __name__ == '__main__':
    app.run()