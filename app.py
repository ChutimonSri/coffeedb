from flask import Flask, render_template, request, redirect, flash, session, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from flask_mysqldb import MySQL
import yaml

app = Flask(__name__)
app.config['SECRET_KEY'] = "Never push this line to github public repo"

cred = yaml.load(open('cred.yaml'), Loader=yaml.Loader)
app.config['MYSQL_HOST'] = cred['mysql_host']
app.config['MYSQL_USER'] = cred['mysql_user']
app.config['MYSQL_PASSWORD'] = cred['mysql_password']
app.config['MYSQL_DB'] = cred['mysql_db']
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

mysql = MySQL(app)

@app.route("/")
def index():
	return render_template("home.html")

@app.route('/home', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        # do stuff when the form is submitted

        # redirect to end the POST handling
        # the redirect can be to the same route or somewhere else
        return redirect(url_for('home'))

    # show the form, it wasn't submitted
    return render_template('home.html')

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        return redirect(url_for('contact'))
    return render_template('contact.html')

@app.route('/cart', methods=['GET', 'POST'])
def cart():
    if request.method == 'POST':
        return redirect(url_for('cart'))
    return render_template('cart.html')

@app.route('/login/', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    elif request.method == 'POST':
        loginForm = request.form
        email = loginForm['email']
        cur = mysql.connection.cursor()
        queryStatement = f"SELECT * FROM user WHERE email = '{email}'"
        numRow = cur.execute(queryStatement)
        if numRow > 0:
            user = cur.fetchone()
            if check_password_hash(user['password'], loginForm['password']):
                # Record session information
                session['login'] = True
                session['user_id'] = user['user_id']  # Store the user ID in the session
                session['email'] = user['email']
                session['userroleid'] = str(user['role_id'])
                session['firstName'] = user['first_name']
                session['lastName'] = user['last_name']
                print(session['email'] + " roleid: " + session['userroleid'])
                flash('Welcome ' + session['firstName'], 'success')
                return redirect('/')
            else:
                cur.close()
                flash("Password doesn't match", 'danger')
                return render_template('login.html')
        else:
            cur.close()
            flash('User not found', 'danger')
            return render_template('login.html')
        cur.close()
        return redirect('/')
    return render_template('login.html')


@app.route('/signup/', methods=['GET', 'POST'])
def signup():
    if request.method == 'GET':
        return render_template('signup.html')
    elif request.method == 'POST':
        userDetails = request.form
        # Check the password and confirm password
        if userDetails['password'] != userDetails['confirm_password']:
            flash('Passwords do not match!', 'danger')
            return render_template('signup.html')
        p1 = userDetails['first_name']
        p2 = userDetails['last_name']
        p3 = userDetails['email']
        p4 = userDetails['password']
        hashed_pw = generate_password_hash(p4)
        print(p1 + "," + p2 + "," + p3 + "," + p4 + "," + hashed_pw)

        queryStatement = (
            f"INSERT INTO "
            f"user(first_name, last_name, email, password, role_id) "
            f"VALUES('{p1}', '{p2}', '{p3}', '{hashed_pw}', 1)"
        )
        print(check_password_hash(hashed_pw, p4))
        print(queryStatement)
        cur = mysql.connection.cursor()
        cur.execute(queryStatement)
        mysql.connection.commit()

        # Retrieve the user ID from the database
        queryStatement = f"SELECT user_id FROM user WHERE email = '{p3}'"
        cur.execute(queryStatement)
        user_id = cur.fetchone()['user_id']
        cur.close()

        # Set session variables to automatically log in the user
        session['login'] = True
        session['user_id'] = user_id  # Store the user ID in the session
        session['email'] = p3
        session['userroleid'] = '1'
        session['firstName'] = p1
        session['lastName'] = p2

        flash("Form Submitted Successfully.", 'success')
        return redirect('/')

    return render_template('signup.html')


@app.route('/menu', methods=['GET', 'POST'])
def menu():
    if request.method == 'POST':
        return redirect(url_for('menu'))
    return render_template('menu.html')


@app.route('/user_mnm/')
def user_mnm():
    cur = mysql.connection.cursor()
    queryStatement = f"SELECT * FROM user order by role_id"
    result_value = cur.execute(queryStatement) 
    if result_value > 0:
        users = cur.fetchall()
        return render_template('user_management.html', users=users)
    else:
        return render_template('user_management.html')


@app.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out", 'info')
    return redirect('/')

@app.route('/add_user/', methods=['GET', 'POST'])
def add_user():
    if request.method == 'GET':
        return render_template('add_user.html')
    elif request.method == 'POST':
        userDetails = request.form
        # Check the password and confirm password
        if userDetails['password'] != userDetails['confirm_password']:
            flash('Passwords do not match!','danger')
            return render_template('add_user.html')
        p1 = userDetails['first_name']
        p2 = userDetails['last_name']
        p3 = userDetails['email']
        p4 = userDetails['password']
        hashed_pw = generate_password_hash(p4)
        print(p1 + "," + p2 + "," + p3 + "," + p4 + "," + hashed_pw)

        if userDetails['role'] == 'admin':
            user_id = 0
        else:
            user_id = 1

        queryStatement = (
            f"INSERT INTO "
            f"user(first_name,last_name, email, password, role_id) "
            f"VALUES('{p1}', '{p2}', '{p3}','{hashed_pw}', {user_id})"
        )
        print(check_password_hash(hashed_pw, p4))
        print(queryStatement)
        cur = mysql.connection.cursor()
        cur.execute(queryStatement)
        mysql.connection.commit()

        flash("Form Submitted Successfully.", 'success')
        return redirect('/user_mnm/')
    return render_template('add_user.html')

@app.route('/edit_user/<int:id>/', methods=['GET', 'POST'])
def edit_user(id):
    if request.method == 'POST':
        cur = mysql.connection.cursor()
        new_firstname= request.form['first_name']
        new_lastname= request.form['last_name']

        queryStatement = f"UPDATE user SET first_name= '{new_firstname}', last_name = '{new_lastname}' WHERE user_id = {id}"
        print(queryStatement)
        cur.execute(queryStatement)
        mysql.connection.commit()
        cur.close()

        session['firstName'] = new_firstname
        session['lastName'] = new_lastname

        flash('User updated', 'success')
        return redirect('/user_mnm/')
    else:
        cur = mysql.connection.cursor()
        queryStatement = f"SELECT * FROM user WHERE user_id = {id}"
        print(queryStatement)
        result_value = cur.execute(queryStatement)
        if result_value > 0:
            member = cur.fetchone()
            member_form = {}
            member_form['first_name'] = member['first_name']
            member_form['last_name'] = member['last_name']
            return render_template('edit_user.html', member_form=member_form)
    
from flask import session

@app.route('/delete_user/<int:id>/', methods=['GET'])
def delete_user(id):

    if request.method == 'GET':
        if id == session.get('user_id'):
            cur = mysql.connection.cursor()        
            queryStatement = f"DELETE FROM user WHERE user_id = {id}"
            print(queryStatement)
            cur.execute(queryStatement)
            mysql.connection.commit()
            cur.close()
            session.clear()  # Clear the session to log them out
            flash('Deleted user successfully', 'success')
            return redirect(url_for('login'))
        else:
            cur = mysql.connection.cursor()        
            queryStatement = f"DELETE FROM user WHERE user_id = {id}"
            print(queryStatement)
            cur.execute(queryStatement)
            mysql.connection.commit()
            cur.close()
            flash('Deleted user successfully', 'success')
            return redirect('/user_mnm/')
        

    

if __name__ == '__main__':
	app.run(debug=True);