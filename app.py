from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from urllib.parse import quote

app = Flask(__name__)
app.secret_key = 'passport_secret_key_123'

# --- Supabase Database Configuration (PERMANENT FIX) ---
# 1. Project ID: bdcmsuybodbjnciferwq
# 2. Password: aathifproject2026
# 3. Connection: Pooler (IPv4 compatible)
# 4. Port: 6543 (Mandatory for Session Pooling)

raw_password = "aathifproject2026"
safe_password = quote(raw_password)

# Username-la Project ID sethurukkaen (Tenant ID issue-ku idhu thaan fix)
# Port 6543 potturukkaen (Networking unreachable issue-ku idhu thaan fix)
app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://postgres.bdcmsuybodbjnciferwq:{safe_password}@aws-0-ap-south-1.pooler.supabase.com:6543/postgres?sslmode=require'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# --- Database Model ---
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

# --- ROUTES ---

@app.route('/')
def index():
    return render_template('index.html')

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
            # Error-ah theriyaama alert panna logic
            if "unique" in str(e).lower() or "aadhar_no" in str(e).lower():
                return "<script>alert('Error: This Aadhaar is already registered!'); window.location.href='/';</script>"
            return f"Error Occurred: {str(e)}"

@app.route('/success/<int:app_id>')
def success_page(app_id):
    return render_template('success.html', id=app_id)

@app.route('/admin')
def admin_dashboard():
    data = Application.query.order_by(Application.applied_at.desc()).all()
    return render_template('admin.html', applications=data)

@app.route('/update_status/<int:id>/<string:status>')
def update_status(id, status):
    application = Application.query.get(id)
    if application:
        application.status = status
        db.session.commit()
    return redirect(url_for('admin_dashboard'))

@app.route('/track', methods=['GET', 'POST'])
def track_status():
    status_data = None
    if request.method == 'POST':
        user_input = request.form.get('app_id') 
        status_data = Application.query.filter(
            (Application.id == user_input) | (Application.aadhar_no == user_input)
        ).first()
    return render_template('track.html', data=status_data)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)