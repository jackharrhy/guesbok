import os
import shelve
from flask import Flask, request, render_template
from jinja2 import Environment, BaseLoader

app = Flask(__name__)

persist = shelve.open(os.path.realpath('store.dat'), writeback=True)
if 'entries' not in persist: persist['entries'] = []

@app.route('/')
def index():
    return render_template('index.html', entries=persist['entries'])

def handle_entries():
    for entry in persist['entries']:
        try:
            template = Environment(loader=BaseLoader()).from_string(entry)
            yield template.render()
        except:
            yield entry

@app.route('/', methods=['POST'])
def add_note():
    text = request.form['text']
    persist['entries'].append(text)
    return render_template('index.html', entries=list(handle_entries()))
