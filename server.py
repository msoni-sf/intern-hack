from flask import Flask, render_template, url_for, redirect, request
import os
import bcrypt

master_secret_key = 'a nice and random master secret key'

if not os.path.exists('photos'):
    os.mkdir('photos')

app = Flask(__name__)
users = dict()

## Show frontend pages
@app.route('/', methods=['GET'])
def login_page():
    return render_template('login.html')

@app.route('/home', methods=['GET'])
def home_page():
    return render_template('home.html')

@app.route('/settings', methods=['GET'])
def settings_page():
    return render_template('settings.html')

@app.route('/webcam', methods=['GET'])
def webcam_page():
    return render_template('webcam.html')

@app.route('/api/login', methods=['POST'])
def login():
    type = request.form['type']
    uname = request.form.get('uname')
    password = request.form.get('pass')

    if type == 'register':
        if uname in users:
            return render_template('error.html', message='User already exists. Please login instead', callback='login_page')
        else:
            users[uname] = {
                'name': uname,
                'pass': bcrypt.hashpw((password + master_secret_key).encode(), bcrypt.gensalt()),
                'num_photos': 0,
            }
            return redirect(url_for('home_page'))

    elif type == 'login':
        if uname not in users:
            return render_template('error.html', message='User does not exist. Please register instead', callback='login_page')
        else:
            return redirect(url_for('home_page'))

@app.route('/api/webcam_auth', methods=['POST'])
def webcam_auth():
    print(request.files)
    file = request.files['img']
    file.save('photos/img.jpeg')


    return redirect(url_for('webcam_page'))

## Run server
if __name__ == '__main__':
    app.jinja_env.auto_reload = True
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.run(debug=True, port=1234)
