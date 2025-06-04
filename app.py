import os
import sys
import requests
from flask_cors import CORS
from flask import Flask, render_template, redirect, request, flash, url_for, session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from sqlalchemy import func, Column, Integer, String, Date, Time, DateTime
from datetime import datetime
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker
from models import User, SQLASession, engine, ScheduleAppointment
from dotenv import load_dotenv 
import openai

app = Flask(__name__)
CORS(app)

#app config
SQLASession = sessionmaker(bind=engine)
db_session = SQLASession()

#setting the connection to the db and secret key form the (.env) file 
load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')
app.secret_key = os.getenv('SECRET_KEY')

TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY")


#for uploading pictures 
UPLOAD_FOLDER = os.path.join('static', 'uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

#route for the home page
@app.route('/')
def index():
    return render_template('index.html')
        
#route for the patient dashboard
@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/services')
def services():
    return render_template('services.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')
        
@app.route('/privacy')
def privacy():
    return render_template('privacy.html')

@app.route('/terms')
def terms():
    return render_template('terms.html')
       
@app.route('/faq')
def faq():
    return render_template('faq.html')

@app.route('/register', methods=['GET', 'POST'])
def register():

    if request.method == 'POST': 
        try:
            user_type = request.form.get('user_type')
            first_name = request.form.get('first_name')
            last_name = request.form.get('last_name')
            email = request.form.get('email')
            password = request.form.get('password')
            sc_code = request.form.get('sc_code')
            tel = request.form.get('tel')
            confirm_password = request.form.get('confirm_password')

            # Check if passwords match
            if password != confirm_password:
                flash('Passwords do not match!', 'error')
                return redirect(url_for('register'))

            hashed_password = generate_password_hash(password)

            # Use session context manager
            with SQLASession() as db_session:
                existing_user = db_session.query(User).filter_by(email=email).first()

                if existing_user:
                    flash('Email is already registered.', 'error')
                    return redirect(url_for('register'))

                new_user = User(
                    user_type=user_type,
                    first_name=first_name,
                    last_name=last_name,
                    email=email,
                    tel=tel,
                    password=hashed_password,
                    sc_code=sc_code,
                    image_url='',
                )

                db_session.add(new_user)
                db_session.commit()

                flash('Successfully registered!', 'success')
                return redirect(url_for('login'))

        except Exception as e:
            flash(f'Unexpected error: {str(e)}', 'error')
            return redirect(url_for('register'))

    # GET request: show the register page
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
      
    if request.method == 'POST':
            user_type = request.form.get('user_type').strip()
            first_name = request.form.get('first_name').strip()
            password = request.form.get('password')
            sc_code = request.form.get('sc_code').strip()


            with SQLASession() as db_session:
                user = db_session.query(User).filter(
                    User.user_type == user_type,
                    func.lower(User.first_name) == first_name.lower(),
                    User.sc_code == sc_code
                ).first()

            if not user or not check_password_hash(user.password, password):
                flash('invalid credentials! please try again', 'error')
                return redirect(url_for('login'))
            
            session['user_id'] = user.id
            session['user_type'] = user.user_type 
            session['first_name'] = user.first_name
            session['sc_code'] = user.sc_code

            if user.user_type == 'patient':
                return redirect(url_for('patient_dash'))
            if user.user_type == 'doctor':
                return redirect(url_for('doctor_dash'))
            if user.user_type == 'nurse':
                return redirect(url_for('nurse_dash'))
            
            flash('Unexpected error: invalid user type!', 'error')
            return redirect(url_for('login'))
           

    return render_template('login.html')

# ==== route for the patient dashboard && it's compenents ====
@app.route('/patient_dash')
def patient_dash():
    return render_template('patient_dash.html')


@app.route('/api/ask', methods=['POST'])
def ask():
    data = request.get_json()
    user_prompt = data.get("prompt", "").strip()

    # Step 1: Build a professional instruction prompt
    full_prompt = (
        "You are a helpful, kind, and professional medical assistant. "
        "Answer clearly and politely, using numbered lists or paragraphs when needed.\n\n"
        f"Question: {user_prompt}\n\nAnswer:"
    )

    headers = {
        "Authorization": f"Bearer {TOGETHER_API_KEY}",
        "Content-Type": "application/json"
    }

    json_data = {
        "model": "mistralai/Mixtral-8x7B-Instruct-v0.1",
        "prompt": full_prompt,
        "max_tokens": 300,
        "temperature": 0.7
    }

    response = requests.post("https://api.together.xyz/v1/completions", headers=headers, json=json_data)

    if response.ok:
        reply = response.json()["choices"][0]["text"].strip()

        # Step 2: Fallback if the response is strange or empty
        if not reply or "I don't understand" in reply or "I'm not sure" in reply:
            reply = "Sorry, I couldn’t understand your question clearly. Could you rephrase it?"

        return jsonify({"response": reply})
    else:
        return jsonify({"error": "Failed to get AI response"}), 500


#route for patient_appoin
@app.route('/patient_appoin')
def patient_appoin():
    return render_template('patient_appoin.html')

#route for patient_mess
@app.route('/patient_mess')
def patient_mess():
    return render_template('patient_mess.html')

#route for patient_prf
@app.route('/patient_prf')
def patient_prf():
    return render_template('patient_prf.html')

#route for patient_sttg
@app.route('/patient_sttg')
def patient_sttg():
    return render_template('patient_sttg.html')
        
# ==== route for the doctor dashboard  && it's compenents ====
@app.route('/doctor_dash')
def doctor_dash():
    return render_template('doctor_dash.html')

#route for doc_appoin
@app.route('/doc_appoin')
def doc_appoin():
    return render_template('doc_appoin.html')

#route for doc_mess
@app.route('/doc_mess')
def doc_mess():
    return render_template('doc_mess.html')

#route for doc_patient
@app.route('/doc_patient')
def doc_patient():
    return render_template('doc_patient.html')

#route for doc_sttg
@app.route('/doc_sttg')
def doc_sttg():
    return render_template('doc_sttg.html')

# ==== route for the nurse dashboard && it's compenents ====
@app.route('/nurse_dash')
def nurse_dash():
    return render_template('nurse_dash.html')

#route for nur_mess
@app.route('/nur_mess')
def nur_mess():
    return render_template('nur_mess.html')

#route for nur_prof
@app.route('/nur_patient')
def nur_patient():
    return render_template('nur_patient.html')

#route for nur_sttg
@app.route('/nur_sttg')
def nur_sttg():
    return render_template('nur_sttg.html')


if __name__ == '__main__':
    app.run(debug=True)