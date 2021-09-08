from flask import Flask, jsonify, request
from elasticsearch import Elasticsearch
from requests.auth import HTTPBasicAuth
from pymongo import MongoClient
from flask import Response
import requests
import pymongo
import aiohttp
import asyncio
import json
import os
import re

cluster = MongoClient('mongodb://localhost:27017/?readPreference=primary&appname=MongoDB%20Compass&directConnection=true&ssl=false')

es = Elasticsearch()

app = Flask(__name__)

db = cluster['test']
collection = db['test']


def get_eur_price():
    ''' Find value of euro and return it '''
    req = requests.get('https://www.bnm.md/ro')
    x = re.search(r"EUR[\s\S]*?class=\"rate down\">(.*?)</span>", req.text).group(1)
    return float(x)


async def get(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url, auth=aiohttp.BasicAuth(os.environ['API_TOKEN']  , '')) as response:
            data = await response.read()
            return data


def get_adverts_info():
    ''' Get all the ads and make an asynchronous request for each to get detailed information about the ad '''
    r = requests.get('https://partners-api.999.md/adverts?page_size=10&page=1', auth=HTTPBasicAuth(os.environ['API_TOKEN'], ''))
    json_data = r.json()

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    coroutines = []

    for advert in json_data['adverts']:
        id = advert['id']
        coroutines.append(get(f'https://partners-api.999.md/adverts/{id}?lang=ru'))

    result = loop.run_until_complete(asyncio.gather(*coroutines))

    return result


def convert_eur_to_mdl(advert):
    ''' Convert euro to mdl at the current exchange rate '''
    eur_price = get_eur_price()

    data = json.loads(advert)
    if data['price']['unit'] == 'eur':
        data['price']['unit'] = 'mdl'
        data['price']['value'] = float(data['price']['value']) * eur_price

    return data


@app.route('/step_1')
def get_adverts():
    ''' Get all adverts from api response and return its '''
    r = requests.get('https://partners-api.999.md/adverts?page_size=10&page=1', auth=HTTPBasicAuth(os.environ['API_TOKEN'], ''))
    return r.json()


@app.route('/step_2')
def save_adverts_to_db():
    ''' Get all adverts from api response and save in bd '''
    r = requests.get('https://partners-api.999.md/adverts?page_size=10&page=1', auth=HTTPBasicAuth(os.environ['API_TOKEN'], ''))
    inserted_id = collection.insert_one(r.json()).inserted_id
    if inserted_id:
        return f'success, inserted id {inserted_id}'


@app.route('/step_3')
def convert_and_save_to_db():
    ''' For adverts that have currency in euros, convert to mdl and save in bd '''
    adverts = get_adverts_info()
    for advert in adverts:
        advert = convert_eur_to_mdl(advert)
        collection.insert_one(advert)

    return 'success'


@app.route('/step_4')
def tracking_changes():
    ''' Tracking changes between adverts from db and from api response '''
    adverts = get_adverts_info()

    for advert in adverts[:4]:
        advert = convert_eur_to_mdl(advert)
        advert_exist = collection.find_one({'id': advert['id']})

        print(advert['id'])

        if advert_exist: del advert_exist['_id']

        if advert_exist and advert == advert_exist:
            continue
        elif advert_exist:
            collection.delete_one(advert_exist)

        collection.insert_one(advert)
    
    return 'success'


@app.route('/step_5')
def synchronize_with_es():
    adverts = collection.find()

    i = 1
    for advert in adverts:
        del advert['_id']
        es.index(index='adverts', doc_type='_doc', id=i, body=advert)
        i += 1
    
    return 'success'