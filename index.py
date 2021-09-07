from flask import Flask, jsonify, request
from requests.auth import HTTPBasicAuth
from pymongo import MongoClient
import requests
import pymongo
import json
import os
import re
from flask import Response

cluster = MongoClient('mongodb://localhost:27017/?readPreference=primary&appname=MongoDB%20Compass&directConnection=true&ssl=false')


app = Flask(__name__)

db = cluster['test']
collection = db['test']

@app.route('/get_adverts')
def step_one():
    r = requests.get('https://partners-api.999.md/adverts?page_size=10&page=1', auth=HTTPBasicAuth('apuUo-UF6yhfoNVVTKWrb5Z8ecru', ''))
    return r.json()


@app.route('/db')
def step_two():
    r = requests.get('https://partners-api.999.md/adverts?page_size=10&page=1', auth=HTTPBasicAuth('apuUo-UF6yhfoNVVTKWrb5Z8ecru', ''))
    collection.insert_one(r.json())
    return 'success'


def get_eur_price():
    req = requests.get('https://www.bnm.md/ro')
    x = re.search(r"EUR[\s\S]*?class=\"rate down\">(.*?)</span>", req.text).group(1)
    return float(x)


@app.route('/convert')
def step_three():
    eur_price = get_eur_price()
    json_data = db.test.find_one()

    for advert in json_data['adverts']:
        id = advert['id']
        r = requests.get(f'https://partners-api.999.md/adverts/{id}?lang=ru', auth=HTTPBasicAuth('apuUo-UF6yhfoNVVTKWrb5Z8ecru', ''))
        json_data = r.json()

        if json_data['price']['unit'] == 'eur':
            actual_price = float(json_data['price']['value']) * eur_price
            print("{:.4f}".format(actual_price))