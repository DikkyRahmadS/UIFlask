from flask import Flask  , render_template,request,make_response,jsonify,url_for,redirect,Response
from sqlalchemy import create_engine,and_
from flask_sqlalchemy import SQLAlchemy
import logging
from functools import wraps
import jwt
from datetime import datetime, timedelta

app = Flask(__name__)


# JUST IN CASE, Connect db without ORM.

# app.config['MYSQL_HOST'] = 'localhost'
# app.config['MYSQL_USER'] = 'root'
# app.config['MYSQL_PASSWORD'] = ''
# app.config['MYSQL_DB'] = 'flask_proto'
 
# mysql = MySQL(app)

# JWT Secret Key
app.config['SECRET_KEY'] = 'your secret key'

# To connect db
app.config['SQLALCHEMY_DATABASE_URI'] ="mysql://root:@localhost/flask_proto"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class user(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(30))
    password = db.Column(db.String(20))
 
 
    def __init__(self, username, password):
        self.username = username
        self.password = password


# Validate token
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        # jwt is passed in the request header


        if 'access_token' in request.cookies:
            token = request.cookies.get('access_token')
        # return 401 if token is not passed
        if not token:
            return redirect("/login")
  
        try:
            decoded_data = jwt.decode(jwt=token,
                              key=app.config['SECRET_KEY'],
                              algorithms=["HS256"])
            current_user = user.query.filter_by(id=decoded_data["userid"]).first()

        except:
            return jsonify({
                'message' : 'Token is invalid !!'
            }), 401
        # returns the current logged in users context to the routes
        return  f( *args, **kwargs)
        # return
  
    return decorated


# User Route
@app.route("/user",methods=['GET'])
@token_required
def userRoute():
    if request.method == "GET":
        token = request.cookies.get('access_token')
        # return token
        decoded_data = jwt.decode(jwt=token,
                              key=app.config['SECRET_KEY'],
                              algorithms=["HS256"])

        
        result = user.query.filter_by(id=decoded_data["userid"]).first()

        # return decoded_data["userid"]
        return render_template('user.html',user=result)

# Main Route
@app.route("/" , methods=['GET'])
@token_required
def index():
    if request.method == "GET":
        users = user.query.all()
        return render_template('index.html', users = users)
    
@app.route("/register", methods=['GET', 'POST'])

# Register Route (Unprotected)
def register():
    if request.method == "GET":
        return render_template('register.html')
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']
        newUser = user(username=username, password=password)
        db.session.add(newUser)
        db.session.commit()
        return redirect("/login")

# Login Route (Unprotected)
@app.route("/login",methods=['GET', 'POST'])
def login():
    if request.method == "GET":
        return render_template('login.html')
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']
        result = user.query.filter_by(username=username).first()

        if result :
            if result.password == password:
                # return result.username
                token = jwt.encode({
                'userid': result.id,
                'exp' : datetime.utcnow() + timedelta(minutes = 30)
                }, app.config['SECRET_KEY'])
                # return "logged in"
                response = make_response(redirect("/user"))
                response.set_cookie('access_token',value=token)
                return response
                # return make_response(jsonify({'token' : token}), 201)
                
            else:
                return 'Incorrect password, try again.'

        else :
            return "no user found"
        

        return redirect(url_for('login'))

# Logout Route, clear cookie (Unprotected)
@app.route("/logout",methods=['POST'])
def logout():
    if request.method == "POST":
        userid = request.form['userid']
        response = make_response(redirect("/"))
        response.delete_cookie(key="access_token")
        return  response
        # Response.delete_cookie(key="access_token" )
       
        # return render_template()


if __name__ == "__main__":
    app.run()