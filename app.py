from flask import Flask, render_template, request, redirect, url_for, flash
from flask_mysqldb import MySQL

app = Flask(__name__)

# Security Key for Flash Messages (Project-ku romba mukkiyam)
app.secret_key = 'passport_secret_key_123'

# --- Database Connection Configuration ---
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = '' # Unga XAMPP password inga podunga
app.config['MYSQL_DB'] = 'passport_db'

mysql = MySQL(app)

# --- HOME PAGE (The Animated Portal) ---
@app.route('/')
def index():
    return render_template('index.html')

# --- APPLICATION SUBMISSION LOGIC ---
@app.route('/apply', methods=['POST'])
def apply():
    if request.method == 'POST':
        full_name = request.form['full_name']
        dob = request.form['dob']
        gender = request.form['gender']
        # Redacting sensitive government ID in logs for security
        aadhar_no = request.form['aadhar_no'] 
        address = request.form['address']

        cur = mysql.connection.cursor()
        try:
            # SQL Query to insert data safely
            cur.execute("INSERT INTO applications (full_name, dob, gender, aadhar_no, address) VALUES (%s, %s, %s, %s, %s)", 
                        (full_name, dob, gender, aadhar_no, address))
            mysql.connection.commit()
            new_id = cur.lastrowid 
            cur.close()
            
            # Application ID-oda success page-ku move aaguvom
            return redirect(url_for('success_page', app_id=new_id))
            
        except Exception as e:
            # Handle Duplicate Entry (Error 1062)
            if "1062" in str(e):
                return """
                <script>
                    alert('Error: [Aadhaar Redacted] IS ALREADY REGISTERED');
                    window.location.href = '/';
                </script>
                """
            return f"Error Occurred: {str(e)}"

# --- SUCCESS PAGE ---
@app.route('/success/<int:app_id>')
def success_page(app_id):
    # Rendering success.html with the new Application ID
    return render_template('success.html', id=app_id)

# --- ADMIN DASHBOARD ---
@app.route('/admin')
def admin_dashboard():
    cur = mysql.connection.cursor()
    cur.execute("SELECT id, full_name, dob, gender, status, applied_at FROM applications ORDER BY applied_at DESC")
    data = cur.fetchall()
    cur.close()
    return render_template('admin.html', applications=data)

# --- UPDATE STATUS (Admin Only) ---
@app.route('/update_status/<int:id>/<string:status>')
def update_status(id, status):
    cur = mysql.connection.cursor()
    cur.execute("UPDATE applications SET status=%s WHERE id=%s", (status, id))
    mysql.connection.commit()
    cur.close()
    return redirect(url_for('admin_dashboard'))

# --- TRACKING LOGIC (Main Dashboard & Search) ---
@app.route('/track', methods=['GET', 'POST'])
def track_status():
    status_data = None
    if request.method == 'POST':
        user_input = request.form.get('app_id') 
        cur = mysql.connection.cursor()
        # Searching via ID or Government ID
        cur.execute("SELECT full_name, status, applied_at FROM applications WHERE id = %s OR aadhar_no = %s", (user_input, user_input))
        status_data = cur.fetchone()
        cur.close()
    return render_template('track.html', data=status_data)

# --- QUICK TRACK (via URL Prompt) ---
@app.route('/track/<string:app_id>')
def track_by_url(app_id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT full_name, status, applied_at FROM applications WHERE id = %s OR aadhar_no = %s", (app_id, app_id))
    status_data = cur.fetchone()
    cur.close()
    return render_template('track.html', data=status_data)

# --- SERVER START ---
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)