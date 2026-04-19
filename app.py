import os  # Idhu Render port-ah kandupidikka venum
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from urllib.parse import quote

app = Flask(__name__)
app.secret_key = 'passport_secret_key_123'

# --- Supabase Database Configuration ---
raw_password = "aathifproject2026"
safe_password = quote(raw_password)

# Username-la Project ID + Port 6543 + SSL
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
            return f"Error Occurred: {str(e)}"

@app.route('/success/<int:app_id>')
def success_page(app_id):
    return render_template('success.html', id=app_id)

@app.route('/admin')
def admin_dashboard():
    data = Application.query.order_by(Application.applied_at.desc()).all()
    return render_template('admin.html', applications=data)

# --- PORT BINDING FIX ---
if __name__ == '__main__':
    # Render-oda port-ah edukkum, illana default 5000-la run aagum
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)