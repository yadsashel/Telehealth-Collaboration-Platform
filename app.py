import os
import sys
from flask import Flask, render_template, redirect, request, flash, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import func
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker
from models import User, session, engine

app = Flask(__name__)

#app config
app.secret_key = '/Yad_locaL$YeS)%'
Session = sessionmaker(bind=engine)


#route for the home page
@app.route('/')
def index():
   return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        try:
            # Get form data
            first_name = request.form['first_name']
            last_name = request.form['last_name']
            email = request.form['email']
            password = request.form['password']
            confirm_password = request.form['confirm_password']
            user_type = request.form['user_type']
            mfa_code = request.form['mfa_code']

            # Check passwords match
            if password != confirm_password:
                flash('Passwords do not match', 'error')
                return redirect(url_for('register'))

            # Hash password
            hashed_password = generate_password_hash(password)

            # Database interaction
            with session() as db_session:
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
        # Extract form data and preprocess inputs
        user_type = request.form['user_type'].strip()
        first_name = request.form['first_name'].strip().split(' ')[0]  # Extract only the first name
        password = request.form['password']
        mfa_code = request.form['mfa_code'].strip()

        # Debugging print statement (remove in production)
        print(f"user_type: {user_type}, first_name: {first_name}, mfa_code: {mfa_code}")

        # Query the database
        with session() as db_session:
            user = db_session.query(User).filter(
                User.user_type == user_type,
                func.lower(User.first_name) == first_name.lower(),
                User.mfa_code == mfa_code
            ).first()

        # Check if user exists and validate password
        if not user or not check_password_hash(user.password, password):
            flash("Invalid credentials! Please try again.", "error")
            return redirect(url_for('login'))

        # Save user data to session
        session['user_type'] = user.user_type
        session['first_name'] = user.first_name
        session['mfa_code'] = user.mfa_code

        # Redirect based on user type
        if user.user_type == 'doctor':
            flash("Welcome, doctor!", "success")
            return redirect(url_for('MyMedicines'))
        elif user.user_type == 'patient':
            flash("Welcome, patient!", "success")
            return redirect(url_for('Upcomapp'))
        elif user.user_type == 'nurse':
            flash("Welcome, nurse!", "success")
            return redirect(url_for('PatientRecords'))
        else:
            flash("Unexpected error: Invalid user type!", "error")
            return redirect(url_for('login'))

    return render_template('login.html')

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

#route for the Upcom Page
@app.route('/UpcomingApp')
def Upcomingapp():
   return render_template('Upcomapp.html')

#route for the Mymedicines Page
@app.route('/MyMedinces')
def MyMmedinces():
   return render_template('MyMmedinces.html')

#route for the Patient Records Page
@app.route('/PatientRecords')
def PatientRecords():
   return render_template('PatientRecords.html')

if __name__ == '__main__':
    app.run(debug=True)