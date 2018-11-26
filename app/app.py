from flask import Flask, render_template, request, jsonify, redirect,url_for, session
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm 
from wtforms import StringField, PasswordField, BooleanField
from wtforms.validators import InputRequired, Email, Length
import pymysql
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import tweepy
from tweepy import OAuthHandler
from sklearn.externals import joblib
import numpy as numpy
import nltk
from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer
from sklearn.feature_extraction.text import TfidfVectorizer
import re
import pandas as pd
from collections import Counter

app = Flask(__name__)
app.config['SECRET_KEY'] = 'MySecretKey'
connection = pymysql.connect(host="localhost", user="root",passwd="",database="isproject")
bootstrap = Bootstrap(app)

class LoginForm(FlaskForm):
    email = StringField('email', validators=[InputRequired(),Email(message='Invalid email'), Length(max=50)])
    password = PasswordField('password', validators=[InputRequired(), Length(min=8, max=80)])


class RegisterForm(FlaskForm):
	firstname = StringField('firstname', validators=[InputRequired()])
	lastname = StringField('lastname', validators=[InputRequired()])
	email = StringField('email', validators=[InputRequired(), Email(message='Invalid email'), Length(max=50)])
	username = StringField('username', validators=[InputRequired(), Length(min=4, max=15)])
	password = PasswordField('password', validators=[InputRequired(), Length(min=8, max=80)])


class KeywordsForm(FlaskForm):
    keywords = StringField('Keywords')
    projectname = StringField('projectname',validators=[Length(max=200), InputRequired()])


#login function
@app.route('/login', methods=['POST', 'GET'])
def login():

	form=LoginForm()

	if form.is_submitted():
		usemail = form.email.data
		cursor = connection.cursor()
		cursor.execute("SELECT * FROM users WHERE email = %s", (usemail))
		user = []
		for row in cursor:
			user.append(row)
		print(user[0][5])
		if user:
			if check_password_hash(user[0][5], form.password.data):
				session['email'] = usemail
				return redirect(url_for('keywords'))
			return '<h1> incorrect password </h1>'

		return '<h1> Email does not exist </h1>'

	return render_template('login2.html', form=form)


#user registration function
@app.route('/register', methods=['POST', 'GET'])
def register():
	form = RegisterForm()
	form2 = LoginForm()

	if form.is_submitted():
		firstname = form.firstname.data
		lastname = form.lastname.data
		username = form.username.data
		email = form.email.data
		password = form.password.data
		pass_hash = generate_password_hash(form.password.data, method='sha256')

		cursor = connection.cursor()

		cursor.execute("INSERT INTO users (firstname,lastname,username,email,password) VALUES (%s,%s,%s,%s,%s)", (firstname,lastname,username,email,pass_hash))
		connection.commit()
		return redirect(url_for('login'))

	return render_template('register2.html', form=form)


#log out function
@app.route('/logout')
def logout():
    session.pop('email', None)
    return redirect(url_for('login'))


@app.route('/getsession')
def getsession():
    if 'email' in session:
    	user = session['email']
    	print(user)
    	print(type(user))


#function to search for tweets
@app.route('/keywords', methods=['POST', 'GET'])
def keywords():
	form = KeywordsForm()

	keywords = form.keywords.data
	project = form.projectname.data

	ckey = 'QnxYONDqyBGXUQOPhSCRVixFu'
	csecret = 'UJ5IjcQAWWIqtHFA9gsEgFZiSJtsN1rfY5jeAZUJDL3992CbvL'
	atoken = '1029968149595267074-YXQ8C3GHHWKMsb6iftSDlKoi1rNLJz'
	asecret = 'CUSbmCkyKclGnBpQciRiIWZz3U2UOMr7JYoA4KGmnOtMm'

	auth = OAuthHandler(ckey,csecret)
	auth.set_access_token(atoken, asecret)
	api = tweepy.API(auth)

	if 'email' in session:
		user = session['email']

	cursor = connection.cursor()
	cursor.execute("SELECT * FROM projects WHERE email = %s",(user))
	projectnames=[]
	output2=[]

	for row in cursor:
		projectname = row[1]
		pid = row[0]
		projectnames.append(projectname)
		temp2={ "projectname": projectname,
				"pid": pid }
		output2.append(temp2)

	connection.commit()



	if form.is_submitted():
		results = api.search(q=keywords)
		ps = PorterStemmer()
		model=joblib.load("C:/Users/Brenda/NBClassifier.pkl")
		tfidf=joblib.load("C:/Users/Brenda/test.pkl")
		output = []
		sentiment_array = []

		for result in results:
			result = result.text
			tweet = [result]
			tftweet=tfidf.transform(tweet)
			sentiment = model.predict(tftweet)
			
			for ans in sentiment:
				print(ans)
				sentiment_array.append(ans)



			if sentiment == 0:
				sentiment =  "Non-Radical"
			elif sentiment == 1:
				sentiment = "Radical"
			else:
				sentiment = "Neutral"
			temp = {
				"tweet":result,
				"sentiment":sentiment
			}
			output.append(temp)

		print(sentiment_array)
		counter = Counter(sentiment_array)
		count_r = counter[1]
		count_nr = counter[0]
		count_n = counter[2]
		print(count_r)
		print(count_nr)
		print(count_n)
		print(counter)
		print(project,user,keywords,count_r,count_nr,count_n)

		cursor = connection.cursor()
		cursor.execute("INSERT INTO projects (projectName,email,keywords,radicalCount,nonradicalCount,neutralCount) VALUES (%s,%s,%s,%s,%s,%s)", (project,user,keywords,count_r,count_nr,count_n))
		
		cursor.execute("SELECT * FROM projects WHERE email = %s",(user))
		projectnames=[]
		output2=[]

		for row in cursor:
			projectname = row[1]
			pid = row[0]
			projectnames.append(projectname)
			temp2={ "projectname": projectname,
					"pid": pid }
			output2.append(temp2)

		connection.commit()

		return render_template('results.html', output = output, output2=output2)
			
	return render_template("search2.html", form=form, output2=output2 )


@app.route('/admin')
def admin():
	return render_template("index.html")

@app.route('/users')
def users():

	output3 =[]
	cursor = connection.cursor()
	cursor.execute("SELECT * FROM users")

	for row in cursor:
		uid = row[0]
		firstname = row[1]
		lastname = row[2]
		username = row[3]
		email = row[4]

		
		temp3={ "uid": uid,
				"firstname": firstname,
				"lastname": lastname,
				"username": username,
				"email": email
				 }
		output3.append(temp3)

	connection.commit()


	return render_template("users.html", output3 = output3 )


@app.route('/projects')
def admin_projects():

	output4 =[]
	cursor = connection.cursor()
	cursor.execute("SELECT * FROM projects")

	for row in cursor:
		pid = row[0]
		projectname = row[1]
		keywords = row[3]
		email = row[2]
		radicalCount = row[4]
		nonradicalCount = row[5]
		neutralCount = row[6]

		
		temp4={ "pid": pid,
				"projectname": projectname,
				"keywords": keywords,
				"email": email,
				"radicalCount": radicalCount,
				"nonradicalCount": nonradicalCount,
				"neutralCount": neutralCount
				 }
		output4.append(temp4)

	connection.commit()


	return render_template("projects.html", output4 = output4 )


@app.route('/delete' , methods=['GET', 'POST'])
def delete():
	if request.method == 'POST':
		user_id = request.form.get('delete')
		print(user_id)

		cursor = connection.cursor()
		cursor.execute("DELETE FROM users WHERE uid=%s",(user_id))
		connection.commit()

	return redirect(url_for('users'))



@app.route('/proj/<pid>')
def proj(pid):
	print("retrieved")
	project=[]
	output5=[]

	cursor = connection.cursor()
	cursor.execute("SELECT * FROM projects WHERE pid=%s",(pid))

	for row in cursor:
		project.append(row)

		pid = row[0]
		projectname = row[1]
		keywords = row[3]
		email = row[2]
		radicalCount = row[4]
		nonradicalCount = row[5]
		neutralCount = row[6]

		temp5={ "pid": pid,
				"projectname": projectname,
				"keywords": keywords,
				"email": email,
				"radicalCount": radicalCount,
				"nonradicalCount": nonradicalCount,
				"neutralCount": neutralCount
				 }
		output5.append(temp5)

	connection.commit()
	return render_template("project_view.html", output5 = output5 )


if __name__ == '__main__':
	app.run()
	app.secret_key = 'MySecretKey'
