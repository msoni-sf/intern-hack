from flask import Flask, render_template, url_for, redirect, request
import os
import bcrypt
from pprint import pprint
import json
from matching import is_matching
from email_generator import generateOTP, email_alert
import io
from base64 import encodebytes
from PIL import Image
from flask import jsonify

master_secret_key = 'a nice and random master secret key'
app = Flask(__name__)

if not os.path.exists('static/photos'):
    os.mkdir('static/photos')

users = dict()

try:
    with open('database.db') as f:
        users = json.load(f)
    for user in users:
        users[user]['logged_in'] = False
except:
    pass

THRESH = 0.7

## Show frontend pages
@app.route('/', methods=['GET'])
def login_page():
    #pprint(users)
    return render_template('login.html')

@app.route('/home/<uname>', methods=['GET'])
def home_page(uname):
    if uname not in users or not users[uname]['logged_in']:
        return render_template('error.html', message='User does not exist or not logged in', callback='login_page', uname=None)
    else:
        return render_template('home.html', uname=uname)

@app.route('/settings', methods=['GET'])
def settings_page():
    return render_template('settings.html')

@app.route('/webcam/<uname>', methods=['GET'])
def webcam_page(uname):
    return render_template('webcam.html', uname=uname)

@app.route('/add_photo/<uname>', methods=['GET'])
def photo_add_page(uname):
    return render_template('photo_add.html', uname=uname)

@app.route('/show_photo/<uname>', methods=['GET'])
def photo_show_page(uname):
    return render_template('photo_show.html', uname=uname,num=users[uname]['num_photos'])

@app.route('/otp/<uname>', methods=['GET'])
def otp_page(uname):
    return render_template('otp.html', uname=uname,)

## Backend APIs
@app.route('/api/logout/<uname>', methods=['GET'])
def logout(uname):
    if uname not in users:
        return render_template('error.html', message='User does not exist', callback='login_page', uname=uname)

    users[uname]['logged_in'] = False
    return redirect(url_for('login_page'))

@app.route('/api/login', methods=['POST'])
def login():
    type = request.form['type']
    uname = request.form.get('uname')
    password = request.form.get('pass')
    email = request.form.get('email')

    if type == 'register':
        if uname in users:
            return render_template('error.html', message='User already exists. Please login instead', callback='login_page', uname=None)
        else:
            users[uname] = {
                'name': uname,
                'email': email,
                'pass': bcrypt.hashpw((password + master_secret_key).encode(), bcrypt.gensalt()).decode(),
                'logged_in': True,
                'num_photos': 0,
            }
            with open('database.db','w') as f:
                json.dump(users, f, indent=4)

            return redirect(url_for('webcam_page',uname=uname))

    elif type == 'login':
        if uname not in users:
            return render_template('error.html', message='User does not exist. Please register instead', callback='login_page', uname=None)
        else:
            if bcrypt.checkpw((password+master_secret_key).encode(), users[uname]['pass'].encode()):
                users[uname]['logged_in'] = True
                return redirect(url_for('webcam_page', uname=uname))
            else:
                return render_template('error.html', message='Password doesn\'t match', callback='login_page', uname=None)

@app.route('/api/webcam_auth', methods=['POST'])
def webcam_auth():
    uname = request.form['uname']
    if uname not in users:
        return {
            'error': True,
            'message': 'User does not exist',
            'redirect': '/',
        }
    elif users[uname]['num_photos'] == 0:
        return {
            'error': True,
            'message': 'You have not added any photos. Please add a photo to enable 2FA',
            'redirect': f'/home/{uname}',
        }
    else:
        file = request.files['img']
        file.save(f'static/photos/{uname}/tmp.jpeg')

        for id in range(users[uname]['num_photos']):
            if is_matching(f'static/photos/{uname}/{id}.jpeg', f'static/photos/{uname}/tmp.jpeg', THRESH):
                return {
                    'error': False,
                    'message': '',
                    'redirect': f'/home/{uname}',
                }

        return {
            'error': True,
            'message': 'Could not authenticate. Make sure your face is clearly visible',
            'redirect': f'/webcam/{uname}',
        }

@app.route('/api/photo_add', methods=['POST'])
def photo_add():
    uname = request.form['uname']
    if uname not in users:
        return {
            'error': True,
            'message': 'User does not exist',
            'redirect': f'/home/{uname}',
        }
    else:
        if not os.path.exists(f'static/photos/{uname}'):
            os.mkdir(f'static/photos/{uname}')

        file = request.files['img']
        file.save(f'static/photos/{uname}/{users[uname]["num_photos"]}.jpeg')
        users[uname]["num_photos"] += 1

        with open('database.db','w') as f:
            json.dump(users, f, indent=4)

        return {
            'error': False,
            'message': '',
            'redirect': f'/home/{uname}',
        }

@app.route('/api/otp_generate/<uname>', methods=['GET'])
def otp_generate(uname):
    if uname not in users:
        return render_template('error.html', message='User does not exist', callback='webcam_page', uname=uname)
    else:
        otp = generateOTP()
        users[uname]['otp'] = otp
        email_alert('One-time OTP for Inern-Hackathon Project', 'Hey user, your OTP is as follows: ' + otp, users[uname]['email'])
        return redirect(url_for('otp_page', uname=uname))

@app.route('/api/otp_verify', methods=['POST'])
def otp_auth():
    otp = request.form['otp']
    uname = request.form['uname']
    if uname not in users:
        return render_template('error.html', message='User does not exist', callback='otp_page', uname=uname)
    elif otp == users[uname]['otp']:
        return redirect(url_for('home_page', uname=uname))
    else:
        return render_template('error.html', message='Incorrect OTP', callback='otp_page', uname=uname)

def get_response_image(image_path):
    pil_img = Image.open(image_path, mode='r') # reads the PIL image
    byte_arr = io.BytesIO()
    pil_img.save(byte_arr, format='PNG') # convert the PIL image to byte array
    encoded_img = encodebytes(byte_arr.getvalue()).decode('ascii') # encode as base64
    return encoded_img

@app.route('/api/imgs/<uname>',methods=['GET'])
def get_images(uname):
    encoded_imges = []
    for id in range(users[uname]['num_photos']):
        encoded_imges.append(get_response_image(f'static/photos/{uname}/{id}.jpeg'))
    return jsonify({'result': encoded_imges})

## Run server
if __name__ == '__main__':
    app.jinja_env.auto_reload = True
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.run(debug=True, port=1234)
