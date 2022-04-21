import json
import os
import shelve
import pprint
from flask import Flask, request, render_template
from jinja2 import Environment, BaseLoader

app = Flask(__name__)

persist = shelve.open(os.path.realpath('store.dat'), writeback=True)
if 'entries' not in persist: persist['entries'] = []

def fetch_context():
    return {**globals(), **locals()}

def handle_entries():
    for entry in persist['entries']:
        try:
            template = Environment(loader=BaseLoader()).from_string(entry)
            yield template.render(**fetch_context())
        except Exception as e:
            yield entry

@app.route('/')
def index():
    return render_template('index.html', **fetch_context(), entries=list(handle_entries()))

@app.route('/', methods=['POST'])
def add_note():
    text = request.form['text']
    persist['entries'].append(text)
    return render_template('index.html', **fetch_context(), entries=list(handle_entries()))
