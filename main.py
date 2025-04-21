from werkzeug.security import check_password_hash
from werkzeug.security import generate_password_hash

import psycopg2
from flask import Flask, jsonify, request, send_file
from psycopg2 import connect, extras
from cryptography.fernet import Fernet
from os import environ
from dotenv import load_dotenv
from flask_cors import CORS
from flask import Flask, render_template
from flask import Flask, render_template, url_for, request, jsonify
import requests
import os
from psycopg2 import sql
import base64
from werkzeug.utils import secure_filename
import random
import string
import time
# from cgitb import html
from email.mime import image
from flask import Flask, render_template, request
import os
import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.image import load_img
import cv2
from keras.applications.vgg16 import VGG16
import numpy as np
from datetime import datetime


load_dotenv()
app = Flask(__name__)
cors = CORS(app, resources={r"/*": {"origins": "*"}})
key = Fernet.generate_key()


host = environ.get('DB_HOST')
database = environ.get('DB_NAME')
username = environ.get('DB_USER')
password = environ.get('DB_PASSWORD')
port = environ.get('DB_PORT')

# Auth database postgresql


def get_db_connection():
    conn = connect(host='dpg-cvrupa0gjchc73a3plg0-a.oregon-postgres.render.com',
                   database='ai_covid_scan',
                   user='ai_covid_scan_user',
                   password='cJDLzYKDo7RCl7ueWJvrpCdaJUfH7NZ4',
                   port=5432)

    return conn


def generate_random_string(length=8):
    letters_and_digits = string.ascii_letters + string.digits
    return ''.join(random.choice(letters_and_digits) for _ in range(length))


@app.route('/signup', methods=['POST'])
def signup():
    data = request.json
    email = data['email']
    password = data['password']

    # Hash the password
    hashed_password = generate_password_hash(password)

    # Check if email already exists
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=extras.RealDictCursor)
    cur.execute("SELECT * FROM admin_login WHERE email = %s", (email,))
    existing_user = cur.fetchone()

    if existing_user:
        return jsonify({'message': 'Email already exists!'}), 400

    # Insert new user into the database
    cur.execute("INSERT INTO admin_login (email, password) VALUES (%s, %s)",
                (email, hashed_password))
    conn.commit()
    cur.close()
    conn.close()

    return jsonify({'message': 'User registered successfully!'}), 201


@app.route('/login', methods=['POST'])
def login():
    data = request.json
    email = data['email']
    password = data['password']

    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=extras.RealDictCursor)
    cur.execute("SELECT * FROM admin_login WHERE email = %s", (email,))
    user = cur.fetchone()

    if user and check_password_hash(user['password'], password):
        return jsonify({'message': 'Login Successful'}), 200
    return jsonify({'message': 'Invalid email or password'}), 400


@app.route('/getpatients', methods=['GET'])
def get_patients():
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=extras.RealDictCursor)
        query = "SELECT * FROM scanner_patients"
        cur.execute(query)
        patients = cur.fetchall()
        cur.close()
        conn.close()

        # Exclude the 'xrayBase64' field
        for patient in patients:
            if 'xraybase64' in patient:
                del patient['xraybase64']

        if not patients:
            return jsonify({'message': 'No patients found'}), 404
        return jsonify(patients)
    except Exception as e:
        return jsonify({'message': str(e)}), 500


# ! ---------- ipmort model important
model = load_model('covid_prediction.h5')
# ! ---------- ipmort model important


@app.route('/scanner', methods=['POST'])
def scanner():
    try:
        new_scanner = request.get_json()
        firstname = new_scanner.get('firstname')
        lastname = new_scanner.get('lastname')
        phonenumber = new_scanner.get('phonenumber')
        cin = new_scanner.get('cin')
        birth = new_scanner.get('birth')
        base64_image = new_scanner.get('image')

        if not base64_image:
            return jsonify({"message": "No image data found."}), 400

        image_data = base64.b64decode(base64_image.split(',')[1])

        current_datetime = datetime.now()
        formatted_date = current_datetime.strftime('%Y-%m-%d-%H_%M')
        # Generate a unique filename
        timestamp = str(int(time.time()))
        random_string = generate_random_string()
        image_filename = f"scanner__{firstname}__{cin}__{formatted_date}_.png"
        image_path = os.path.join('./static/', image_filename)

        with open(image_path, 'wb') as f:
            f.write(image_data)

        im = cv2.imread(image_path)
        ima = cv2.resize(im, (160, 160))
        ima = ima.reshape(1, 160, 160, 3)
        prediction = model.predict(ima)
        class_labels = {
            0: 'Covid',
            1: 'Normal',
            2: 'Viral Pneumonia',
            3: 'error'
        }
        result = class_labels[np.argmax(prediction)]

        conn = get_db_connection()
        with conn.cursor() as cur:
            cur.execute("INSERT INTO scanner_patients (firstname,lastname,cin,phonenumber,birth,result,xraybase64) VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING *",
                        (firstname, lastname, cin, phonenumber, birth, result, base64_image))
            new_user = cur.fetchone()
            conn.commit()

        return jsonify({"result": result}), 201

    except KeyError as e:
        print(f"Error processing request: {e}")
        message = "Missing required field"
        return jsonify({"error": message}), 400

    except Exception as e:
        print(f"An error occurred: {e}")
        return jsonify({"message": "An error occurred while processing the request."}), 500


@app.route('/predict', methods=['POST', 'GET'])
def predict():
    name = request.form['Name']
    im = request.files['images']

    im.save('./static/images/{}'.format(im.filename))
    im = cv2.imread('./static/images/{}'.format(im.filename))
    im = np.asarray(im)
    ima = cv2.resize(im, (160, 160))
    ima = ima.reshape(1, 160, 160, 3)
    # im = load_img(im, target_size=(160, 160))
    # im = np.expand_dims(im, axis=0)
    prediction = model.predict(ima)
    class_predictions = np.argmax(prediction, axis=1)
    print(class_predictions)
    if class_predictions == 0:
        pred = 'Covid'
    elif class_predictions == 1:
        pred = 'Normal'
    elif class_predictions == 2:
        pred = 'Viral Pneumonia'
    message = pred
    # con = sqlite3.connect('sql_pr.sqlite3')
    # cur = con.cursor()
    # cur.execute("INSERT INTO classification (name, xray,prediction) values ('{}','{}','{}')".format(
    #     name, im, message))
    # print('added successfully to database !! ')
    # con.commit()
    # con.close()
    return message


@app.route('/', methods=['GET'])
def home():

    return jsonify('AI ScanCovid Server Application')


# if __name__ == '__main__':
#     print("welcome")
#     # port = int(os.environ.get('PORT', 5000))
#     app.run(debug=True, port=5000)
#     # app.run()
