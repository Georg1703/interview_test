from flask import Flask, jsonify, request
import requests
from requests.auth import HTTPBasicAuth
import json
import pymongo
from pymongo import MongoClient

cluster = MongoClient('mongodb://localhost:27017/?readPreference=primary&appname=MongoDB%20Compass&directConnection=true&ssl=false')

app = Flask(__name__)


@app.route('/')
def index():
    r = requests.get('https://partners-api.999.md/adverts?page_size=10&page=1', auth=HTTPBasicAuth('apuUo-UF6yhfoNVVTKWrb5Z8ecru', ''))
    return r.json()


@app.route('/db')
def db():
    db = cluster['test']
    collection = db['test']
    r = requests.get('https://partners-api.999.md/adverts?page_size=10&page=1', auth=HTTPBasicAuth('apuUo-UF6yhfoNVVTKWrb5Z8ecru', ''))
    collection.insert_one(r.json())
    return 'success'
    