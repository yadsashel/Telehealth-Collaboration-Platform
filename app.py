import os
import sys
from flask import Flask, render_template, redirect, request, flash, url_for, session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import func, Column, Integer, String, Date, Time, DateTime
from datetime import datetime
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker
from models import User, SQLASession, engine, ScheduleAppointment
from dotenv import load_dotenv 

app = Flask(__name__)

#app config
SQLASession = sessionmaker(bind=engine)
db_session = SQLASession()

#setting the connection to the db and secret key form the (.env) file 
load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')
app.secret_key = os.getenv('SECRET_KEY') 


#route for the home page
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        try:
            first_name = request.form['first_name']
            last_name = request.form['last_name']
            email = request.form['email']
            password = request.form['password']
            confirm_password = request.form['confirm_password']
            user_type = request.form['user_type']
            mfa_code = request.form['mfa_code']

            if password != confirm_password:
                flash('Passwords do not match', 'error')
                return redirect(url_for('register'))

            hashed_password = generate_password_hash(password)

            with SQLASession() as db_session:  # ✅ Correct session usage
                existing_user = db_session.query(User).filter_by(email=email).first()
                if existing_user:
                    flash('Email already exists', 'error')
                    return redirect(url_for('register'))

                new_user = User(
                    first_name=first_name,
                    last_name=last_name,
                    email=email,
                    password=hashed_password,
                    user_type=user_type,
                    mfa_code=mfa_code
                )
                db_session.add(new_user)
                db_session.commit()

            flash('Registration successful!', 'success')
            return redirect(url_for('login'))

        except SQLAlchemyError as e:
            flash(f'Error: {e}', 'error')
            return redirect(url_for('register'))

    return render_template('register.html')


#route for the Login Page
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user_type = request.form['user_type'].strip()
        first_name = request.form['first_name'].strip().split(' ')[0]
        password = request.form['password']
        mfa_code = request.form['mfa_code'].strip()

        with SQLASession() as db_session:
            user = db_session.query(User).filter(
                User.user_type == user_type,
                func.lower(User.first_name) == first_name.lower(),
                User.mfa_code == mfa_code
            ).first()

        if not user or not check_password_hash(user.password, password):
            flash("Invalid credentials! Please try again.", "error")
            return redirect(url_for('login'))

        session['user_type'] = user.user_type  # Flask session (correct)
        session['first_name'] = user.first_name
        session['mfa_code'] = user.mfa_code

        if user.user_type == 'doctor':
            return redirect(url_for('AppointOver'))
        elif user.user_type == 'patient':
            return redirect(url_for('dashschedule'))
        elif user.user_type == 'nurse':
            return redirect(url_for('PatientRecords'))

        flash("Unexpected error: Invalid user type!", "error")
        return redirect(url_for('login'))

    return render_template('login.html')

#route for home page
@app.route('/')
def index():
    return render_template('index.html')

#route for the About page
@app.route('/About')
def About():
   return render_template('About.html')

#route for the Contact page
@app.route('/Contact')
def Contact():
   return render_template('Contact.html')

#route for the Services page
@app.route('/Services') 
def Services():
   return render_template('Services.html')

#route for the FQA page
@app.route('/FQA')
def FQA():
   return render_template('FQA.html')

#route for the Privacy Page
@app.route('/Privacy')
def Privacy():
   return render_template('Privacy.html')

# |----- Patient's routes ------|

#route for the dash-schedule Page
@app.route('/dashschedule', methods=['GET', 'POST'])
def dashschedule():
    if request.method == 'POST':
        try:
            full_name = request.form['full_name']
            age = request.form['age']
            gender = request.form['gender']
            reason = request.form['reason']
            date_str = request.form['date']
            time_str = request.form['time']
            
            # Parse the date and time properly
            date = datetime.strptime(date_str, "%Y-%m-%d").date()
            time = datetime.strptime(time_str, "%H:%M").time()

            with SQLASession() as db_session:
                new_scheduled_appointment = ScheduleAppointment(
                   full_name=full_name,
                   age=age,
                   gender=gender,
                   reason=reason,
                   date=date,
                   time=time
                )

                db_session.add(new_scheduled_appointment)
                db_session.commit()

            flash('Appointement Scheduled Successfully!', 'success')
            return redirect(url_for('Consult'))
        except SQLAlchemyError as e:
            flash(f'Error: {e}', 'error')
            return redirect(url_for('dashschedule'))

    return render_template('dashschedule.html')

# Route to display "My Appointments" page
@app.route('/Consult')
def Consult():
    with SQLASession() as db_session:
        appointments = db_session.query(ScheduleAppointment).order_by(ScheduleAppointment.date.desc()).all()
    return render_template('Consult.html', appointments=appointments)


#route for the Mymedicines Page
@app.route('/MyMedicines')
def MyMedicines():
   return render_template('MyMedicines.html')

# |----- Nurse's routes ------|

#route for the Patient Records Page
@app.route('/PatientRecords')
def PatientRecords():
   return render_template('PatientRecords.html')

#route for MedMan page
@app.route('/MedMan')
def MedMan():
   return render_template('MedMan.html')


# |----- Doctor's routes ------|

#route for Appoint-Over page
@app.route('/AppointOver')
def AppointOver():
   return render_template('AppointOver.html')

#route for consultations page
@app.route('/Consultations')
def Consultations():
   return render_template('Consultations.html')

#route for Medicines-patient page
@app.route('/Medicines-patient')
def Medicinespatient():
   return render_template('Medicines-patient.html')

if __name__ == '__main__':
    app.run(debug=True)