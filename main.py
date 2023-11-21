from flask import Flask, render_template, request, redirect, url_for, session, jsonify, g
import psycopg2, os, random
from flask_mail import Mail, Message
from dotenv import load_dotenv
from datetime import timedelta, datetime
from flask_login import UserMixin, LoginManager, login_required, login_user, logout_user
from functools import wraps

# Loads .env file
load_dotenv()

# Set up for email
email_username = os.environ.get('EMAIL_USERNAME')
email_password = os.environ.get('EMAIL_PASSWORD_CODE')

# Set up for user authentication
class User(UserMixin):
    def __init__(self, id):
        self.id = id

# Set up for flask server
app = Flask(__name__)

# Set up for flask email service
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USERNAME'] = email_username
app.config['MAIL_PASSWORD'] = email_password
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
mail = Mail(app)

# Set the session duration to 30 days, log's out user after allotted time
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=30)

# Set up log in manager
login_manager = LoginManager()
login_manager.init_app(app)
@login_manager.user_loader
def load_user(user_id):
    return User(user_id)

# Before each Database request, tries to connect to the Database
@app.before_request
def before_request():
    try:
        g.db_conn = psycopg2.connect(
            database=os.getenv('DB_NAME'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            host=os.getenv('DB_HOST'),
            port=os.getenv('DB_PORT')
        )
        g.db_cursor = g.db_conn.cursor()
    except psycopg2.Error as e:
        return f"Database connection error: {e}", 500

# After each Database request, tries to commit changes and close the connection to the Database
@app.teardown_request
def teardown_request(exception=None):
    # If the user calls this, the changes are committed and the connection is closed
    if hasattr(g, 'db_conn'):
        g.db_conn.commit()
        g.db_conn.close()
    # If the users calls this, the database closes without commiting any changes
    if hasattr(g, 'db_cursor'):
        g.db_cursor.close()

# Gets key that is used for encryption in the server
app.secret_key = os.environ.get('SECRET_KEY')

# Log In Page (Default starting page)
@app.route('/', methods=['GET', 'POST'])
def index():
    # If the User has logged in in the last 30 days (time period defined above), the website will be routed to the homepage
    if '_user_id' in session:
        return redirect(url_for('login_homepage'))
    if request.method == 'POST':
        # Get's users input
        db_email = request.form['email_input']
        db_password = request.form['password_input']
        
        # Attempts to find the user in the Database
        g.db_cursor.execute("SELECT * FROM users WHERE email = %s AND password = %s;", (db_email, db_password))
        result = g.db_cursor.fetchone()
        
        # If a User is found, a random 5 digit code is created and sent via email to the inputted users email
        if result:
            random_code = ''.join(str(random.randint(0, 9)) for _ in range(5))
            email_code = " ".join(random_code) 
            session['verification_code'] = random_code
            session['temp_user_id'] = result[0]
            session['completed_step'] = True
            msg = Message('Shield Pass Two-Factor', sender='shield.pass.two.factor@gmail.com', recipients=[db_email])
            msg.html = render_template('emails/email_two_factor.html', email_code=email_code)
            msg.content_subtype = 'html'
            mail.send(msg)
            # Once email is sent, user is redirected to the two factor page
            return redirect(url_for('two_factor'))
        else:
            # If the user is not found in the database or username/password is incorrect, an error message is displayed and the email is put back into the email input
            message = "Invalid username or password. Please try again."
            return render_template('log_in.html', message=message, email=db_email)
     
    # Default starting log in page        
    return render_template('log_in.html')

# Sign Up Page
@app.route('/sign_up', methods=['GET', 'POST'])
def sign_up():
    # If the User has logged in in the last 30 days (time period defined above), the website will be routed to the homepage
    if '_user_id' in session:
        return redirect(url_for('homepage'))
    if request.method == 'POST':
        # Get's users input
        email = request.form['email_input']
        password = request.form['password_input']
        
        # Attempts to find the user in the Database
        g.db_cursor.execute("SELECT * FROM users WHERE email=%s;", (email,))
        user = g.db_cursor.fetchone()
        
        # If the user does not exist, creates a user and creates a random 5 digit code and sends it via email to the inputted users email
        if user is None:
            g.db_cursor.execute('INSERT INTO users (email, password) VALUES (%s, %s);', (email, password))
            g.db_conn.commit()
            g.db_cursor.execute('SELECT * FROM users WHERE email = %s AND password = %s;', (email, password))
            result = g.db_cursor.fetchone()
            random_code = ''.join(str(random.randint(0, 9)) for _ in range(5))
            email_code = " ".join(random_code) 
            session['verification_code'] = random_code
            session['temp_user_id'] = result[0]
            session['completed_step'] = True
            msg = Message('Shield Pass Two-Factor', sender='shield.pass.two.factor@gmail.com', recipients=[email])
            msg.html = render_template('emails/email_two_factor.html', email_code=email_code)
            msg.content_subtype = 'html'
            mail.send(msg)
            # Once email is sent, user is redirected to the two factor page
            return redirect(url_for('two_factor'))
        else:
            # If the user already exists in the database, an error message is displayed and the email is put back into the email input
            message = "Email already in use"
            
        return render_template('sign_up.html', message=message, email=email)
    
     # Default starting sign up page
    return render_template('sign_up.html')

# Two Factore Page
@app.route('/two_factor', methods=['GET', 'POST'])
def two_factor():
    if request.method == 'POST':
        # Get's users input
        input0 = request.form['input0']
        input1 = request.form['input1']
        input2 = request.form['input2']
        input3 = request.form['input3']
        input4 = request.form['input4']
        
        # Makes sure that the user has gone through the log in page or sign up page
        stored_code = session.get('verification_code')
        
        # If the code is correct according to the locally stored code, user can log in
        if (input0 == stored_code[0] and input1 == stored_code[1] and input2 == stored_code[2] and input3 == stored_code[3] and input4 == stored_code[4]):
            user_id = session['temp_user_id']
            
            # Log's in User
            user = User(user_id)
            login_user(user)
            
            # User is redirected to the login homepage
            return redirect(url_for('login_homepage'))
        else:
            # If the inputted code is not match the stored one, an error message is displayed and the input's are placed back
            message = "Code does not match"
        
        return render_template('enter_two_factor.html', message=message, input0=input0, input1=input1, input2=input2, input3=input3, input4=input4)
   
    # Default starting two factor page
    return render_template('enter_two_factor.html')

# Reset Password Page
@app.route('/reset_password', methods=['GET', 'POST'])
def reset_password():
    if request.method == 'POST':
        # Get's users input
        email = request.form['email_input']
        
        # Attempts to find the user in the Database
        g.db_cursor.execute("SELECT * FROM users WHERE email=%s;", (email,))
        user = g.db_cursor.fetchone()
        
        # If the user does exist, sends an email link to reset the password
        if user is not None:
            msg = Message('Shield Pass Reset Password', sender='shield.pass.two.factor@gmail.com', recipients=[email])
            # Link directs user to the new password page
            email_msg = f'http://127.0.0.1:5000/new_password?email={email}'
            msg.html = render_template('emails/email_send_email.html', email_link=email_msg)
            msg.content_subtype = 'html'
            mail.send(msg)
            
            # User is redirected to the sent password page, which is just text. The user must go to their email
            return redirect(url_for('sent_password'))
        else:
            # If the email is not found in the Database, an error message is displayed and the email is put back into the email input
            message = "Email not in use"
        
        return render_template('reset_password.html', message=message, email=email)
    
    # Default starting reset password page
    return render_template('reset_password.html')

# New Password Page
@app.route('/new_password', methods=['GET', 'POST'])
def new_password():
    # Get's users email from the link
    email = request.args.get('email')
    
    if request.method == 'POST':
        # Get's users input
        password = request.form['password_input']
        email = request.form['email']
        
        # Updates the users password
        g.db_cursor.execute('UPDATE users SET password = %s WHERE email = %s;', (password, email))
        g.db_conn.commit()
        
        # After resetting the password, redirects the user to the log in page
        return redirect(url_for('index'))
    
    # Default starting new password page    
    return render_template('new_password.html', email=email)

# Sent Password Page
@app.route('/sent_password')
def sent_password():
    # Default starting sent password page (Only text)
    return render_template('sent_password.html')

# Homepage (Login's) Page, requires the user to be logged in 
@app.route('/login_homepage', methods=['GET', 'POST'])
@login_required
def login_homepage():
    # Get's the user id in the session
    user_id = session.get('_user_id')
    
    if request.method == 'POST':
        # Get's users input
        website = request.form['new-website']
        email = request.form['new-email']
        username = request.form['new-username']
        password = request.form['new-password']
        
        # Inserts a login into the database with the users input
        g.db_cursor.execute('INSERT INTO login (uid, website, email, username, password) VALUES (%s, %s, %s, %s, %s);', (user_id, website, email, username, password))
        g.db_conn.commit()
        
        # Refreshes page
        return redirect(url_for('login_homepage'))
    
    # If statement that inplements a filter system with different button
    
    # Displays the logins by the number of uses stored in the database (number of uses added each time you view a password)
    if request.args.get('buttonName') == 'Popular':
        g.db_cursor.execute("SELECT lid, company, strength FROM login WHERE uid = %s ORDER BY num_of_uses DESC;", (user_id,))
        record = g.db_cursor.fetchall()
        sql_table = [(item[0], item[1], item[2]) for item in record]
        return jsonify(sql_table)
    # Displays the logins alphabetically, starting with A and going to Z
    elif request.args.get('buttonName') == 'A-Z':
        g.db_cursor.execute("SELECT lid, company, strength FROM login WHERE uid = %s ORDER BY company;", (user_id,))
        record = g.db_cursor.fetchall()
        sql_table = [(item[0], item[1], item[2]) for item in record]
        return jsonify(sql_table)
    # Displays the logins alphabetically, starting with Z and going to A
    elif request.args.get('buttonName') == 'Z-A':
        g.db_cursor.execute("SELECT lid, company, strength FROM login WHERE uid = %s ORDER BY company DESC;", (user_id,))
        record = g.db_cursor.fetchall()
        sql_table = [(item[0], item[1], item[2]) for item in record]
        return jsonify(sql_table)
    # Displays the logins by the oldest updated time, where updated time is any change in the database for a login
    elif request.args.get('buttonName') == 'Oldest':
        g.db_cursor.execute("SELECT lid, company, strength FROM login WHERE uid = %s ORDER BY updated_at;", (user_id,))
        record = g.db_cursor.fetchall()
        sql_table = [(item[0], item[1], item[2]) for item in record]
        return jsonify(sql_table)
    # Displays the logins by the most recently updated time, where updated time is any change in the database for a login
    elif request.args.get('buttonName') == 'Newest':
        g.db_cursor.execute("SELECT lid, company, strength FROM login WHERE uid = %s ORDER BY updated_at DESC;", (user_id,))
        record = g.db_cursor.fetchall()
        sql_table = [(item[0], item[1], item[2]) for item in record]
        return jsonify(sql_table)
    # Displays the logins by the weakest password
    elif request.args.get('buttonName') == 'Weakest':
        g.db_cursor.execute("SELECT lid, company, strength FROM login WHERE uid = %s ORDER BY strength;", (user_id,))
        record = g.db_cursor.fetchall()
        sql_table = [(item[0], item[1], item[2]) for item in record]
        return jsonify(sql_table)
    # Default: Displays logins alphabetically, starting with A and going to Z
    else:
        g.db_cursor.execute("SELECT lid, company, strength FROM login WHERE uid = %s ORDER BY company;", (user_id,))
        record = g.db_cursor.fetchall()
        ids = [records[0] for records in record]
        sql_table = [(item[1], item[2]) for item in record]
        return render_template('login_homepage.html', sql_table=zip(ids, sql_table))

# Generator Page
# This page generates a secure password with several varying options, requires the user to be logged in 
@app.route('/generator')
@login_required
def generator():
    return render_template('generator.html')

# Update Row Operation
@app.route('/update_row/<int:row_id>', methods=['PUT'])
# Parameter is a row id
def update_row(row_id):
    if request.method == 'PUT':
        try:
            # Updates the number of uses by 1
            g.db_cursor.execute("UPDATE login SET num_of_uses = num_of_uses + 1 WHERE lid = %s", (row_id,))
            g.db_conn.commit()
            return jsonify({'message': 'Row updated successfully.'})
        except Exception as e:
            return jsonify({'error': str(e)}), 500

# Get Login Info Operation
@app.route('/get_login_info/<int:login_id>', methods=['GET'])
# Parameter is a login id
def get_login_info(login_id):
    # Attempts to find the login information in the Database
    g.db_cursor.execute("SELECT website, email, username, password FROM login WHERE lid = %s;", (login_id,))
    record = g.db_cursor.fetchone()
    if record:
        return jsonify({'website': record[0], 'email': record[1], 'username': record[2], 'password': record[3]})
    else:
        return jsonify({'error': 'Login information not found'})
    
# Save Changes Operation  
@app.route('/save_changes', methods=['POST'])
def save_changes():
    if request.method == 'POST':
        data = request.get_json()
        
        # Get's users input
        lid = data['lid']
        website = data['website']
        email = data['email']
        username = data['username']
        password = data['password']
        
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Updates the login information in the Database
        g.db_cursor.execute("UPDATE login SET email = %s, username = %s, password = %s, website = %s, updated_at = %s WHERE lid = %s", (email, username, password, website, current_time, lid))
        g.db_conn.commit()

        return jsonify({'message': 'Data updated in the database.'})

# Save Changes Notes Operation
@app.route('/save_changes_notes', methods=['POST'])
def save_changes_notes():
    if request.method == 'POST':
        data = request.get_json()
        
        # Get's users input
        nid = data['nid']
        note_name = data['note_name']
        note = data['note']
        
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Updates the note information in the Database
        g.db_cursor.execute("UPDATE notes SET note_name = %s, note = %s, updated_at = %s WHERE nid = %s", (note_name, note, current_time, nid))
        g.db_conn.commit()

        return jsonify({'message': 'Data updated in the database.'})

# Delete Row Operation
@app.route('/delete_row', methods=['POST'])
def delete_row():
    data = request.get_json()
    if data and 'row_id' in data:
        # Get's row_id from input
        row_id = data['row_id']
        
        # Deletes login from Database
        g.db_cursor.execute("DELETE FROM login WHERE lid = %s", (row_id,))
        g.db_conn.commit()
        
        return jsonify({'message': 'Row deleted successfully.'})
    else:
        return jsonify({'message': 'Invalid data format.'}), 400

# Delete Row Note Operation
@app.route('/delete_row_note', methods=['POST'])
def delete_row_note():
    data = request.get_json()
    if data and 'row_id' in data:
        # Get's row_id from input
        row_id = data['row_id']
        
        # Deletes note from Database
        g.db_cursor.execute("DELETE FROM notes WHERE nid = %s", (row_id,))
        g.db_conn.commit()
        return jsonify({'message': 'Row deleted successfully.'})
    else:
        return jsonify({'message': 'Invalid data format.'}), 400

# Search Operation
@app.route('/search', methods=['POST'])
def search():
    data = request.get_json()
    
    # Get's input from the search input
    query = data['query']

    # Get's all logins that contain the characters in the query. The search is a substring so when searching 'ma', 'amazon' will show up
    g.db_cursor.execute("SELECT lid, company FROM login WHERE company ILIKE %s ORDER BY company;", ('%' + query + '%',))
    record = g.db_cursor.fetchall()
    sql_table = [(item[0], item[1]) for item in record]

    return jsonify(sql_table)

# Search Notes Operation
@app.route('/search_notes', methods=['POST'])
def search_notes():
    data = request.get_json()
    
    # Get's input from the search input
    query = data['query']

    # Get's all notes that contain the characters in the query. The search is a substring so when searching 'SN', 'SSN' will show up
    g.db_cursor.execute("SELECT nid, note_name FROM notes WHERE note_name ILIKE %s ORDER BY note_name;", ('%' + query + '%',))
    record = g.db_cursor.fetchall()
    sql_table = [(item[0], item[1]) for item in record]

    return jsonify(sql_table)

# Homepage (Notes) Page, requires the user to be logged in 
@app.route('/notes_homepage', methods=['GET', 'POST'])
@login_required
def notes_homepage():
    # Get's the user id in the session
    user_id = session.get('_user_id')
    
    if request.method == 'POST':
        # Get's users input
        note_name = request.form['note-name-add']
        note = request.form['note-add']
        
        # Inserts a note into the database with the users input
        g.db_cursor.execute('INSERT INTO notes (uid, note_name, note) VALUES (%s, %s, %s);', (user_id, note_name, note))
        g.db_conn.commit()
        
        # Refreshes page
        return redirect(url_for('notes_homepage'))
    
    # Displays notes alphabetically, starting with A and going to Z
    g.db_cursor.execute("SELECT nid, note_name FROM notes WHERE uid = %s ORDER BY note_name;", (user_id,))
    record = g.db_cursor.fetchall()
    ids = [records[0] for records in record]
    sql_table = [item[1] for item in record]
    return render_template('notes_homepage.html', sql_table=zip(ids, sql_table))

# Update Row Operation
@app.route('/get_note_info/<int:note_id>', methods=['GET'])
# Parameter is a note id
def get_note_info(note_id):
    # Attempts to find the note information in the Database
    g.db_cursor.execute("SELECT note_name, note FROM notes WHERE nid = %s;", (note_id,))
    record = g.db_cursor.fetchone()
    if record:
        return jsonify({'note_name': record[0], 'note': record[1]})
    else:
        return jsonify({'error': 'Login information not found'})

# Settings Page, requires the user to be logged in
@app.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    # Get's the user id in the session
    user_id = session.get('_user_id')
    
    # Gets the current Users email and password from the Database
    g.db_cursor.execute("SELECT email, password FROM users WHERE uid = %s;", (user_id,))
    record = g.db_cursor.fetchone()
    email = record[0]
    password = record[1]
    
    if request.method =='POST':
        # Get's users input
        new_email = request.form['email']
        
        # Gets the current Users email and password from the Database
        g.db_cursor.execute("SELECT email, password FROM users WHERE email = %s;", (new_email,))
        result = g.db_cursor.fetchone()
        
        # Put's the email and password into the inputs for the user to view
        if result[0] == new_email:
            message = ""
            return render_template('settings.html', email=email, password=password, message=message)
        # Put's the email and password into the inputs for the user to view and put's an error message because the user inputted an email that already exists
        elif result:
            message = "Email already exists. Please try again."
            return render_template('settings.html', email=email, password=password, message=message)
        # Updates the current user's email and refreshes the page
        else:
            g.db_cursor.execute("UPDATE users SET email = %s WHERE uid = %s", (new_email, user_id))
            g.db_conn.commit()
            
            return render_template('settings.html', email=new_email, password=password)
    
    # Default starting settings page  
    return render_template('settings.html', email=email, password=password)

# Update Row Operation
@app.route('/delete_user', methods=['POST'])
def delete_user_route():
    # Get's the user id in the session
    user_id = session.get('_user_id')

    # Does the delete_user function when user_id is present
    if user_id is not None:
        delete_user(user_id)

    return jsonify({'success': 'User deleted successfully!'})

# Function that deletes the user (cascades to delete all logins and notes that are linked to the user)
def delete_user(uid):
    g.db_cursor.execute('DELETE FROM users WHERE UID = %s;', (uid,))
    g.db_conn.commit()

# Logout Operation, requires the user to be logged in
@app.route('/logout')
@login_required
def logout():
    # Log's the user out of the 
    logout_user()
    return redirect(url_for('index'))

# Starts the flask server
# Commented out line enables https and self authenticates (would need to be replaced with a real certification)
if __name__ == '__main__':
    app.debug = True
    ip = '127.0.0.1'
    # For https: ssl_context='adhoc'
    app.run(host=ip)