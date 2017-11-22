#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re
import json
import urllib2
from urllib2 import urlopen
from os import system
from time import sleep
from decimal import *
import sys
import operator
import sqlite3

# select name, bnet, hero from heroes
SQL = {}
SQL['createHeroTable'] = 'CREATE TABLE heroes (id integer primary key autoincrement, name text, bnet text, hero text)'
SQL['createParagonTable'] = 'CREATE TABLE paragon (id integer primary key autoincrement, bnet text, level integer, checked datetime)'
SQL['createItemTable'] = 'CREATE TABLE items (id integer primary key autoincrement, bnet text, toolTip text, checked datetime)'
SQL['getHeroes'] = 'select name, bnet, hero from heroes'
SQL['getConfig'] = 'select item, value from config'
SQL['inParagon'] = "INSERT INTO paragon (`id`,`bnet`,`level`,`checked`) VALUES (NULL,'{bnet}', {paragon}, datetime('now'))"

URL = {}
URL['PROFILE'] = 'https://us.api.battle.net/d3/profile/{bnetTag}/hero/{heroId}?locale=en_US&apikey={bnetAPI}'
URL['ITEM'] = 'https://us.api.battle.net/d3/data/{tooltipString}?locale=en_US&apikey={bnetAPI}'

CONFIG = {}
CONFIG['BNET_API'] = None
CONFIG['GROUPME_API'] = None


def groupme_announce(text):
    url = "https://api.groupme.com/v3/bots/post"
    jdata = json.dumps({'bot_id': CONFIG['GROUPME_API'], 'text': text})
    urllib2.urlopen(url, jdata)


def get_hero(bnetTag, hero):
    request = URL['PROFILE'].format(bnetTag=bnetTag, heroId=hero, bnetAPI=CONFIG['BNET_API'])
    result = get_json_data(request)
    return result


def get_item(tooltipString):
    request = URL['ITEM'].format(tooltipString=tooltipString, bnetAPI=CONFIG['BNET_API'])
    result = get_json_data(request)
    return result


def get_json_data(source):
    try:
        data = urlopen(source).read()
    except Exception, e:
        print "error reading: " + source
        return None

    obj = json.loads(data)
    return obj


def load_config():
    global conn
    confData = conn.execute(SQL['getConfig'])
    for item, value in confData:
        CONFIG[item] = value


###
conn = sqlite3.connect('d3.db')

load_config()
if (CONFIG['BNET_API'] is None or CONFIG['GROUPME_API'] is None):
    sys.exit('Error loading config data!')

# load hero data
heroData = conn.execute(SQL['getHeroes'])

for name, bnet, hero in heroData:
    userMsg = None
    data = get_hero(bnetTag=bnet, hero=hero)

    if (data is None):
        print 'Error getting data for {bnetTag} hero: {hero}'.format(bnetTag=bnet, hero=hero)
        continue

    name = str(data['name'])
    paragon = str(data['paragonLevel'])
    userMsg = '{name} / {paragon} paragon / {damage:,} dmg\n'.format(name=name, paragon=paragon, damage=int(data['stats']['damage']))  # start user message
    sqlString = SQL['inParagon'].format(bnet=bnet, paragon=paragon)
    print sqlString
    conn.execute(sqlString)
    conn.commit()
    for currentItem in data['items']:
        item = data['items'][currentItem]

        typeName = get_item(item['tooltipParams'])['typeName']
        typePrefix = None
        if (typeName.startswith('Primal')):
            typePreix = 'Primal Ancient'

        if (typeName.startswith('Ancient')):
            typePrefix = 'Ancient'

        if (typePrefix is not None):
            userMsg += ' {typePrefix} {name}\n'.format(typePrefix=typePrefix, name=item['name'])

    if (userMsg is not None):
        print userMsg
        #groupme_announce(userMsg)

conn.close()
