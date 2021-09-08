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
from bson.json_util import dumps
from flask import Response

cluster = MongoClient('mongodb://localhost:27017/?readPreference=primary&appname=MongoDB%20Compass&directConnection=true&ssl=false')
db = cluster['test']
collection = db['test2']


change_stream = collection.watch()

for change in change_stream:
    print(dumps(change))
    print('') # for readability only
