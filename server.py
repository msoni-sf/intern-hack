from flask import Flask, render_template, url_for
app = Flask(__name__)

@app.route('/')
def index_page():
    return render_template('login.html')

@app.route('/home')
def home_page():
    return render_template('home.html')

@app.route('/settings')
def settings_page():
    return render_template('settings.html')

@app.route('/webcam')
def webcam_page():
    return render_template('webcam.html')

if __name__ == '__main__':
    app.jinja_env.auto_reload = True
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.run(debug=True, port=1234)
