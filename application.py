import os, hashlib, uuid, datetime, json, requests

from flask import (
	Flask, flash, jsonify, redirect, render_template, request, session, url_for
)
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

app = Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

darkskyapikey = "ef88d8b9c63ef193a0446df5b04168bf"



@app.route("/", methods=["GET","POST"])
def index():
	"""Homepage (Search Page). Redirects if not logged in."""

	# Checks if user is logged in
	if session.get("user_id") is None:
		return redirect(url_for('login'))
	else:
		# Renders search page
		return render_template("index.html")

@app.route("/register", methods=["POST"])
def register():
	"""Register an account."""

	# Gets input username and password
	username = request.form["usernamereg"]
	password = request.form["passwordreg"]

	# Checks if username is unique
	if db.execute("SELECT * FROM users WHERE username = :username",
	   {"username": username}).rowcount == 0:

		# Hashes password
		salt = uuid.uuid4().hex
		password = hashlib.sha256(salt.encode() + \
		           password.encode()).hexdigest() + ':' + salt

		# Adds input into users table
		db.execute("INSERT INTO users (username, password) VALUES \
		(:username, :password)",
		{"username": username, "password": password})
		db.commit()

		# Successful registration
		flash('You have successfully registered!', 'success')
		return redirect(url_for('login'))
	else:
		# Fails if username is not unique
		flash('Somebody already has that username.', 'danger')
		return redirect(url_for('login'))

@app.route("/login", methods=["GET", "POST"])
def login():
	"""Log in to an account."""

	# Gets input username and password
	if request.method == "POST":
		username = request.form["usernamelogin"]
		password = request.form["passwordlogin"]

		# Checks if username exists
		if db.execute("SELECT * FROM users WHERE username = :user",
		   {"user": username}).rowcount == 0:
			flash('There is no account with that username.', 'danger')
			return redirect(url_for('login'))

		# Checks if password is correct
		hashed_pass = db.execute("SELECT * FROM users WHERE \
		              username = :user", {"user": username}).fetchone()[2]
		check, salt = hashed_pass.split(':')

		if check == (hashlib.sha256(salt.encode()
		            + password.encode()).hexdigest()):

			# Login succeeds
			user = db.execute("SELECT * FROM users WHERE username = :user",
			       {"user": username}).fetchone()
			session["user_id"] = user.id
			session["username"] = user.username
			session["logged_in"] = True

			db.commit()
		else:
			# Incorrect password
			flash('The input password was incorrect.', 'danger')
			return redirect(url_for('login'))

	# Renders login page
	if session.get("user_id") is None:
		return render_template("login.html")
	else:
		# Redirects to homepage if logged in
		return redirect(url_for('index'))

@app.route("/logout", methods=["GET" ,"POST"])
def logout():
	"""Logs a player out."""

	# Clears session
	session.clear()
	flash('You have been successfully logged out.', 'success')
	return redirect(url_for('login'))

@app.route("/search", methods=["POST"])
def search():
	"""Shows search results."""

	# Gets input
	input = request.form["searchinput"]

	# Searches/sorts by zipcode if input is a zipcode
	if input.isdigit():
		search = '%' + input + '%'
		matches = db.execute("SELECT zipcode, city, statecode, id FROM \
		          locations WHERE zipcode LIKE :input ORDER BY zipcode",
		          {"input": search}).fetchall()

	# Searches/sorts by city otherwise
	else:
		search = '%' + input.upper() + '%'
		matches = db.execute("SELECT zipcode, city, statecode, id FROM \
		          locations WHERE city LIKE :input ORDER BY city, zipcode",
		          {"input": search}).fetchall()

	# Returns matches
	return render_template("search.html", matches=matches)

@app.route("/<int:loc_id>", methods=["GET","POST"])
def location_info(loc_id):
	"""Gives information on a location."""

	# Checks if user is signed in
	if session.get("user_id") is None:
		return redirect(url_for('login'))

	# Gets the matching location
	loc = db.execute("SELECT * FROM locations WHERE id = :input",
	      {"input": loc_id}).fetchone()

	# Gets the number of check-ins
	checkin_count = db.execute("SELECT COUNT(*) FROM checkins WHERE \
	                loc_id = :input", {"input": loc_id}).fetchone()[0]

	# Gets the comments on the location
	comments = db.execute("SELECT username, comments FROM checkins JOIN \
	           users ON users.id = checkins.cin_userid WHERE comments != '' AND loc_id = :input",
	           {"input": loc_id}).fetchall()

	# Gets the weather of the location
	request = ("https://api.darksky.net/forecast/" + darkskyapikey + "/"
	          + str(loc.latitude) + "," + str(loc.longitude))
	weather = requests.get(request).json()
	unixtime = json.dumps(weather["currently"]["time"])

	# Weather information to be displayed
	time = (datetime.datetime.fromtimestamp(int(unixtime))
	       .strftime('%m-%d-%Y %H:%M:%S'))
	summary = json.dumps(weather["currently"]["summary"])
	temperature = json.dumps(weather["currently"]["temperature"])
	dew_point = json.dumps(weather["currently"]["dewPoint"])
	humidity = (str(int(float(json.dumps(weather["currently"]["humidity"]))
	           * 100)) + '%')

	# Displays location page
	return render_template("location.html", loc=loc, checkins=checkin_count,
	       commentlist=comments, time=time, summary=summary,
	       temperature=temperature, dew_point=dew_point,
	       humidity=humidity, loc_id=loc_id)

@app.route("/checkin/<int:loc_id>", methods=["POST"])
def checkin(loc_id):

	# Gets input
	cin_id = session["user_id"]
	cin_comment = request.form["comment"]

	# Checks if a checkin has been submitted by the user for that zipcode
	if db.execute("SELECT * FROM checkins WHERE cin_userid = :check1 \
	   AND loc_id = :check2",
	   {"check1": cin_id, "check2": loc_id}).rowcount==0:

		# Adds check-in to database
		db.execute("INSERT INTO checkins (cin_userid, loc_id, comments) \
		VALUES (:input1, :input2, :input3)",
		{"input1":cin_id, "input2": loc_id, "input3": cin_comment})
		db.commit()

		flash('You have successfully checked in!', 'success')
		return redirect(url_for('location_info', loc_id=loc_id))

	else:

		# Check-in has already been submitted before
		flash('You already checked in before.', 'danger')
		return redirect(url_for('location_info', loc_id=loc_id))

@app.route("/api/<zip>")
def zip_api(zip):
	"""Return details about a zipcode."""

	# Make sure zipcode exists in the database
	zipcode = db.execute("SELECT * FROM locations WHERE zipcode = :input",
	          {"input": zip}).fetchone()

	if zipcode is None:
		return jsonify({"Error 404": "Zipcode not found"}), 404
	else:
		# Gets the number of checkins for the zipcode
		checkins = db.execute("SELECT COUNT(*) FROM checkins JOIN locations \
		           ON locations.id = checkins.loc_id WHERE zipcode = :zip",
		           {"zip": zip}).fetchone()[0]

		# Returns info as a JSON
		return jsonify({
			"place_name": zipcode.city,
			"state": zipcode.statecode,
			"latitude": float(zipcode.latitude),
			"longitude": float(zipcode.longitude),
			"zip": zipcode.zipcode,
			"population": zipcode.population,
			"check_ins": checkins
		})