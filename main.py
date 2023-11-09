# TODO: Make it so the user has to do the two factor to be logged in

from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import psycopg2, os, random
from flask_mail import Mail, Message
from dotenv import load_dotenv
from datetime import timedelta, datetime
from flask_login import UserMixin, LoginManager, login_required, login_user, logout_user

# Set up for email
load_dotenv()
email_username = os.environ.get('EMAIL_USERNAME')
email_password = os.environ.get('EMAIL_PASSWORD_CODE')

# Set up for database
conn = psycopg2.connect(
    database='shield_pass',
    user='raywu1990',
    password='test',
    host='127.0.0.1',
    port='5432')
cursor = conn.cursor()

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

login_manager = LoginManager()
login_manager.init_app(app)
@login_manager.user_loader
def load_user(user_id):
    return User(user_id)

app.secret_key = os.environ.get('SECRET_KEY')

@app.route('/', methods=['GET', 'POST'])
def index():
    if '_user_id' in session:
        return redirect(url_for('login_homepage'))
    if request.method == 'POST':
        db_email = request.form['email_input']
        db_password = request.form['password_input']
        
        cursor.execute("SELECT * FROM users WHERE email = %s AND password = %s;", (db_email, db_password))
        result = cursor.fetchone()
        
        if result:
            user_id = result[0]
            user = User(user_id)
            login_user(user)
            random_code = ''.join(str(random.randint(0, 9)) for _ in range(5))
            email_code = " ".join(random_code) 
            session['verification_code'] = random_code
            msg = Message('Shield Pass Two-Factor', sender='shield.pass.two.factor@gmail.com', recipients=[db_email])
            # msg.body = f'Your sign-in code: {random_code}'
            # msg.body = "Authenticate Your Account To make sure you’re account is secure, you’ll need to verify your identity. Please enter the code below to access your account 1 2 3 4 5 Thank you for using ShieldPass"
            msg.html = render_template('emails/email_two_factor.html', email_code=email_code)
            msg.content_subtype = 'html'
            mail.send(msg)
            return redirect(url_for('two_factor'))
        else:
            message = "Invalid username or password. Please try again."
            return render_template('log_in.html', message=message)
            
    return render_template('log_in.html')

@app.route('/sign_up', methods=['GET', 'POST'])
def sign_up():
    if '_user_id' in session:
        return redirect(url_for('homepage'))
    if request.method == 'POST':
        email = request.form['email_input']
        password = request.form['password_input']
        
        cursor.execute("SELECT * FROM users WHERE email=%s;", (email,))
        user = cursor.fetchone()
        
        if user is None:
            cursor.execute('INSERT INTO users (email, password) VALUES (%s, %s);', (email, password))
            conn.commit()
            cursor.execute('SELECT * FROM users WHERE email = %s AND password = %s;', (email, password))
            result = cursor.fetchone()
            user_id = result[0]
            user = User(user_id)
            login_user(user)
            return redirect(url_for('two_factor'))
        else:
            message = "Email already in use"
            
        return render_template('sign_up.html', message=message)
        
    return render_template('sign_up.html')

@app.route('/two_factor', methods=['GET', 'POST'])
@login_required
def two_factor():
    if request.method == 'POST':
        input0 = request.form['input0']
        input1 = request.form['input1']
        input2 = request.form['input2']
        input3 = request.form['input3']
        input4 = request.form['input4']
        stored_code = session.get('verification_code')
        if (input0 == stored_code[0] and input1 == stored_code[1] and input2 == stored_code[2] and input3 == stored_code[3] and input4 == stored_code[4]):
            return redirect(url_for('login_homepage'))
        else:
            message = "Code does not match"
        
        return render_template('enter_two_factor.html', message=message)
    
    return render_template('enter_two_factor.html')

@app.route('/reset_password', methods=['GET', 'POST'])
def reset_password():
    if request.method == 'POST':
        email = request.form['email_input']
        
        cursor.execute("SELECT * FROM users WHERE email=%s;", (email,))
        user = cursor.fetchone()
        
        if user is not None:
            msg = Message('Shield Pass Reset Password', sender='shield.pass.two.factor@gmail.com', recipients=[email])
            # msg.body = f'Reset your password here: http://127.0.0.1:5000/new_password?email={email}'
            email_msg = f'http://127.0.0.1:5000/new_password?email={email}'
            msg.html = render_template('emails/email_send_email.html', email_link=email_msg)
            msg.content_subtype = 'html'
            mail.send(msg)
            
            return redirect(url_for('sent_password'))
        else:
            message = "Email not in use"
        
        return render_template('reset_password.html', message=message)
    
    return render_template('reset_password.html')

@app.route('/new_password', methods=['GET', 'POST'])
def new_password():
    email = request.args.get('email')
    
    if request.method == 'POST':
        password = request.form['password_input']
        email = request.form['email']
        
        cursor.execute('UPDATE users SET password = %s WHERE email = %s;', (password, email))
        conn.commit()
        
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
        
        cursor.execute('INSERT INTO login (uid, website, email, username, password) VALUES (%s, %s, %s, %s, %s);', (user_id, website, email, username, password))
        conn.commit()
        return redirect(url_for('login_homepage'))
    
    if request.args.get('buttonName') == 'Popular':
        cursor.execute("SELECT lid, company FROM login WHERE uid = %s ORDER BY num_of_uses DESC;", (user_id,))
        record = cursor.fetchall()
        sql_table = [(item[0], item[1]) for item in record]
        return jsonify(sql_table)
    elif request.args.get('buttonName') == 'A-Z':
        cursor.execute("SELECT lid, company FROM login WHERE uid = %s ORDER BY company;", (user_id,))
        record = cursor.fetchall()
        sql_table = [(item[0], item[1]) for item in record]
        return jsonify(sql_table)
    elif request.args.get('buttonName') == 'Z-A':
        cursor.execute("SELECT lid, company FROM login WHERE uid = %s ORDER BY company DESC;", (user_id,))
        record = cursor.fetchall()
        sql_table = [(item[0], item[1]) for item in record]
        return jsonify(sql_table)
    elif request.args.get('buttonName') == 'Oldest':
        cursor.execute("SELECT lid, company FROM login WHERE uid = %s ORDER BY updated_at;", (user_id,))
        record = cursor.fetchall()
        sql_table = [(item[0], item[1]) for item in record]
        return jsonify(sql_table)
    elif request.args.get('buttonName') == 'Newest':
        cursor.execute("SELECT lid, company FROM login WHERE uid = %s ORDER BY updated_at DESC;", (user_id,))
        record = cursor.fetchall()
        sql_table = [(item[0], item[1]) for item in record]
        return jsonify(sql_table)
    else:
        cursor.execute("SELECT lid, company FROM login WHERE uid = %s ORDER BY company;", (user_id,))
        record = cursor.fetchall()
        ids = [records[0] for records in record]
        sql_table = [(item[1],) for item in record]
        return render_template('login_homepage.html', sql_table=zip(ids, sql_table))

@app.route('/generator')
@login_required
def generator():
    return render_template('generator.html')

@app.route('/update_row/<int:row_id>', methods=['PUT'])
def update_row(row_id):
    if request.method == 'PUT':
        try:
            cursor.execute("UPDATE login SET num_of_uses = num_of_uses + 1 WHERE lid = %s", (row_id,))
            conn.commit()
            return jsonify({'message': 'Row updated successfully.'})
        except Exception as e:
            return jsonify({'error': str(e)}), 500

@app.route('/get_login_info/<int:login_id>', methods=['GET'])
def get_login_info(login_id):
    cursor.execute("SELECT website, email, username, password FROM login WHERE lid = %s;", (login_id,))
    record = cursor.fetchone()
    if record:
        return jsonify({'website': record[0], 'email': record[1], 'username': record[2], 'password': record[3]})
    else:
        return jsonify({'error': 'Login information not found'})
    
@app.route('/save_changes', methods=['POST'])
def save_changes():
    if request.method == 'POST':
        data = request.get_json()
        
        # Extract the data from the JSON request
        lid = data['lid']
        website = data['website']
        email = data['email']
        username = data['username']
        password = data['password']
        
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Update the data in the PostgreSQL database
        cursor.execute("UPDATE login SET email = %s, username = %s, password = %s, website = %s, updated_at = %s WHERE lid = %s", (email, username, password, website, current_time, lid))
        conn.commit()

        return jsonify({'message': 'Data updated in the database.'})
    
@app.route('/delete_row', methods=['POST'])
def delete_row():
    data = request.get_json()
    if data and 'row_id' in data:
        row_id = data['row_id']
        cursor.execute("DELETE FROM login WHERE lid = %s", (row_id,))
        conn.commit()
        return jsonify({'message': 'Row deleted successfully.'})
    else:
        return jsonify({'message': 'Invalid data format.'}), 400
    
@app.route('/search', methods=['POST'])
def search():
    data = request.get_json()
    query = data['query']

    cursor.execute("SELECT lid, company FROM login WHERE company ILIKE %s ORDER BY company;", ('%' + query + '%',))
    record = cursor.fetchall()
    sql_table = [(item[0], item[1]) for item in record]

    return jsonify(sql_table)

@app.route('/homepage')
@login_required
def homepage():
    return render_template('homepage.html')

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