import os
import shelve
import shortuuid
from flask import Flask, request, render_template, jsonify, Response, abort

app = Flask(__name__)

persist = shelve.open(os.path.realpath('store.dat'), writeback=True)

# persist.clear()

if 'entries' not in persist: persist['entries'] = {}

def new_id():
    return shortuuid.uuid()

# persist['entries'][new_id()] = 'hello'
# persist['entries'][new_id()] = 'world'
# persist['entries'][new_id()] = '<b>:)</b>'

def new_entry(text):
    persist['entries'][new_id()] = text

def delete_entries(uids):
    for uid in uids:
        if uid in persist['entries']: del persist['entries'][uid]

@app.route('/api/entries')
def all_entries():
    return jsonify(persist['entries'])

@app.route('/api/entries', methods=['POST'])
def new_entry_via_api():
    new_entry(request.get_data())
    return Response(status=204)

@app.route('/api/entries/<uid>')
def grab_by_uid_via_api(uid):
    if uid in persist['entries']: return jsonify(persist['entries'][uid])
    Response(status=404)

def render(filename):
    return render_template('{}.html'.format(filename), entries=persist['entries'])

@app.route('/')
def index():
    return render('index')

@app.route('/<uid>')
def grab_by_uid(uid):
    if uid in persist['entries']: return persist['entries'][uid]
    abort(404)

@app.route('/clean')
def clean():
    return render('clean')

@app.route('/clean', methods=['POST'])
def nuke():
    delete_entries(request.form)
    return render('clean')

