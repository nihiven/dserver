import json
import urllib2
import sqlite3
import sys

SQL = {}  # holds all of our sql queries
# battle.net related
SQL['createProfilesTable'] = "CREATE TABLE profiles (id integer primary key autoincrement, battleTag text, guildName text, paragonLevelSoftcore integer, paragonLevelHardcore integer, paragonLevelSeason integer, lastUpdate datetime)"
SQL['createHeroesTable'] = 'CREATE TABLE heroes (id integer primary key autoincrement, heroId text, seasonal boolean, level integer, hardcore boolean, class text)'
SQL['createParagonHistoryTable'] = 'CREATE TABLE paragonHistory (id integer primary key autoincrement, bnet text, level integer, checked datetime)'
SQL['createItemTable'] = 'CREATE TABLE items (id integer primary key autoincrement, bnet text, toolTip text, checked datetime)'
SQL['updateProfile'] = "UPDATE profiles SET guildName='{guildName}', paragonLevelSoftcore='{paragonLevelSoftcore}', paragonLevelHardcore='{paragonLevelHardcore}', paragonLevelSeason='{paragonLevelSeason}', lastUpdate=datetime('now') where battleTag = '{battleTag}'"
SQL['addProfile'] = "INSERT INTO profiles (id, battleTag, guildName, paragonLevelSoftcore, paragonLevelHardcore, paragonLevelSeason, lastUpdate) VALUES (NULL, '{battleTag}', '{guildName}', '{paragonLevelSoftcore}', '{paragonLevelHardcore}', '{paragonLevelSeason}', datetime('now'))"
SQL['isProfile'] = "select count(1) from profiles where battleTag='{battleTag}'"
SQL['getHeroes'] = 'select name, bnet, hero from heroes'
SQL['inParagon'] = "INSERT INTO paragon (`id`,`bnet`,`level`,`checked`) VALUES (NULL,'{bnet}', {paragon}, datetime('now'))"
# app related
SQL['getConfig'] = 'select item, value from config'

URL = {}  # holds all of our API calls
URL['PROFILE'] = 'https://us.api.battle.net/d3/profile/{battleTag}/?locale=en_US&apikey={bnetAPI}'
URL['HERO'] = 'https://us.api.battle.net/d3/profile/{battleTag}/hero/{heroId}?locale=en_US&apikey={bnetAPI}'
URL['ITEM'] = 'https://us.api.battle.net/d3/data/{tooltipString}?locale=en_US&apikey={bnetAPI}'

CONFIG = {}  # holds all of our configuration variables
CONFIG['BNET_API'] = None

conn = sqlite3.connect('d3.db')


def is_profile_db(battleTag):
    global conn, SQL
    query = SQL['isProfile'].format(battleTag=battleTag)
    cursor = conn.execute(query)
    row = cursor.fetchone()
    if (row[0] == 0):
        return False

    return True


def get_profile_api(battleTag):
    global URL
    request = URL['PROFILE'].format(battleTag=battleTag, bnetAPI=CONFIG['BNET_API'])
    profile = get_json_data(request)
    return profile


def get_hero_api(battleTag, hero):
    global URL
    request = URL['HERO'].format(battleTag=battleTag, heroId=hero, bnetAPI=CONFIG['BNET_API'])
    result = get_json_data(request)
    return result


def get_item_api(tooltipString):
    global URL
    request = URL['ITEM'].format(tooltipString=tooltipString, bnetAPI=CONFIG['BNET_API'])
    result = get_json_data(request)
    return result


def get_json_data(source):
    try:
        data = urllib2.urlopen(source).read()
    except Exception, e:
        print "error reading: " + source, e
        return None

    obj = json.loads(data)
    return obj


def load_config():
    global conn, SQL
    confData = conn.execute(SQL['getConfig'])
    for item, value in confData:
        CONFIG[item] = value


def add_profile_db(battleTag):
    global conn, SQL
    profile = get_profile_api(battleTag)
    if (profile is None):
        return None

    conn.execute(SQL['addProfile'].format(
        battleTag=battleTag,
        guildName=profile['guildName'],
        paragonLevelSoftcore=profile['paragonLevel'],
        paragonLevelHardcore=profile['paragonLevelHardcore'],
        paragonLevelSeason=profile['paragonLevelSeason']
    ))
    conn.commit()
    return profile


def update_profile_db(battleTag):
    global conn, SQL
    profile = get_profile_api(battleTag)
    if (profile is None):
        return None

    conn.execute(SQL['updateProfile'].format(
        battleTag=battleTag,
        guildName=profile['guildName'],
        paragonLevelSoftcore=profile['paragonLevel'],
        paragonLevelHardcore=profile['paragonLevelHardcore'],
        paragonLevelSeason=profile['paragonLevelSeason']
    ))
    conn.commit
    return profile


# this is meant to update everything so do your work here
def do_profile(battleTag):
    profile = None
    if (is_profile_db(battleTag=battleTag)):
        profile = update_profile_db(battleTag=battleTag)
        print 'update'
    else:
        profile = add_profile_db(battleTag=battleTag)
        print 'add'

    if (profile is None):
        return False

    for hero in profile['heroes']:
        print hero['seasonal'], hero['level'], hero['name'], hero['hardcore'], hero['class'], hero['id']




###
load_config()
if (CONFIG['BNET_API'] is None):
    sys.exit('Error loading config data!')

# load external processing queue

# load hero data
battleTag = 'nihiven-1513'
profile = None
do_profile(battleTag)
conn.close()
