import os
import shelve
from flask import Flask, request, render_template

app = Flask(__name__)

persist = shelve.open(os.path.realpath('store.dat'), writeback=True)
if 'entries' not in persist: persist['entries'] = []

@app.route('/')
def index():
    return render_template('index.html', entries=persist['entries'])

@app.route('/', methods=['POST'])
def add_note():
    text = request.form['text']
    persist['entries'].append(text)
    return render_template('index.html', entries=persist['entries'])
