from flask import Flask, render_template, request, jsonify
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm 
from wtforms import StringField, PasswordField, BooleanField
from wtforms.validators import InputRequired, Email, Length
import pymysql
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import tweepy
from tweepy import OAuthHandler

app = Flask(__name__)
app.config['SECRET_KEY'] = 'MySecretKey'
connection = pymysql.connect(host="localhost", user="root",passwd="",database="isproject")
bootstrap = Bootstrap(app)

# app.config['MYSQL_HOST'] = '127.0.0.1'
# app.config['MYSQL_USER'] = 'root'
# app.config['MYSQL_PASSWORD'] = ''
# app.config['MYSQL_DB'] = 'isproject'

# app.config['SQLAlchemy_DATABASE_URL'] = 'sqlite:///mnt/c\\Users\\Brenda\\Desktop\\IS_Project\\project_database.db'

# database = SQLAlchemy(app)


class LoginForm(FlaskForm):
    email = StringField('email', validators=[InputRequired(),Email(message='Invalid email'), Length(max=50)])
    password = PasswordField('password', validators=[InputRequired(), Length(min=8, max=80)])
    remember = BooleanField('remember me')


class RegisterForm(FlaskForm):
	firstname = StringField('firstname', validators=[InputRequired()])
	lastname = StringField('lastname', validators=[InputRequired()])
	email = StringField('email', validators=[InputRequired(), Email(message='Invalid email'), Length(max=50)])
	username = StringField('username', validators=[InputRequired(), Length(min=4, max=15)])
	password = PasswordField('password', validators=[InputRequired(), Length(min=8, max=80)])


class KeywordsForm(FlaskForm):
    keywords = StringField('Keywords')


# @app.route('/dbConnection')
# def db():
# 	cursor = connection.cursor()
# 	cursor.execute("SELECT * FROM users" )
# 	rv = cursor.fetchall()
# 	print(rv)
    

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/login', methods=['POST', 'GET'])
def login():

	form=LoginForm()

	if form.is_submitted():
		usemail = form.data.email
		cursor = connection.cursor()
		cursor.execute("SELECT * FROM users WHERE email = %s", (usemail))
		user = cursor.fetchall()

		if user:
			if check_password_hash(user.password, form.password.data):
				login_user(user, remember=form.remember.data)
				return render_template("index.html")
			return '<h1> incorrect password </h1>'

		return '<h1> Email does not exist </h1>'

	return render_template('login2.html', form=form)

	# if form.validate_on_submit():
	# 	user = User.query.filter_by(username=form.username.data).first()
	# 	if user:
	# 		if check_password_hash(user.password, form.password.data):
	# 			login_user(user, remember=form.remember.data)
	# 			return redirect(url_for('dashboard'))
	# 	else:		
	# 		return '<h1>Invalid username or password</h1>'
 #        #return '<h1>' + form.username.data + ' ' + form.password.data + '</h1>'
 #    else:
    

@app.route('/register', methods=['POST', 'GET'])
def register():
	form = RegisterForm()

	if form.is_submitted():
		firstname = form.firstname.data
		lastname = form.lastname.data
		username = form.username.data
		email = form.email.data
		password = generate_password_hash(form.password.data, method='sha256')

		cursor = connection.cursor()

		cursor.execute("INSERT INTO users (firstname,lastname,username,email,password) VALUES (%s,%s,%s,%s,%s)", (firstname,lastname,username,email,password))
		connection.commit()
		render_template("login2.html", form=LoginForm())

	return render_template('register2.html', form=form)

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', name=current_user.username)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/keywords', methods=['POST', 'GET'])
def keywords():
	form = KeywordsForm()

	keywords = form.keywords.data

	ckey = 'QnxYONDqyBGXUQOPhSCRVixFu'
	csecret = 'UJ5IjcQAWWIqtHFA9gsEgFZiSJtsN1rfY5jeAZUJDL3992CbvL'
	atoken = '1029968149595267074-YXQ8C3GHHWKMsb6iftSDlKoi1rNLJz'
	asecret = 'CUSbmCkyKclGnBpQciRiIWZz3U2UOMr7JYoA4KGmnOtMm'

	auth = OAuthHandler(ckey,csecret)
	auth.set_access_token(atoken, asecret)
	api = tweepy.API(auth)

	if form.is_submitted():
		results = api.search(q=keywords)

		for result in results:
			tweet = result.text
			print(tweet)

		# return '<h1>' + keywords + '</h1>'
	return render_template("search2.html", form=form)

@app.route('/results')
def results():
    return render_template("results.html")


if __name__ == '__main__':
	app.run()
