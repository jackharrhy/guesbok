import os
import shelve
import shortuuid
from flask import (
    Flask, request, render_template, jsonify,
    Response, abort, redirect, url_for
)
from flask_jwt_extended import (
    JWTManager, jwt_required, create_access_token,
    jwt_refresh_token_required, create_refresh_token,
    get_jwt_identity, set_access_cookies,
    set_refresh_cookies, unset_jwt_cookies
)
from dotenv import load_dotenv

load_dotenv()
secret_passcode = os.getenv('GUESBOK_PASSCODE')

persist = shelve.open(os.path.realpath('store.dat'), writeback=True)

persist.clear()

if 'entries' not in persist: persist['entries'] = {}


def new_id():
    return shortuuid.uuid()


persist['entries'][new_id()] = 'hello'
persist['entries'][new_id()] = 'world'
persist['entries'][new_id()] = '<b>:)</b>'


def new_entry(text):
    persist['entries'][new_id()] = text


def delete_entries(uids):
    print(uids)
    for uid in uids:
        if uid in persist['entries']: del persist['entries'][uid]


app = Flask(__name__)
app.config['JWT_TOKEN_LOCATION'] = ['cookies']
app.config['JWT_COOKIE_SECURE'] = False
app.config['JWT_COOKIE_CSRF_PROTECT'] = True
app.config['JWT_SECRET_KEY'] = 'super-secret'  # Change this!

jwt = JWTManager(app)


@app.route('/login', methods=['POST'])
def handle_web_login():
    print(request)
    passcode = request.form.get('passcode', None)
    if not passcode:
        abort(400)
    if passcode != secret_passcode:
        abort(401)

    access_token = create_access_token(identity="cleaner")
    refresh_token = create_refresh_token(identity="cleaner")
    resp = redirect(url_for('clean'))
    set_access_cookies(resp, access_token)
    set_refresh_cookies(resp, refresh_token)
    return resp


@app.route('/token/auth', methods=['POST'])
def token_via_json():
    passcode = request.json.get('passcode', None)
    if not passcode:
        return jsonify({'msg': 'Missing passcode parameter'}), 400
    if passcode != secret_passcode:
        return jsonify({'msg': 'Bad passcode'}), 401

    access_token = create_access_token(identity="cleaner")
    return jsonify({'access_token': access_token}), 20


@app.route('/token/refresh', methods=['POST'])
@jwt_refresh_token_required
def refresh():
    current_user = get_jwt_identity()
    access_token = create_access_token(identity=current_user)
    resp = jsonify({'refresh': True})
    set_access_cookies(resp, access_token)
    return resp, 200


@app.route('/token/remove', methods=['POST'])
def logout():
    resp = jsonify({'logout': True})
    unset_jwt_cookies(resp)
    return resp, 200


@app.route('/api/entries/')
def all_entries():
    return jsonify(persist['entries'])


@app.route('/api/entries/', methods=['POST'])
@jwt_required
def new_entry_via_api():
    new_entry(request.get_data())
    return '', 204


@app.route('/api/entries/<uid>')
def grab_by_uid_via_api(uid):
    if uid in persist['entries']: return jsonify(persist['entries'][uid])
    return '', 404


def render(filename):
    return render_template('{}.html'.format(filename), entries=persist['entries'])


@app.route('/')
def index():
    return render('index')


@app.route('/', methods=['POST'])
def add_entry():
    new_entry(request.form['text'])
    return render('index')


@app.route('/<uid>')
def grab_by_uid(uid):
    if uid in persist['entries']: return persist['entries'][uid]
    abort(404)


@app.route('/login')
def show_login_page():
    return render('login')


@app.route('/clean')
@jwt_required
def clean():
    return render('clean')


@app.route('/clean', methods=['POST'])
@jwt_required
def nuke():
    delete_entries(request.form)
    return render('clean')