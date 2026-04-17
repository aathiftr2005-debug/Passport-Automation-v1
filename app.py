from flask import Flask, render_template, request, redirect, url_for
from flask_mysqldb import MySQL

app = Flask(__name__)

# Database Connection
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'passport_db'

mysql = MySQL(app)

@app.route('/')
def index():
    return render_template('index.html')

# --- APPLICATION SUBMISSION ---
@app.route('/apply', methods=['POST'])
def apply():
    if request.method == 'POST':
        full_name = request.form['full_name']
        dob = request.form['dob']
        gender = request.form['gender']
        aadhar_no = request.form['aadhar_no']
        address = request.form['address']

        cur = mysql.connection.cursor()
        try:
            cur.execute("INSERT INTO applications (full_name, dob, gender, aadhar_no, address) VALUES (%s, %s, %s, %s, %s)", 
                        (full_name, dob, gender, aadhar_no, address))
            mysql.connection.commit()
            new_id = cur.lastrowid 
            cur.close()
            return redirect(url_for('success_page', app_id=new_id))
        except Exception as e:
            if "1062" in str(e): # Duplicate Aadhar/Entry Check
                return """
                <script>
                    alert('Error: SORRY THIS ADHAR CARD IS ALREADY REGISTERED');
                    window.location.href = '/';
                </script>
                """
            return f"Error: {str(e)}"

# Success Page
@app.route('/success/<int:app_id>')
def success_page(app_id):
    return render_template('success.html', id=app_id)

# --- ADMIN DASHBOARD ---
@app.route('/admin')
def admin_dashboard():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM applications ORDER BY applied_at DESC")
    data = cur.fetchall()
    cur.close()
    return render_template('admin.html', applications=data)

@app.route('/update_status/<int:id>/<string:status>')
def update_status(id, status):
    cur = mysql.connection.cursor()
    cur.execute("UPDATE applications SET status=%s WHERE id=%s", (status, id))
    mysql.connection.commit()
    cur.close()
    return redirect(url_for('admin_dashboard'))

# --- TRACKING LOGIC (Form Search Page & Aadhar Search) ---
@app.route('/track', methods=['GET', 'POST'])
def track_status():
    status_data = None
    if request.method == 'POST':
        user_input = request.form.get('app_id') # Can be ID or Aadhar
        cur = mysql.connection.cursor()
        # Multi-search: ID moolamavum search pannum, illa Aadhar moolamavum search pannum
        cur.execute("SELECT full_name, status, applied_at FROM applications WHERE id = %s OR aadhar_no = %s", (user_input, user_input))
        status_data = cur.fetchone()
        cur.close()
    return render_template('track.html', data=status_data)

# --- TRACKING LOGIC (Quick Track via URL / Prompt Box) ---
@app.route('/track/<string:app_id>')
def track_by_url(app_id):
    cur = mysql.connection.cursor()
    # Direct URL tracking handles ID or Aadhar
    cur.execute("SELECT full_name, status, applied_at FROM applications WHERE id = %s OR aadhar_no = %s", (app_id, app_id))
    status_data = cur.fetchone()
    cur.close()
    return render_template('track.html', data=status_data)

if __name__ == '__main__':
    app.run(debug=True)