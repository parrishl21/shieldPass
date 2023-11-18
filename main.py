# TODO: Make it so the user has to do the two factor to be logged in

from flask import Flask, render_template, request, redirect, url_for, session, jsonify, g
import psycopg2, os, random
from flask_mail import Mail, Message
from dotenv import load_dotenv
from datetime import timedelta, datetime
from flask_login import UserMixin, LoginManager, login_required, login_user, logout_user
from functools import wraps

# Set up for email
load_dotenv()
email_username = os.environ.get('EMAIL_USERNAME')
email_password = os.environ.get('EMAIL_PASSWORD_CODE')

# Set up for user authentication
class User(UserMixin):
    def __init__(self, id):
        self.id = id

# Set up for flask server
app = Flask(__name__)
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USERNAME'] = email_username
app.config['MAIL_PASSWORD'] = email_password
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
# Set the session duration to 30 days
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=30)
mail = Mail(app)

# Set up log in manager
login_manager = LoginManager()
login_manager.init_app(app)
@login_manager.user_loader
def load_user(user_id):
    return User(user_id)

def check_completion(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not session.get('completed_step'):
            return redirect(url_for('index'))
        return func(*args, **kwargs)
    return wrapper

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

@app.teardown_request
def teardown_request(exception=None):
    if hasattr(g, 'db_conn'):
        g.db_conn.commit()
        g.db_conn.close()
    if hasattr(g, 'db_cursor'):
        g.db_cursor.close()

app.secret_key = os.environ.get('SECRET_KEY')

@app.route('/', methods=['GET', 'POST'])
def index():
    if '_user_id' in session:
        return redirect(url_for('login_homepage'))
    if request.method == 'POST':
        db_email = request.form['email_input']
        db_password = request.form['password_input']
        
        g.db_cursor.execute("SELECT * FROM users WHERE email = %s AND password = %s;", (db_email, db_password))
        result = g.db_cursor.fetchone()
        
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
            return redirect(url_for('two_factor'))
        else:
            message = "Invalid username or password. Please try again."
            return render_template('log_in.html', message=message, email=db_email)
            
    return render_template('log_in.html')

@app.route('/sign_up', methods=['GET', 'POST'])
def sign_up():
    if '_user_id' in session:
        return redirect(url_for('homepage'))
    if request.method == 'POST':
        email = request.form['email_input']
        password = request.form['password_input']
        
        g.db_cursor.execute("SELECT * FROM users WHERE email=%s;", (email,))
        user = g.db_cursor.fetchone()
        
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
            return redirect(url_for('two_factor'))
        else:
            message = "Email already in use"
            
        return render_template('sign_up.html', message=message, email=email)
        
    return render_template('sign_up.html')

@app.route('/two_factor', methods=['GET', 'POST'])
@check_completion
def two_factor():
    if request.method == 'POST':
        input0 = request.form['input0']
        input1 = request.form['input1']
        input2 = request.form['input2']
        input3 = request.form['input3']
        input4 = request.form['input4']
        stored_code = session.get('verification_code')
        if (input0 == stored_code[0] and input1 == stored_code[1] and input2 == stored_code[2] and input3 == stored_code[3] and input4 == stored_code[4]):
            user_id = session['temp_user_id']
            user = User(user_id)
            login_user(user)
            return redirect(url_for('login_homepage'))
        else:
            message = "Code does not match"
        
        return render_template('enter_two_factor.html', message=message, input0=input0, input1=input1, input2=input2, input3=input3, input4=input4)
    
    return render_template('enter_two_factor.html')

@app.route('/reset_password', methods=['GET', 'POST'])
def reset_password():
    if request.method == 'POST':
        email = request.form['email_input']
        
        g.db_cursor.execute("SELECT * FROM users WHERE email=%s;", (email,))
        user = g.db_cursor.fetchone()
        
        if user is not None:
            msg = Message('Shield Pass Reset Password', sender='shield.pass.two.factor@gmail.com', recipients=[email])
            email_msg = f'http://127.0.0.1:5000/new_password?email={email}'
            msg.html = render_template('emails/email_send_email.html', email_link=email_msg)
            msg.content_subtype = 'html'
            mail.send(msg)
            
            return redirect(url_for('sent_password'))
        else:
            message = "Email not in use"
        
        return render_template('reset_password.html', message=message, email=email)
    
    return render_template('reset_password.html')

@app.route('/new_password', methods=['GET', 'POST'])
def new_password():
    email = request.args.get('email')
    
    if request.method == 'POST':
        password = request.form['password_input']
        email = request.form['email']
        
        g.db_cursor.execute('UPDATE users SET password = %s WHERE email = %s;', (password, email))
        g.db_conn.commit()
        
        return redirect(url_for('index'))
        
    return render_template('new_password.html', email=email)

@app.route('/sent_password')
def sent_password():
    return render_template('sent_password.html')

@app.route('/login_homepage', methods=['GET', 'POST'])
@login_required
def login_homepage():
    user_id = session.get('_user_id')
    if request.method == 'POST':
        website = request.form['new-website']
        email = request.form['new-email']
        username = request.form['new-username']
        password = request.form['new-password']
        
        g.db_cursor.execute('INSERT INTO login (uid, website, email, username, password) VALUES (%s, %s, %s, %s, %s);', (user_id, website, email, username, password))
        g.db_conn.commit()
        return redirect(url_for('login_homepage'))
    
    if request.args.get('buttonName') == 'Popular':
        g.db_cursor.execute("SELECT lid, company, strength FROM login WHERE uid = %s ORDER BY num_of_uses DESC;", (user_id,))
        record = g.db_cursor.fetchall()
        sql_table = [(item[0], item[1], item[2]) for item in record]
        return jsonify(sql_table)
    elif request.args.get('buttonName') == 'A-Z':
        g.db_cursor.execute("SELECT lid, company, strength FROM login WHERE uid = %s ORDER BY company;", (user_id,))
        record = g.db_cursor.fetchall()
        sql_table = [(item[0], item[1], item[2]) for item in record]
        return jsonify(sql_table)
    elif request.args.get('buttonName') == 'Z-A':
        g.db_cursor.execute("SELECT lid, company, strength FROM login WHERE uid = %s ORDER BY company DESC;", (user_id,))
        record = g.db_cursor.fetchall()
        sql_table = [(item[0], item[1], item[2]) for item in record]
        return jsonify(sql_table)
    elif request.args.get('buttonName') == 'Oldest':
        g.db_cursor.execute("SELECT lid, company, strength FROM login WHERE uid = %s ORDER BY updated_at;", (user_id,))
        record = g.db_cursor.fetchall()
        sql_table = [(item[0], item[1], item[2]) for item in record]
        return jsonify(sql_table)
    elif request.args.get('buttonName') == 'Newest':
        g.db_cursor.execute("SELECT lid, company, strength FROM login WHERE uid = %s ORDER BY updated_at DESC;", (user_id,))
        record = g.db_cursor.fetchall()
        sql_table = [(item[0], item[1], item[2]) for item in record]
        return jsonify(sql_table)
    elif request.args.get('buttonName') == 'Weakest':
        g.db_cursor.execute("SELECT lid, company, strength FROM login WHERE uid = %s ORDER BY strength;", (user_id,))
        record = g.db_cursor.fetchall()
        sql_table = [(item[0], item[1], item[2]) for item in record]
        return jsonify(sql_table)
    else:
        g.db_cursor.execute("SELECT lid, company, strength FROM login WHERE uid = %s ORDER BY company;", (user_id,))
        record = g.db_cursor.fetchall()
        ids = [records[0] for records in record]
        sql_table = [(item[1], item[2]) for item in record]
        return render_template('login_homepage.html', sql_table=zip(ids, sql_table))

@app.route('/generator')
@login_required
def generator():
    return render_template('generator.html')

@app.route('/update_row/<int:row_id>', methods=['PUT'])
def update_row(row_id):
    if request.method == 'PUT':
        try:
            g.db_cursor.execute("UPDATE login SET num_of_uses = num_of_uses + 1 WHERE lid = %s", (row_id,))
            g.db_conn.commit()
            return jsonify({'message': 'Row updated successfully.'})
        except Exception as e:
            return jsonify({'error': str(e)}), 500

@app.route('/get_login_info/<int:login_id>', methods=['GET'])
def get_login_info(login_id):
    g.db_cursor.execute("SELECT website, email, username, password FROM login WHERE lid = %s;", (login_id,))
    record = g.db_cursor.fetchone()
    if record:
        return jsonify({'website': record[0], 'email': record[1], 'username': record[2], 'password': record[3]})
    else:
        return jsonify({'error': 'Login information not found'})
    
@app.route('/save_changes', methods=['POST'])
def save_changes():
    if request.method == 'POST':
        data = request.get_json()
        
        lid = data['lid']
        website = data['website']
        email = data['email']
        username = data['username']
        password = data['password']
        
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        g.db_cursor.execute("UPDATE login SET email = %s, username = %s, password = %s, website = %s, updated_at = %s WHERE lid = %s", (email, username, password, website, current_time, lid))
        g.db_conn.commit()

        return jsonify({'message': 'Data updated in the database.'})
    
@app.route('/save_changes_notes', methods=['POST'])
def save_changes_notes():
    if request.method == 'POST':
        data = request.get_json()
        
        nid = data['nid']
        note_name = data['note_name']
        note = data['note']
        
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        g.db_cursor.execute("UPDATE notes SET note_name = %s, note = %s, updated_at = %s WHERE nid = %s", (note_name, note, current_time, nid))
        g.db_conn.commit()

        return jsonify({'message': 'Data updated in the database.'})
    
@app.route('/delete_row', methods=['POST'])
def delete_row():
    data = request.get_json()
    if data and 'row_id' in data:
        row_id = data['row_id']
        g.db_cursor.execute("DELETE FROM login WHERE lid = %s", (row_id,))
        g.db_conn.commit()
        return jsonify({'message': 'Row deleted successfully.'})
    else:
        return jsonify({'message': 'Invalid data format.'}), 400
    
@app.route('/delete_row_note', methods=['POST'])
def delete_row_note():
    data = request.get_json()
    if data and 'row_id' in data:
        row_id = data['row_id']
        g.db_cursor.execute("DELETE FROM notes WHERE nid = %s", (row_id,))
        g.db_conn.commit()
        return jsonify({'message': 'Row deleted successfully.'})
    else:
        return jsonify({'message': 'Invalid data format.'}), 400
    
@app.route('/search', methods=['POST'])
def search():
    data = request.get_json()
    query = data['query']

    g.db_cursor.execute("SELECT lid, company FROM login WHERE company ILIKE %s ORDER BY company;", ('%' + query + '%',))
    record = g.db_cursor.fetchall()
    sql_table = [(item[0], item[1]) for item in record]

    return jsonify(sql_table)

@app.route('/search_notes', methods=['POST'])
def search_notes():
    data = request.get_json()
    query = data['query']

    g.db_cursor.execute("SELECT nid, note_name FROM notes WHERE note_name ILIKE %s ORDER BY note_name;", ('%' + query + '%',))
    record = g.db_cursor.fetchall()
    sql_table = [(item[0], item[1]) for item in record]

    return jsonify(sql_table)

@app.route('/notes_homepage', methods=['GET', 'POST'])
@login_required
def notes_homepage():
    user_id = session.get('_user_id')
    
    if request.method == 'POST':
        note_name = request.form['note-name-add']
        note = request.form['note-add']
        
        g.db_cursor.execute('INSERT INTO notes (uid, note_name, note) VALUES (%s, %s, %s);', (user_id, note_name, note))
        g.db_conn.commit()
        return redirect(url_for('notes_homepage'))
    
    g.db_cursor.execute("SELECT nid, note_name FROM notes WHERE uid = %s ORDER BY note_name;", (user_id,))
    record = g.db_cursor.fetchall()
    ids = [records[0] for records in record]
    sql_table = [item[1] for item in record]
    return render_template('notes_homepage.html', sql_table=zip(ids, sql_table))

@app.route('/get_note_info/<int:note_id>', methods=['GET'])
def get_note_info(note_id):
    g.db_cursor.execute("SELECT note_name, note FROM notes WHERE nid = %s;", (note_id,))
    record = g.db_cursor.fetchone()
    if record:
        return jsonify({'note_name': record[0], 'note': record[1]})
    else:
        return jsonify({'error': 'Login information not found'})

@app.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    user_id = session.get('_user_id')
    g.db_cursor.execute("SELECT email, password FROM users WHERE uid = %s;", (user_id,))
    record = g.db_cursor.fetchone()
    
    email = record[0]
    password = record[1]
    
    if request.method =='POST':
        new_email = request.form['email']
        g.db_cursor.execute("SELECT email, password FROM users WHERE email = %s;", (new_email,))
        result = g.db_cursor.fetchone()
        
        if result[0] == new_email:
            message = ""
            return render_template('settings.html', email=email, password=password, message=message)
        elif result:
            message = "Email already exists. Please try again."
            return render_template('settings.html', email=email, password=password, message=message)
        else:
            g.db_cursor.execute("UPDATE users SET email = %s WHERE uid = %s", (new_email, user_id))
            g.db_conn.commit()
            
            return render_template('settings.html', email=new_email, password=password)
    
    return render_template('settings.html', email=email, password=password)

@app.route('/delete_user', methods=['POST'])
def delete_user_route():
    user_id = session.get('_user_id')

    if user_id is not None:
        delete_user(user_id)

    return jsonify({'success': 'User deleted successfully!'})

def delete_user(uid):
    g.db_cursor.execute('DELETE FROM users WHERE UID = %s;', (uid,))
    g.db_conn.commit()

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.debug = True
    ip = '127.0.0.1'
    # For https: ssl_context='adhoc'
    app.run(host=ip)