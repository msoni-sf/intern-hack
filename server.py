from flask import Flask, render_template, url_for, redirect, request
import os
import bcrypt
from pprint import pprint
import json
from matching import is_matching

master_secret_key = 'a nice and random master secret key'
app = Flask(__name__)

if not os.path.exists('photos'):
    os.mkdir('photos')

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

    if type == 'register':
        if uname in users:
            return render_template('error.html', message='User already exists. Please login instead', callback='login_page', uname=None)
        else:
            users[uname] = {
                'name': uname,
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
        file.save(f'photos/{uname}/tmp.jpeg')

        for id in range(users[uname]['num_photos']):
            if is_matching(f'photos/{uname}/{id}.jpeg', f'photos/{uname}/tmp.jpeg', THRESH):
                return {
                    'error': False,
                    'message': '',
                    'redirect': f'/home/{uname}',
                }

        return {
            'error': True,
            'message': 'Could not authenticate. Make sure your face is clearly visible',
            'redirect': f'/home/{uname}',
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
        if not os.path.exists(f'photos/{uname}'):
            os.mkdir(f'photos/{uname}')

        file = request.files['img']
        file.save(f'photos/{uname}/{users[uname]["num_photos"]}.jpeg')
        users[uname]["num_photos"] += 1

        with open('database.db','w') as f:
            json.dump(users, f, indent=4)

        return {
            'error': False,
            'message': '',
            'redirect': f'/home/{uname}',
        }

## Run server
if __name__ == '__main__':
    app.jinja_env.auto_reload = True
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.run(debug=True, port=1234)
