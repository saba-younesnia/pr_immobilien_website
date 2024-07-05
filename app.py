import os
from flask import *
import sqlite3
from flask_session import Session
from werkzeug.utils import secure_filename
from datetime import datetime
import pandas as pd
import numpy as np
from polynomial_regression_class import RealEstateModel

app = Flask(__name__)

app.config['DATABASE'] = 'pr1.db'

app.config['SESSION_PERMANENT'] = False
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

app.config['UPLOAD_FOLDER'] = 'static/property_images'

model = RealEstateModel('D:\\germany_real_estate_prices_final_modified1.csv')

def connect_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(app.config['DATABASE'])
    return db

def check_username_in(username):
    db = connect_db()
    cursor = db.cursor()
    query = "SELECT * FROM users WHERE username= ?"
    cursor.execute(query,[username])
    same_usernames = cursor.fetchall()
    if len(same_usernames) == 0:
         return True
    else:
        return False

def check_password_in(password):
    if len(password) < 8:
        return False
    else:
        return True

abstract_api_key = '123a5da50c2a4bad877f5687f23bdf27'
@app.route('/check_email', methods=['POST'])
def check_email():
    db = connect_db()
    cur = db.cursor()
    email = request.form['email']
    query1 = "select email from users where email= ?"
    cur.execute(query1,[email] )
    results1 = cur.fetchall()
    if len(results1) > 0:
        return jsonify({'exists': True})
    else:
        return jsonify({'exists': False})

@app.route('/', methods=['GET', 'POST'])
def index():
    db=connect_db()
    cur=db.cursor()
    property_list=[]
    if request.method == 'POST':
        search_query = request.form.get('search')
        session['search_query'] = search_query
        if session.get('user_id'):
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            query1 = "INSERT INTO searches(userid, search_query, time) VALUES (?,?,?)"
            cur.execute(query1,(session['user_id'],search_query,timestamp))
        if search_query:
            query = "SELECT property_id, status, property_type, area, price, deposite, monthly_rent, property_address, image_paths, latitude, longitude FROM properties where property_address like '%"+search_query+"%'"
            cur.execute(query)
            properties = cur.fetchall()
            db.commit()
            for property in properties:
                image_paths = property[8].replace('\\', '/').split(',') if property[8] else []
                image_paths = [path for path in image_paths if path]
                property_dict = {
                    'property_id': property[0],
                    'status': property[1],
                    'property_type': property[2],
                    'area': property[3],
                    'price': property[4],
                    'deposit': property[5],
                    'monthly_rent': property[6],
                    'address': property[7],
                    'latitude': property[9],
                    'longitude': property[10],
                    'image_paths': image_paths
                }
                property_list.append(property_dict)
        return render_template('all_posts.html', properties=property_list)
    else:
        return render_template('index.html')

@app.route('/check_username', methods=["POST"])
def check_username():
    username = request.form.get("username")
    if check_username_in(username)==False:
        return jsonify({"exists": True})
    else:
        return jsonify({"exists": False})

@app.route('/signup', methods=['POST','GET'])
def signup():
    if request.method == 'POST':
        db=connect_db()
        cur=db.cursor()
        username = request.form.get("username")
        password = request.form.get("password")
        email = request.form['email']
        query1 = "select email from users where email=?"
        cur.execute(query1,[email] )
        results1 = cur.fetchall()
        if (check_username_in(username)==True and check_password_in(password)==True and len(results1)==0):
            db = connect_db()
            cur = db.cursor()
            name = request.form.get('name')
            familyname = request.form.get('familyname')
            query1 = "insert into users(name, familyname, username, password, email) values(?,?,?,?,?)"
            cur.execute(query1,[name,familyname,username,password,str(email)])
            db.commit()
            return render_template('signin.html')
        else:
            return render_template('signup.html')
    else:
        return render_template('signup.html')

@app.route('/signin', methods=['GET', 'POST'])
def signin():
    if request.method == 'POST':
        db=connect_db()
        cur=db.cursor()
        username = request.form.get('username')
        password = request.form.get('password')
        query1 = "select * from users where username=? and password=?"
        cur.execute(query1,[username,password])
        user=cur.fetchall()
        if len(user) == 0:
            no_user = 'Wrong username or password'
            return render_template('signin.html', no_user=no_user)
        else:
            session['username'] = username
            session['password'] = password
            session['user_id'] = user[0][0]
            query2 = "select roll from users where username=? and password=?"
            cur.execute(query2,[username,password])
            user_roll=cur.fetchall()
            for mylist in user_roll:
                for element in mylist:
                    if element=='normal':
                        return render_template('index.html')
                    else:
                        return render_template('admin_index.html')
    else:
        return render_template('signin.html')

@app.route('/signout')
def signout():
    session.clear()
    return redirect(url_for('signin'))


@app.route('/suggestions', methods=['GET'])
def suggestions():
    db = connect_db()
    cur = db.cursor()
    query = request.args.get('query', '')
    filtered_suggestions = []
    if query:
        query1 = f"""SELECT property_address FROM properties WHERE SUBSTR(property_address, 1, INSTR(property_address, ',') - 1) LIKE '{query}%';"""
        query2 = f"""SELECT property_address FROM properties WHERE SUBSTR(property_address, INSTR(property_address, ',') + 2, INSTR(SUBSTR(property_address, INSTR(property_address, ',') + 2), ',') - 1) LIKE '{query}%';"""
        cur.execute(query1)
        results1 = cur.fetchall()
        cur.execute(query2)
        results2 = cur.fetchall()
        seen = set()
        for mytuple in results1:
            if len(mytuple) > 0:
                for string in mytuple:
                    split_string = string.split(',')
                    if split_string[0] not in seen:
                        seen.add(split_string[0])
                        filtered_suggestions.append(split_string[0])
        for mytuple in results2:
            if len(mytuple) > 0:
                for string in mytuple:
                    split_string = string.split(',')
                    if split_string[1] not in seen:
                        seen.add(split_string[1])
                        filtered_suggestions.append(split_string[1])
    else:
        if session.get('user_id'):
            query3 = "SELECT search_query FROM searches WHERE userid=? ORDER BY searchid DESC LIMIT 3"
            cur.execute(query3, (session['user_id'],))
            results3 = cur.fetchall()
            seen = set()
            for row in results3:
                if row[0] not in seen:
                    seen.add(row[0])
                    filtered_suggestions.append(row[0])

    return jsonify(filtered_suggestions)


@app.route('/add_property',methods=['GET','POST'])
def add_property():
    if request.method == 'POST':
        return render_template('add_property.html')
    else:
        return render_template('add_property.html')

@app.route('/map', methods=['POST','GET'])
def map():
    if request.method == 'POST':
        return render_template('map.html')
    else:
        return render_template('map.html')

@app.route('/submit-address', methods=['POST','GET'])
def submit_address():
    if request.method == 'POST':
        db = connect_db()
        cur = db.cursor()
        data = request.json
        address = data.get('address')
        latlng = data.get('latlng', {})
        latitude = latlng.get('lat', None)
        print(latitude)
        longitude = latlng.get('lng', None)
        str_address = address[len('Address: '):]
        query = "UPDATE properties SET property_address = ?, latitude = ?, longitude = ? WHERE property_id = ?"
        cur.execute(query, (str_address, latlng['lat'], latlng['lng'], session['property_id']))
        db.commit()
        query = "SELECT * FROM properties WHERE property_id = ?"
        cur.execute(query,[session['property_id']])
        info_for_csvFile=cur.fetchall()
        if info_for_csvFile[0][2]=='sale':
            date_obj = datetime.strptime(info_for_csvFile[0][13], '%Y-%m-%d')
            year=date_obj.year
            #closest_latitude=model.get_nearest_latitude(latitude,longitude)
            #closest_longitude=model.get_nearest_longitude(latitude,longitude)
            price = float(info_for_csvFile[0][5]) / float(info_for_csvFile[0][4])
            if info_for_csvFile[0][3]=='villa':
                model.add_row_and_save(latitude=latitude, longitude=longitude, year=year, villa_min=price, villa_max=price)
            elif info_for_csvFile[0][3]=='apartment':
                model.add_row_and_save(latitude=latitude, longitude=longitude, year=year, apartment_min=price, apartment_max=price)
            elif info_for_csvFile[0][3]=='land':
                model.add_row_and_save(latitude=latitude, longitude=longitude, year=year, land_min=price, land_max=price)
        return render_template('index.html')
    else:
        return render_template('map.html')


@app.route('/get-addresses', methods=['GET'])
def get_addresses():
    db = connect_db()
    cur = db.cursor()
    query = "SELECT property_address, latitude, longitude FROM properties WHERE latitude IS NOT NULL AND longitude IS NOT NULL"
    cur.execute(query)
    rows = cur.fetchall()
    db.close()
    addresses = [{'address': row[0], 'latlng': {'lat': row[1], 'lng': row[2]}} for row in rows]
    return jsonify(addresses)

@app.route('/view', methods=['GET', 'POST'])
def view_map():
    db = connect_db()
    cur = db.cursor()
    property_list = []
    if request.method == 'GET':
        search_query=session['search_query']
        if search_query:
            query = "SELECT property_id,property_address, latitude, longitude FROM properties where property_address like '%"+search_query+"%' and property_id='"+str(session['post_of_property_id'])+"'"
            cur.execute(query)
            properties = cur.fetchall()
            for property in properties:
                property_dict = {
                    'property_id': property[0],
                    'address': property[1],
                    'latitude': property[2],
                    'longitude': property[3],
                }
                property_list.append(property_dict)
    return render_template('view_map.html', properties=property_list)


@app.route('/submit_info', methods=['POST'])
def submit_info():
    db = connect_db()
    cur = db.cursor()
    property_type = request.form['propertyType']
    area = request.form['area']
    listing_type = request.form['listingType']
    current_date = datetime.now().strftime('%Y-%m-%d')  # Get the current date

    if listing_type == 'sale':
        price = request.form.get('price')
        query1 = """INSERT INTO properties (userid, status, property_type, area, price, date) VALUES (?, ?, ?, ?, ?, ?)"""
        cur.execute(query1, (session['user_id'], listing_type, property_type, area, price, current_date))
        db.commit()
    if listing_type == 'rent':
        deposit = request.form.get('deposit')
        monthly_rent = request.form.get('monthlyRent')
        query2 = """INSERT INTO properties (userid, status, property_type, area, deposite, monthly_rent, date)VALUES (?, ?, ?, ?, ?, ?, ?)"""
        cur.execute(query2,(session['user_id'], listing_type, property_type, area, deposit, monthly_rent, current_date))
        db.commit()
    query3 = "SELECT property_id FROM properties ORDER BY rowid DESC LIMIT 1"
    cur.execute(query3)
    property_id = cur.fetchone()
    session['property_id'] = property_id[0]

    images = request.files.getlist('pictures[]')
    image_paths = []
    user_directory = os.path.join(app.config['UPLOAD_FOLDER'], str(session['property_id']))
    os.makedirs(user_directory, exist_ok=True)

    for image in images:
        if image.filename != '':
            filename = secure_filename(image.filename)
            image_path = os.path.join(user_directory, filename)
            image.save(image_path)
            image_paths.append(image_path)

    image_paths_str = ','.join(image_paths)
    query4 = "UPDATE properties SET image_paths = ? WHERE property_id = ?"
    cur.execute(query4, (image_paths_str, session['property_id']))
    db.commit()

    return render_template('map.html')

@app.route('/update_favorite', methods=['POST'])
def update_favorite():
    db=connect_db()
    cur=db.cursor()
    favorite = request.form.get('favorite', '0')
    print(favorite)
    query1="select * from favorits where post_id='"+str(session['post_of_property_id'])+"' and userid='"+str(session['user_id'])+"'"
    cur.execute(query1)
    already_favorited=cur.fetchall()
    print(already_favorited)
    if len(already_favorited)>0:
        query2="delete from favorits where post_id='"+str(session['post_of_property_id'])+"'"
        cur.execute(query2)
        db.commit()
    else:
        query3="insert into favorits (post_id, userid) values('"+str(session['post_of_property_id'])+"','"+str(session['user_id'])+"')"
        cur.execute(query3)
        db.commit()
    return 'Favorite status updated'


@app.route('/property/<int:property_id>', methods=['GET'])
def property_detail(property_id):
    session['post_of_property_id'] = property_id
    db = connect_db()
    cur = db.cursor()
    query1 = """
    SELECT property_type, area, price, deposite, monthly_rent, property_address, image_paths, status,userid
    FROM properties
    WHERE property_id = ?
    """
    cur.execute(query1, (property_id,))
    property = cur.fetchone()
    property_value = property[6] if len(property) > 6 else None

    if property_value:
        image_paths = property_value.replace('\\', '/').split(',')
    else:
        image_paths = []
    image_paths = [path for path in image_paths if path]  # Remove empty strings

    if property:
        property_dict = {
            'property_id': property_id,
            'property_type': property[0],
            'area': property[1],
            'price': property[2],
            'deposit': property[3],
            'monthly_rent': property[4],
            'address': property[5],
            'image_paths': image_paths,
            'listing_type': property[7]
        }
        session['post_owner_id']=property[8]
        if session.get('user_id'):
            query2 = """
            SELECT favorits.post_id, favorits.userid 
            FROM favorits 
            INNER JOIN properties ON favorits.post_id = properties.property_id 
            INNER JOIN users ON favorits.userid = users.userid 
            WHERE favorits.post_id = ? AND users.userid = ?
            """
            cur.execute(query2, (session['post_of_property_id'], session['user_id']))
            already_favorited = cur.fetchall()
            if len(already_favorited) > 0:
                return render_template('post.html', **property_dict, turn_red=True, user_id=session['user_id'])
            else:
                return render_template('post.html', **property_dict, user_id=session['user_id'])
        else:
            return render_template('post.html',**property_dict)

@app.route('/all_posts', methods=['GET', 'POST'])
def all_posts():
    db = connect_db()
    cur = db.cursor()
    if request.method == 'POST':
        property_filter = request.form.get('filter')
        min_area = request.form.get('min_area')
        max_area = request.form.get('max_area')

        min_price = max_price = None
        min_rent = max_rent = min_deposit = max_deposit = None

        if property_filter == 'sale':
            min_price = request.form.get('min_price')
            max_price = request.form.get('max_price')
        else:
            min_rent = request.form.get('min_monthly_rent')
            max_rent = request.form.get('max_monthly_rent')
            min_deposit = request.form.get('min_deposit')
            max_deposit = request.form.get('max_deposit')

        if min_area and max_area and float(min_area) > float(max_area):
            min_area, max_area = max_area, min_area
        if min_price and max_price and float(min_price) > float(max_price):
            min_price, max_price = max_price, min_price
        if min_rent and max_rent and float(min_rent) > float(max_rent):
            min_rent, max_rent = max_rent, min_rent
        if min_deposit and max_deposit and float(min_deposit) > float(max_deposit):
            min_deposit, max_deposit = max_deposit, min_deposit

        query = "SELECT property_id, status, property_type, area, price, deposite, monthly_rent, property_address, image_paths, latitude, longitude FROM properties WHERE status = ?"
        query_params = [property_filter]

        if min_area:
            query += " AND area >= ?"
            query_params.append(min_area)
        if max_area:
            query += " AND area <= ?"
            query_params.append(max_area)

        if property_filter == 'sale':
            if min_price:
                query += " AND price >= ?"
                query_params.append(min_price)
            if max_price:
                query += " AND price <= ?"
                query_params.append(max_price)
        else:
            if min_rent:
                query += " AND monthly_rent >= ?"
                query_params.append(min_rent)
            if max_rent:
                query += " AND monthly_rent <= ?"
                query_params.append(max_rent)
            if min_deposit:
                query += " AND deposite >= ?"
                query_params.append(min_deposit)
            if max_deposit:
                query += " AND deposite <= ?"
                query_params.append(max_deposit)

        query += " AND property_address LIKE ?"
        search_query = "%" + session.get('search_query', '') + "%"
        query_params.append(search_query)
        cur.execute(query, query_params)
        properties = cur.fetchall()

        property_list = []
        for property in properties:
            image_paths = property[8].replace('\\', '/').split(',') if property[8] else []
            image_paths = [path for path in image_paths if path]
            property_dict = {
                'property_id': property[0],
                'status': property[1],
                'property_type': property[2],
                'area': property[3],
                'price': property[4],
                'deposit': property[5],
                'monthly_rent': property[6],
                'address': property[7],
                'latitude': property[9],
                'longitude': property[10],
                'image_paths': image_paths
            }
            property_list.append(property_dict)
        return render_template('all_posts.html', properties=property_list)

@app.route("/favorited_posts",methods=['GET'])
def favorited_posts():
    if request.method == "GET":
        db=connect_db()
        cur=db.cursor()
        query1="SELECT property_id, status, property_type, area, price, deposite, monthly_rent, property_address, image_paths FROM properties inner join favorits on properties.property_id=favorits.post_id inner join users on favorits.userid=users.userid where users.userid='"+str(session['user_id'])+"'"
        cur.execute(query1)
        properties = cur.fetchall()
        property_list = []
        for property in properties:
            image_paths = property[8].replace('\\', '/').split(',') if property[8] else []
            image_paths = [path for path in image_paths if path]
            property_dict = {
                'property_id': property[0],
                'status': property[1],
                'property_type': property[2],
                'area': property[3],
                'price': property[4],
                'deposit': property[5],
                'monthly_rent': property[6],
                'address': property[7],
                'image_paths': image_paths
            }
            property_list.append(property_dict)
        return render_template('favorited_properties.html',properties=property_list)

@app.route('/user_properties',methods=['GET','POST'])
def user_properties():
    db=connect_db()
    cur=db.cursor()
    query="SELECT property_id, status, property_type, area, price, deposite, monthly_rent, property_address, image_paths FROM properties where userid='"+str(session['user_id'])+"'"
    cur.execute(query)
    properties = cur.fetchall()
    property_list = []
    for property in properties:
        image_paths = property[8].replace('\\', '/').split(',') if property[8] else []
        image_paths = [path for path in image_paths if path]
        property_dict = {
            'property_id': property[0],
            'status': property[1],
            'property_type': property[2],
            'area': property[3],
            'price': property[4],
            'deposit': property[5],
            'monthly_rent': property[6],
            'address': property[7],
            'image_paths': image_paths
        }
        property_list.append(property_dict)
    return render_template('user_properties1.html', properties=property_list)

@app.route('/chat', methods=['GET', 'POST'])
def chat():
    if 'user_id' not in session:
        return redirect(url_for('signin'))

    db = connect_db()
    cur = db.cursor()
    sender_id = session['user_id']

    if request.method == 'GET':
        receiver_username = request.args.get('username')
        receiverid_query = "SELECT userid FROM users WHERE username = ?"
        cur.execute(receiverid_query, (receiver_username,))
        receiver_id_t = cur.fetchone()
        receiver_id = receiver_id_t[0]
        post_query = """SELECT post_id FROM messages WHERE (receiver_id = ? AND sender_id = ?) 
                                    OR (receiver_id = ? AND sender_id = ?) ORDER BY timestamp DESC LIMIT 1"""
        cur.execute(post_query, (receiver_id, sender_id, sender_id, receiver_id))
        post_id_t = cur.fetchone()
        post_id = post_id_t[0]
        messages_query = """
        SELECT sender_id, receiver_id, message, timestamp, post_id
        FROM messages  
        WHERE (sender_id = ? AND receiver_id = ?) 
        UNION
        SELECT sender_id, receiver_id, message, timestamp, post_id
        FROM messages WHERE (sender_id = ? AND receiver_id = ?) 
        ORDER BY timestamp ASC
        """
        cur.execute(messages_query, (sender_id, receiver_id, receiver_id, sender_id))
        messages = cur.fetchall()
        return jsonify({'messages': messages, 'receiver_username': receiver_username, 'sender_id': sender_id, 'receiver_id': receiver_id})

    elif request.method == 'POST':
        data = request.json
        receiver_id = data['receiver_id']
        receiver_username = data['receiver_username']
        message = data['message']
        post_query = """
        SELECT post_id FROM messages WHERE (receiver_id = ? AND sender_id = ?) 
        OR (receiver_id = ? AND sender_id = ?) ORDER BY timestamp DESC LIMIT 1
        """
        cur.execute(post_query, (receiver_id, sender_id, sender_id, receiver_id))
        post = cur.fetchone()
        post_id = post[0] if post else None
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        query = "INSERT INTO messages (sender_id, receiver_id, post_id, message, timestamp) VALUES (?, ?, ?, ?, ?)"
        cur.execute(query, (sender_id, receiver_id, post_id, message, timestamp))
        db.commit()

        messages_query = """
        SELECT sender_id, receiver_id, message, timestamp, post_id
        FROM messages 
        WHERE (sender_id = ? AND receiver_id = ?) 
        UNION
        SELECT sender_id, receiver_id, message, timestamp, post_id
        FROM messages WHERE (sender_id = ? AND receiver_id = ?) 
        ORDER BY timestamp ASC
        """
        cur.execute(messages_query, (sender_id, receiver_id, receiver_id, sender_id))
        messages = cur.fetchall()
        return jsonify({'messages': messages, 'receiver_username': receiver_username, 'sender_id': sender_id, 'receiver_id': receiver_id})

@app.route('/conversations', methods=['GET'])
def conversations():
    user_id = session['user_id']
    db = connect_db()
    cur = db.cursor()
    query = """SELECT DISTINCT users.username
    FROM users
    INNER JOIN messages ON users.userid = messages.receiver_id
    WHERE messages.sender_id = ?
    UNION
    SELECT DISTINCT users.username
    FROM users
    INNER JOIN messages ON users.userid = messages.sender_id
    WHERE messages.receiver_id = ?"""
    cur.execute(query, (user_id, user_id))
    usernames = cur.fetchall()
    return render_template('chat.html', usernames=usernames)

@app.route('/chat_in_post', methods=['GET', 'POST'])
def chat_in_post():
    db=connect_db()
    cur=db.cursor()
    if request.method == 'GET':
        if session.get('user_id'):
            sender_id = session['user_id']
            receiver_id = session['post_owner_id']
            receiver_query = "SELECT username FROM users WHERE userid = ?"
            cur.execute(receiver_query, (receiver_id,))
            receiver = cur.fetchone()
            receiver_username = receiver[0]
            post_id = session['post_of_property_id']
            messages_query = """
                            SELECT sender_id, receiver_id, message, timestamp, post_id
                            FROM messages 
                            WHERE (sender_id = ? AND receiver_id = ?) 
                            UNION
                            SELECT sender_id, receiver_id, message, timestamp, post_id
                            FROM messages WHERE (sender_id = ? AND receiver_id = ?) 
                            ORDER BY timestamp ASC
                            """
            cur.execute(messages_query, (sender_id, receiver_id, receiver_id, sender_id))
            messages = cur.fetchall()
            return render_template('chat_in_post.html', messages=messages, receiver_username=receiver_username,
                                   sender_id=sender_id,
                                   receiver_id=receiver_id)
        else:
            return render_template('signin.html')
    elif request.method == 'POST':
        sender_id = session['user_id']
        receiver_id = request.form.get('receiver_id')
        receiver_username = request.form.get('receiver_username')
        message = request.form.get('message')
        post_query = """
        SELECT post_id FROM messages WHERE (receiver_id = ? AND sender_id = ?) 
        OR (receiver_id = ? AND sender_id = ?) ORDER BY timestamp DESC LIMIT 1
        """
        cur.execute(post_query, (receiver_id, sender_id, sender_id, receiver_id))
        post = cur.fetchone()
        post_id = post[0] if post else None
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        query = "INSERT INTO messages (sender_id, receiver_id, post_id, message, timestamp) VALUES (?, ?, ?, ?, ?)"
        cur.execute(query, (sender_id, receiver_id, post_id, message, timestamp))
        db.commit()

        messages_query = """
        SELECT sender_id, receiver_id, message, timestamp, post_id
        FROM messages 
        WHERE (sender_id = ? AND receiver_id = ?) 
        UNION
        SELECT sender_id, receiver_id, message, timestamp, post_id
        FROM messages WHERE (sender_id = ? AND receiver_id = ?) 
        ORDER BY timestamp ASC
        """
        cur.execute(messages_query, (sender_id, receiver_id, receiver_id, sender_id))
        messages = cur.fetchall()
        return render_template('chat_in_post.html', messages=messages, receiver_username=receiver_username, sender_id=sender_id,
                               receiver_id=receiver_id)

@app.route('/estimate_value', methods=['GET', 'POST'])
def estimate_value():
    if request.method == 'POST':
        property_type=request.form['propertyType']
        session['estimated_property_type']=property_type
        predict_year=request.form['predictYear']
        session['estimated_property_predict_year']=predict_year
        return render_template('map2.html')
    else:
        return render_template('estimate_value.html')

@app.route('/submit-address2', methods=['POST','GET'])
def submit_address2():
    if request.method == 'POST':
        data = request.json
        latlng = data.get('latlng')
        if latlng:
            latitude = latlng.get('lat')
            session['estimated_property_latitude']=latitude
            longitude = latlng.get('lng')
            session['estimated_property_longitude']=longitude
        return render_template('show_estimate.html')
    else:
        return render_template('map.html')


@app.route('/show_estimate', methods=['POST'])
def show_estimate():
    property_type=session.get('estimated_property_type')
    predict_year=session['estimated_property_predict_year']
    latitude=session.get('estimated_property_latitude')
    longitude=session.get('estimated_property_longitude')
    if property_type and predict_year and latitude and longitude:
        predict_year=float(predict_year)
        latitude=float(latitude)
        longitude=float(longitude)
        if property_type == 'villa':
            print('if villa')
            min_price = model.predict_villa_min(predict_year, latitude, longitude)
            print('min_price',min_price)
            max_price = model.predict_villa_max(predict_year, latitude, longitude)
        elif property_type == 'apartment':
            min_price = model.predict_apartment_min(predict_year, latitude, longitude)
            max_price = model.predict_apartment_max(predict_year, latitude, longitude)
        else:
            min_price = model.predict_land_min(predict_year, latitude, longitude)
            max_price = model.predict_land_max(predict_year, latitude, longitude)
        return jsonify({'min_price': min_price, 'max_price': max_price})
    else:
        return jsonify({'error': 'Missing property information in session.'}), 400

if __name__ == '__main__':
    app.run(debug=True)

