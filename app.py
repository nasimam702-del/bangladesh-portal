# -*- coding: utf-8 -*-
from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = "bangladesh_portal_secret_2026"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    last_login = db.Column(db.DateTime, nullable=True)

with app.app_context():
    db.create_all()

services = {
    "Sorkari Seba": [
        {"name": "NID Card", "desc": "NID abedon o songsodhon", "icon": "ID", "link": "https://services.nidw.gov.bd"},
        {"name": "Jonmo Nibondhon", "desc": "Jonmo sohod abedon o jachai", "icon": "DOC", "link": "https://bdris.gov.bd"},
        {"name": "Passport Seba", "desc": "Passport er abedon o nobayan", "icon": "PP", "link": "https://www.passport.gov.bd"},
        {"name": "Driving License", "desc": "License abedon o nobayan", "icon": "CAR", "link": "https://bsp.brta.gov.bd"},
        {"name": "Bhumi Seba", "desc": "Khotian, porcha o namjari", "icon": "LAND", "link": "https://land.gov.bd"},
        {"name": "Trade License", "desc": "Byabosaik license abedon", "icon": "BIZ", "link": "#"},
    ],
    "Shikha Seba": [
        {"name": "SSC/HSC Result", "desc": "Board porikhar result dekhun", "icon": "EDU", "link": "http://www.educationboardresults.gov.bd"},
        {"name": "University Vorthi", "desc": "GST o university vorthi tothyo", "icon": "UNI", "link": "#"},
        {"name": "Britti Abedon", "desc": "Sorkari brittir tothyo o abedon", "icon": "SCH", "link": "#"},
        {"name": "Certificate Jachai", "desc": "Certificate verification", "icon": "CER", "link": "#"},
    ],
    "Swastha Seba": [
        {"name": "Hospital Khujun", "desc": "Kacher sorkari-besorkari hospital", "icon": "HSP", "link": "#"},
        {"name": "Ambulance Seba", "desc": "Joruri ambulance jogajog", "icon": "AMB", "link": "#"},
        {"name": "Rokto Bank", "desc": "Roktodaata o rokto banker talika", "icon": "BLD", "link": "#"},
        {"name": "Tika Seba", "desc": "Sorkari tikadan kormosuci", "icon": "VAC", "link": "https://surokkha.gov.bd"},
    ],
    "Arthik Seba": [
        {"name": "Mobile Banking", "desc": "bKash, Nagad, Rocket tothyo", "icon": "MOB", "link": "#"},
        {"name": "Tax Return", "desc": "Ayokor return dakhil", "icon": "TAX", "link": "https://etaxnbr.gov.bd"},
        {"name": "Bank Seba", "desc": "Sorkari banker sebasomuho", "icon": "BNK", "link": "#"},
        {"name": "Bima Seba", "desc": "Jibon o swastha bima", "icon": "INS", "link": "#"},
    ],
    "Jogajog o Poribohon": [
        {"name": "Train Ticket", "desc": "Bangladesh Railway online booking", "icon": "TRN", "link": "https://eticket.railway.gov.bd"},
        {"name": "Bus Seba", "desc": "Antorjela baser tothyo", "icon": "BUS", "link": "#"},
        {"name": "Biman Ticket", "desc": "Biman Bangladesh Airlines", "icon": "AIR", "link": "https://www.biman-airlines.com"},
        {"name": "Dak Seba", "desc": "Parcel tracking o postal seba", "icon": "POST", "link": "https://www.bangladeshpost.gov.bd"},
    ],
    "Joruri Seba": [
        {"name": "999 Joruri", "desc": "Police, Fire, Ambulance", "icon": "SOS", "link": "tel:999"},
        {"name": "Durniti Domon", "desc": "Dudoke obhijog dayer", "icon": "ACC", "link": "https://www.acc.org.bd"},
        {"name": "Manobaddhikar", "desc": "Manobaddhikar commission", "icon": "HUM", "link": "http://www.nhrc.org.bd"},
        {"name": "Aini Sohayta", "desc": "Binamullo aini seba", "icon": "LAW", "link": "#"},
    ],
}

emergency_numbers = [
    {"name": "Joruri", "number": "999"},
    {"name": "Fire", "number": "199"},
    {"name": "Ambulance", "number": "16430"},
    {"name": "Police", "number": "100"},
    {"name": "Nari", "number": "109"},
    {"name": "Shishu", "number": "1098"},
]

@app.route("/")
def index():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user = User.query.get(session['user_id'])
    return render_template("index.html", services=services, emergency=emergency_numbers, user=user)

@app.route("/search")
def search():
    query = request.args.get("q", "").lower()
    results = []
    for category, items in services.items():
        for item in items:
            if query in item["name"].lower() or query in item["desc"].lower():
                results.append({**item, "category": category})
    return jsonify(results)

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")
        if User.query.filter_by(email=email).first():
            return render_template("register.html", error="This email is already registered!")
        hashed = generate_password_hash(password)
        user = User(name=name, email=email, password=hashed)
        db.session.add(user)
        db.session.commit()
        session['user_id'] = user.id
        return redirect(url_for('index'))
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            user.last_login = datetime.now()
            db.session.commit()
            return redirect(url_for('index'))
        return render_template("login.html", error="Email or Password is incorrect!")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login'))

@app.route("/admin")
def admin():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user = User.query.get(session['user_id'])
    if not user or not user.is_admin:
        return redirect(url_for('index'))
    users = User.query.all()
    return render_template("admin.html", users=users, total=len(users))

if __name__ == "__main__":
    app.run(debug=True)
