from flask import Flask, render_template, url_for, redirect, request
import os
import bcrypt
from pprint import pprint

master_secret_key = 'a nice and random master secret key'

if not os.path.exists('photos'):
    os.mkdir('photos')

app = Flask(__name__)
users = dict()
THRESH = 0.5

## Show frontend pages
@app.route('/', methods=['GET'])
def login_page():
    pprint(users)
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

@app.route('/webcam', methods=['GET'])
def webcam_page():
    return render_template('webcam.html')

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
                'pass': bcrypt.hashpw((password + master_secret_key).encode(), bcrypt.gensalt()),
                'logged_in': True,
                'num_photos': 0,
            }
            return redirect(url_for('home_page',uname=uname))

    elif type == 'login':
        if uname not in users:
            return render_template('error.html', message='User does not exist. Please register instead', callback='login_page', uname=None)
        else:
            if bcrypt.checkpw((password+master_secret_key).encode(), users[uname]['pass']):
                users[uname]['logged_in'] = True
                return redirect(url_for('home_page', uname=uname))
            else:
                return render_template('error.html', message='Password doesn\'t match', callback='login_page', uname=None)

@app.route('/api/webcam_auth/<uname>', methods=['POST'])
def webcam_auth(uname):
    if uname not in users:
        return render_template('error.html', message='User does not exist', callback='webcam_page', uname=None)
    elif users[uname]['num_photos'] == 0:
        pass # go to add photos page
    else:
        file = request.files['img']
        file.save(f'photos/users/tmp.jpeg')

    return redirect(url_for('home_page'))

## Run server
if __name__ == '__main__':
    app.jinja_env.auto_reload = True
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.run(debug=True, port=1234)
