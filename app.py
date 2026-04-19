from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)

# Security Key for Flash Messages
app.secret_key = 'passport_secret_key_123'

# --- Supabase Database Configuration ---
# Brackets-ah thookittu unga password-ah ippo replace pannittaen
# Palaiya line-ah thookittu idhai podunga
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres.bdcmsuybodbjnciferwq:AathifProject2026@aws-0-ap-south-1.pooler.supabase.com:5432/postgres'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# --- Database Model (Table Structure) ---
class Application(db.Model):
    __tablename__ = 'applications'
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(255), nullable=False)
    dob = db.Column(db.Date, nullable=False)
    gender = db.Column(db.String(20))
    aadhar_no = db.Column(db.String(12), unique=True, nullable=False)
    address = db.Column(db.Text)
    status = db.Column(db.String(50), default='Pending')
    applied_at = db.Column(db.DateTime, default=datetime.utcnow)

# --- HOME PAGE ---
@app.route('/')
def index():
    return render_template('index.html')

# --- APPLICATION SUBMISSION LOGIC ---
@app.route('/apply', methods=['POST'])
def apply():
    if request.method == 'POST':
        try:
            new_app = Application(
                full_name = request.form['full_name'],
                dob = request.form['dob'],
                gender = request.form['gender'],
                aadhar_no = request.form['aadhar_no'],
                address = request.form['address']
            )
            db.session.add(new_app)
            db.session.commit()
            
            return redirect(url_for('success_page', app_id=new_app.id))
            
        except Exception as e:
            db.session.rollback()
            # Handle Duplicate Entry
            if "unique constraint" in str(e).lower() or "aadhar_no" in str(e).lower():
                return """
                <script>
                    alert('Error: This ID is already registered!');
                    window.location.href = '/';
                </script>
                """
            return f"Error Occurred: {str(e)}"

# --- SUCCESS PAGE ---
@app.route('/success/<int:app_id>')
def success_page(app_id):
    return render_template('success.html', id=app_id)

# --- ADMIN DASHBOARD ---
@app.route('/admin')
def admin_dashboard():
    # Fetching all applications using SQLAlchemy
    data = Application.query.order_by(Application.applied_at.desc()).all()
    return render_template('admin.html', applications=data)

# --- UPDATE STATUS (Admin Only) ---
@app.route('/update_status/<int:id>/<string:status>')
def update_status(id, status):
    application = Application.query.get(id)
    if application:
        application.status = status
        db.session.commit()
    return redirect(url_for('admin_dashboard'))

# --- TRACKING LOGIC ---
@app.route('/track', methods=['GET', 'POST'])
def track_status():
    status_data = None
    if request.method == 'POST':
        user_input = request.form.get('app_id') 
        # Search by ID or Aadhaar
        status_data = Application.query.filter(
            (Application.id == user_input) | (Application.aadhar_no == user_input)
        ).first()
    return render_template('track.html', data=status_data)

# --- QUICK TRACK (via URL Prompt) ---
@app.route('/track/<string:app_id>')
def track_by_url(app_id):
    status_data = Application.query.filter(
        (Application.id == app_id) | (Application.aadhar_no == app_id)
    ).first()
    return render_template('track.html', data=status_data)

# --- SERVER START ---
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)