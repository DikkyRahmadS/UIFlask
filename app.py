from flask import Flask  , render_template,request,make_response,jsonify,url_for,redirect,Response
from sqlalchemy import create_engine,and_
from flask_sqlalchemy import SQLAlchemy
import logging
from functools import wraps
import jwt
from datetime import datetime, timedelta

app = Flask(__name__)
# app.wsgi_app = middleware.SimpleMiddleWare(app.wsgi_app)

# app.config['MYSQL_HOST'] = 'localhost'
# app.config['MYSQL_USER'] = 'root'
# app.config['MYSQL_PASSWORD'] = ''
# app.config['MYSQL_DB'] = 'flask_proto'
 
# mysql = MySQL(app)

app.config['SECRET_KEY'] = 'your secret key'

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


# def token_required(f):
#     @wraps(f)
#     def decorated(*args, **kwargs):
#         token = None
#         if "Authorization" in request.headers:
#             token = request.headers["Authorization"].split(" ")[1]
#         if not token:
#             return {
#                 "message": "Authentication Token is missing!",
#                 "data": None,
#                 "error": "Unauthorized"
#             }, 401
#         try:
#             data=jwt.decode(token, current_app.config["SECRET_KEY"], algorithms=["HS256"])
#             current_user=models.User().get_by_id(data["user_id"])
#             if current_user is None:
#                 return {
#                 "message": "Invalid Authentication token!",
#                 "data": None,
#                 "error": "Unauthorized"
#             }, 401
#             if not current_user["active"]:
#                 abort(403)
#         except Exception as e:
#             return {
#                 "message": "Something went wrong",
#                 "data": None,
#                 "error": str(e)
#             }, 500

#         return f(current_user, *args, **kwargs)

#     return decorated



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
            # decoding the payload to fetch the stored details
            # data = jwt.decode(token, app.config['SECRET_KEY'])
            # current_user = User.query\
            #     .filter_by(public_id = data['public_id'])\
            #     .first()
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


@app.route("/" , methods=['GET'])
@token_required
def index():
    if request.method == "GET":
        users = user.query.all()
        return render_template('index.html', users = users)
    
@app.route("/register", methods=['GET', 'POST'])

def register():
    if request.method == "GET":
        return render_template('register.html')
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']
        newUser = user(username=username, password=password)
        db.session.add(newUser)
        db.session.commit()
        return f"Done!!"

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