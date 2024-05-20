from flask import Flask, render_template, url_for, redirect, session, request
from pymongo import MongoClient
from datetime import datetime
from bson.objectid import ObjectId 

app = Flask(__name__)
app.secret_key = '@A*Laxman!@$#12!^&77HG'

client = MongoClient("mongodb+srv://pradeepmajji42:Pradeep123@cluster0.mb8pytv.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
db = client.presidio

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/register_user')
def register_user():
    return render_template("register.html")

@app.route("/user_login", methods=['GET', 'POST'])
def user_login():
    if request.method == "POST":
        email = request.form['email']
        password = request.form['pwd']
        type = request.form['type']
        if type == "None":
            return render_template("index.html", msg="Enter Correct Details")
        else:
            try:
                user = db.users.find_one({"email": email, "password": password, "type": type})
                if user:
                    session['email'] = email
                    if type == "1":
                        return redirect('/after_seller_login')
                    else:
                        return redirect('/after_buyer_login')
                else:
                    return render_template('index.html', msg="Your credentials are Wrong")
            except Exception as e:
                return render_template('register.html', msg=f"Something went wrong. Please try again {e}")

@app.route("/user_register", methods=['GET', 'POST'])
def user_register():
    if request.method == "POST":
        first_name = request.form['first_name']
        second_name = request.form['second_name']
        email = request.form['email']
        password = request.form['password']
        phone = request.form['phone']
        Type = request.form['type']
        if Type == "-1":
            return render_template('register.html', msg="Enter Correct Inputs")
        else:
            try:
                user = db.users.find_one({"email": email, "type": Type})
                if user:
                    return render_template('register.html', msg="User already exists")
                else:
                    db.users.insert_one({
                        "first_name": first_name,
                        "last_name": second_name,
                        "email": email,
                        "password": password,
                        "type": Type,
                        "phone": phone
                    })
                    return render_template('index.html', msg="Account created successfully")
            except Exception as e:
                return render_template('register.html', msg="Something went wrong. Please try again")

@app.route('/get_search_data', methods=["POST"])
def get_search_data():
    if 'email' in session:
        query = request.form['search_query'].lower()
        try:
            posts = db.post.find({"place": {"$regex": query}})
            return render_template('after_buyer_login.html', posts=posts)
        except Exception as e:
            return redirect('/after_buyer_login')
    else:
        return redirect('/')

@app.route('/after_seller_login')
def after_seller_login():
    if 'email' in session:
        email = session['email']
        try:
            posts = list(db.post.find({"email": email}))
            print(posts)
            return render_template('after_seller_login.html', posts=posts)
        except Exception as e:
            return render_template('index.html', msg=f'Something went wrong! Please login again {e}')
    else:
        return redirect('/')

@app.route('/after_buyer_login')
def after_buyer_login():
    if 'email' in session:
        try:
            details = db.post.find()
            return render_template('after_buyer_login.html', posts=details)
        except Exception as e:
            return redirect('/')
    else:
        return redirect('/')

@app.route('/get_post_details', methods=["POST"])
def get_post_details():
    if 'email' in session:
        email = request.form['id']
        try:
            data = db.users.find_one({"email": email})
            return render_template('show_seller.html', data=data)
        except Exception as e:
            return redirect('/')
    else:
        return redirect('/')

@app.route('/insert_post')
def insert_post():
    if 'email' in session:
        return render_template('insert_post.html')
    else:
        return redirect('/')

@app.route('/add_post', methods=['POST'])
def add_post():
    if 'email' in session:
        if request.method == 'POST':
            email = session['email']
            place = request.form['place'].lower()
            area = request.form['area'].lower()
            rooms = request.form['rooms']
            baths = request.form['baths']
            hospitals = request.form['hospitals']
            colleges = request.form['colleges']
            schools = request.form['schools']
            try:
                db.post.insert_one({
                    "email": email,
                    "place": place,
                    "area": area,
                    "num_of_bed_rooms": rooms,
                    "bath_rooms": baths,
                    "hospitals": hospitals,
                    "colleges": colleges,
                    "schools": schools
                })
                return redirect('after_seller_login')
            except Exception as e:
                return redirect('after_seller_login')
        else:
            return render_template('after_seller_login.html')
    else:
        return redirect('/')

@app.route('/delete_post', methods=['POST'])
def delete_post():
    if request.method == 'POST':
        if 'email' in session:
            post_id = request.form['id']
            try:
                db.post.delete_one({"_id": ObjectId(post_id)})
                return redirect('/after_seller_login')
            except Exception as e:
                return redirect('/')
        else:
            return redirect('/')

@app.route('/update_post', methods=['POST'])
def update_post():
    if 'email' in session:
        post_id = request.form['id']
        place = request.form['place']
        area = request.form['area']
        rooms = request.form['num_of_bed_rooms']
        baths = request.form['bath_rooms']
        hospitals = request.form['hospitals']
        colleges = request.form['colleges']
        schools = request.form['schools']
        return render_template('edit.html', details=[post_id, place, area, rooms, baths, hospitals, colleges, schools])
    else:
        return redirect('/')

@app.route('/update_details', methods=["POST"])
def update_details():
    if request.method == 'POST':
        if 'email' in session:
            post_id = request.form['id']
            place = request.form['place'].lower()
            area = request.form['area'].lower()
            rooms = request.form['rooms']
            baths = request.form['baths']
            hospitals = request.form['hospitals']
            colleges = request.form['colleges']
            schools = request.form['schools']
            try:
                db.post.update_one(
                    {"_id": ObjectId(post_id)},
                    {"$set": {
                        "place": place,
                        "area": area,
                        "num_of_bed_rooms": rooms,
                        "bath_rooms": baths,
                        "hospitals": hospitals,
                        "colleges": colleges,
                        "schools": schools
                    }}
                )
                return redirect('/after_seller_login')
            except Exception as e:
                return redirect('/after_seller_login')
        else:
            return redirect('/')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)
