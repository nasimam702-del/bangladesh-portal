# -*- coding: utf-8 -*-
from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = "bangladesh_portal_secret_2026"
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///users.db')
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
    "সরকারি সেবা": {
        "bn": "সরকারি সেবা",
        "en": "Government Services",
        "items": [
            {"name_bn": "জাতীয় পরিচয়পত্র (NID)", "name_en": "National ID Card (NID)", "desc_bn": "NID আবেদন ও সংশোধন", "desc_en": "NID Application & Correction", "icon": "🪪", "link": "https://services.nidw.gov.bd"},
            {"name_bn": "জন্ম নিবন্ধন", "name_en": "Birth Registration", "desc_bn": "জন্ম সনদ আবেদন ও যাচাই", "desc_en": "Apply & Verify Birth Certificate", "icon": "📋", "link": "https://bdris.gov.bd"},
            {"name_bn": "পাসপোর্ট সেবা", "name_en": "Passport Service", "desc_bn": "পাসপোর্ট আবেদন ও নবায়ন", "desc_en": "Apply & Renew Passport", "icon": "📕", "link": "https://www.passport.gov.bd"},
            {"name_bn": "ড্রাইভিং লাইসেন্স", "name_en": "Driving License", "desc_bn": "লাইসেন্স আবেদন ও নবায়ন", "desc_en": "Apply & Renew License", "icon": "🚗", "link": "https://bsp.brta.gov.bd"},
            {"name_bn": "ভূমি সেবা", "name_en": "Land Service", "desc_bn": "খতিয়ান, পর্চা ও নামজারি", "desc_en": "Land Records & Registration", "icon": "🏡", "link": "https://land.gov.bd"},
            {"name_bn": "ট্রেড লাইসেন্স", "name_en": "Trade License", "desc_bn": "ব্যবসায়িক লাইসেন্স আবেদন", "desc_en": "Business License Application", "icon": "📜", "link": "#"},
        ]
    },
    "শিক্ষা সেবা": {
        "bn": "শিক্ষা সেবা",
        "en": "Education Services",
        "items": [
            {"name_bn": "SSC/HSC ফলাফল", "name_en": "SSC/HSC Results", "desc_bn": "বোর্ড পরীক্ষার ফলাফল দেখুন", "desc_en": "Check Board Exam Results", "icon": "🎓", "link": "http://www.educationboardresults.gov.bd"},
            {"name_bn": "বিশ্ববিদ্যালয় ভর্তি", "name_en": "University Admission", "desc_bn": "GST ও ভর্তি তথ্য", "desc_en": "GST & Admission Info", "icon": "🏫", "link": "#"},
            {"name_bn": "বৃত্তি আবেদন", "name_en": "Scholarship", "desc_bn": "সরকারি বৃত্তির তথ্য ও আবেদন", "desc_en": "Government Scholarship Info", "icon": "🏆", "link": "#"},
            {"name_bn": "সনদ যাচাই", "name_en": "Certificate Verify", "desc_bn": "সার্টিফিকেট ভেরিফিকেশন", "desc_en": "Certificate Verification", "icon": "✅", "link": "#"},
        ]
    },
    "স্বাস্থ্য সেবা": {
        "bn": "স্বাস্থ্য সেবা",
        "en": "Health Services",
        "items": [
            {"name_bn": "হাসপাতাল খুঁজুন", "name_en": "Find Hospital", "desc_bn": "কাছের সরকারি-বেসরকারি হাসপাতাল", "desc_en": "Find Nearby Hospitals", "icon": "🏥", "link": "#"},
            {"name_bn": "অ্যাম্বুলেন্স সেবা", "name_en": "Ambulance Service", "desc_bn": "জরুরি অ্যাম্বুলেন্স যোগাযোগ", "desc_en": "Emergency Ambulance Contact", "icon": "🚑", "link": "#"},
            {"name_bn": "রক্ত ব্যাংক", "name_en": "Blood Bank", "desc_bn": "রক্তদাতা ও রক্ত ব্যাংকের তালিকা", "desc_en": "Blood Donor & Bank List", "icon": "🩸", "link": "#"},
            {"name_bn": "টিকা সেবা", "name_en": "Vaccination", "desc_bn": "সরকারি টিকাদান কর্মসূচি", "desc_en": "Government Vaccination Program", "icon": "💉", "link": "https://surokkha.gov.bd"},
        ]
    },
    "আর্থিক সেবা": {
        "bn": "আর্থিক সেবা",
        "en": "Financial Services",
        "items": [
            {"name_bn": "মোবাইল ব্যাংকিং", "name_en": "Mobile Banking", "desc_bn": "bKash, Nagad, Rocket তথ্য", "desc_en": "bKash, Nagad, Rocket Info", "icon": "📱", "link": "#"},
            {"name_bn": "ট্যাক্স রিটার্ন", "name_en": "Tax Return", "desc_bn": "আয়কর রিটার্ন দাখিল", "desc_en": "File Income Tax Return", "icon": "💰", "link": "https://etaxnbr.gov.bd"},
            {"name_bn": "ব্যাংক সেবা", "name_en": "Bank Service", "desc_bn": "সরকারি ব্যাংকের সেবাসমূহ", "desc_en": "Government Bank Services", "icon": "🏦", "link": "#"},
            {"name_bn": "বীমা সেবা", "name_en": "Insurance", "desc_bn": "জীবন ও স্বাস্থ্য বীমা", "desc_en": "Life & Health Insurance", "icon": "🛡️", "link": "#"},
        ]
    },
    "যোগাযোগ ও পরিবহন": {
        "bn": "যোগাযোগ ও পরিবহন",
        "en": "Transport & Communication",
        "items": [
            {"name_bn": "ট্রেনের টিকিট", "name_en": "Train Ticket", "desc_bn": "Bangladesh Railway অনলাইন বুকিং", "desc_en": "Bangladesh Railway Online Booking", "icon": "🚂", "link": "https://eticket.railway.gov.bd"},
            {"name_bn": "বাস সেবা", "name_en": "Bus Service", "desc_bn": "আন্তঃজেলা বাসের তথ্য", "desc_en": "Inter-city Bus Information", "icon": "🚌", "link": "#"},
            {"name_bn": "বিমান টিকিট", "name_en": "Air Ticket", "desc_bn": "Biman Bangladesh Airlines", "desc_en": "Biman Bangladesh Airlines", "icon": "✈️", "link": "https://www.biman-airlines.com"},
            {"name_bn": "ডাক সেবা", "name_en": "Postal Service", "desc_bn": "পার্সেল ট্র্যাকিং ও পোস্টাল সেবা", "desc_en": "Parcel Tracking & Postal Service", "icon": "📮", "link": "https://www.bangladeshpost.gov.bd"},
        ]
    },
    "জরুরি সেবা": {
        "bn": "জরুরি সেবা",
        "en": "Emergency Services",
        "items": [
            {"name_bn": "জাতীয় জরুরি সেবা", "name_en": "National Emergency", "desc_bn": "999 - পুলিশ, ফায়ার, অ্যাম্বুলেন্স", "desc_en": "999 - Police, Fire, Ambulance", "icon": "🆘", "link": "tel:999"},
            {"name_bn": "দুর্নীতি দমন", "name_en": "Anti-Corruption", "desc_bn": "দুদকে অভিযোগ দায়ের", "desc_en": "File Complaint to ACC", "icon": "⚖️", "link": "https://www.acc.org.bd"},
            {"name_bn": "মানবাধিকার", "name_en": "Human Rights", "desc_bn": "মানবাধিকার কমিশন", "desc_en": "Human Rights Commission", "icon": "🕊️", "link": "http://www.nhrc.org.bd"},
            {"name_bn": "আইনি সহায়তা", "name_en": "Legal Aid", "desc_bn": "বিনামূল্যে আইনি সেবা", "desc_en": "Free Legal Service", "icon": "🏛️", "link": "#"},
        ]
    },
}

emergency_numbers = [
    {"name_bn": "জরুরি সেবা", "name_en": "Emergency", "number": "999"},
    {"name_bn": "ফায়ার সার্ভিস", "name_en": "Fire Service", "number": "199"},
    {"name_bn": "অ্যাম্বুলেন্স", "name_en": "Ambulance", "number": "16430"},
    {"name_bn": "পুলিশ", "name_en": "Police", "number": "100"},
    {"name_bn": "নারী সহায়তা", "name_en": "Women Help", "number": "109"},
    {"name_bn": "শিশু সহায়তা", "name_en": "Children Help", "number": "1098"},
]

def format_services():
    result = []
    for key, cat in services.items():
        result.append({
            "bn": cat["bn"],
            "en": cat["en"],
            "items": cat["items"]
        })
    return result

@app.route("/")
def index():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user = User.query.get(session['user_id'])
    return render_template("index.html", services=format_services(), emergency=emergency_numbers, user=user)

@app.route("/search")
def search():
    query = request.args.get("q", "").lower()
    lang = request.args.get("lang", "bn")
    results = []
    for key, cat in services.items():
        for item in cat["items"]:
            if (query in item["name_bn"].lower() or
                query in item["name_en"].lower() or
                query in item["desc_bn"].lower() or
                query in item["desc_en"].lower()):
                results.append({**item, "category_bn": cat["bn"], "category_en": cat["en"]})
    return jsonify(results)

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")
        if User.query.filter_by(email=email).first():
            return render_template("register.html", error="এই email ইতিমধ্যে নিবন্ধিত!")
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
        return render_template("login.html", error="Email বা Password ভুল!")
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
