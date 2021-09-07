from flask import Flask, jsonify, request
from requests.auth import HTTPBasicAuth
from pymongo import MongoClient
import requests
import pymongo
import aiohttp
import asyncio
import json
import os
import re
import time
from flask import Response

cluster = MongoClient('mongodb://localhost:27017/?readPreference=primary&appname=MongoDB%20Compass&directConnection=true&ssl=false')


app = Flask(__name__)

db = cluster['test']
collection = db['test']


@app.route('/get_adverts')
def step_one():
    r = requests.get('https://partners-api.999.md/adverts?page_size=10&page=1', auth=HTTPBasicAuth('apuUo-UF6yhfoNVVTKWrb5Z8ecru', ''))
    return r.json()


@app.route('/save_adverts_to_db')
def save_adverts_to_db():
    r = requests.get('https://partners-api.999.md/adverts?page_size=10&page=1', auth=HTTPBasicAuth('apuUo-UF6yhfoNVVTKWrb5Z8ecru', ''))
    collection.insert_one(r.json())
    return 'success'


def get_eur_price():
    req = requests.get('https://www.bnm.md/ro')
    x = re.search(r"EUR[\s\S]*?class=\"rate down\">(.*?)</span>", req.text).group(1)
    return float(x)


async def get(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url, auth=aiohttp.BasicAuth('apuUo-UF6yhfoNVVTKWrb5Z8ecru', '')) as response:
            data = await response.read()
            return data


@app.route('/convert_and_save')
def convert_and_save():
    eur_price = get_eur_price()
    json_data = db.test.find_one()

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    coroutines = []

    for advert in json_data['adverts']:
        id = advert['id']
        coroutines.append(get(f'https://partners-api.999.md/adverts/{id}?lang=ru'))

    result = loop.run_until_complete(asyncio.gather(*coroutines))

    for advert in result[:2]:
        print('-------')
        data = json.loads(advert)
        if data['price']['unit'] == 'eur':
            data['price']['unit'] = 'mdl'
            data['price']['value'] = float(data['price']['value']) * eur_price
        collection.insert_one(data)