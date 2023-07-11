from flask import Flask, render_template, request, redirect, flash
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
	return render_template("index.html")

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
        username = loginForm['username']
        cur = mysql.connection.cursor()
        queryStatement = f"SELECT * FROM user WHERE username = '{username}'"
        numRow = cur.execute(queryStatement)
        if numRow > 0:
            user =  cur.fetchone()
            if check_password_hash(user['password'], loginForm['password']):
                flash("Log In successful",'success')
                return redirect('/')
            else:
                cur.close()
                flash("Password doesn't match", 'danger')
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
            flash('Passwords do not match!','danger')
            return render_template('signup.html')
        p1 = userDetails['first_name']
        p2 = userDetails['last_name']
        p3 = userDetails['email']
        p4 = userDetails['password']
        hashed_pw = generate_password_hash(p4)
        print(p1 + "," + p2 + "," + p3 + "," + p4 + "," + hashed_pw)

        queryStatement = (
            f"INSERT INTO "
            f"user(first_name,last_name, email, password, role_id) "
            f"VALUES('{p1}', '{p2}', '{p3}','{hashed_pw}', 1)"
        )
        print(check_password_hash(hashed_pw, p4))
        print(queryStatement)
        cur = mysql.connection.cursor()
        cur.execute(queryStatement)
        mysql.connection.commit()
        cur.close()

        flash("Form Submitted Successfully.",'success')
        return redirect('/')    
    return render_template('signup.html')

@app.route('/menu', methods=['GET', 'POST'])
def menu():
    if request.method == 'POST':
        return redirect(url_for('menu'))
    return render_template('menu.html')

if __name__ == '__main__':
	app.run(debug=True);