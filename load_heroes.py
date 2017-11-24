import json
import urllib2
import sqlite3
import sys


class SQL:
    # profile
    createProfilesTable = "CREATE TABLE profiles (id integer primary key autoincrement, battleTag text, guildName text, paragonLevelSoftcore integer, paragonLevelHardcore integer, paragonLevelSeason integer, lastUpdate datetime)"
    isProfile = "select count(1) from profiles where battleTag='{battleTag}'"
    updateProfile = "UPDATE profiles SET guildName='{guildName}', paragonLevelSoftcore='{paragonLevelSoftcore}', paragonLevelHardcore='{paragonLevelHardcore}', paragonLevelSeason='{paragonLevelSeason}', lastUpdate=datetime('now') where battleTag = '{battleTag}'"
    addProfile = "INSERT INTO profiles (id, battleTag, guildName, paragonLevelSoftcore, paragonLevelHardcore, paragonLevelSeason, lastUpdate) VALUES (NULL, '{battleTag}', '{guildName}', '{paragonLevelSoftcore}', '{paragonLevelHardcore}', '{paragonLevelSeason}', datetime('now'))"
    # hero
    createHeroesTable = 'CREATE TABLE heroes (id integer primary key autoincrement, heroId text, name text, seasonal boolean, level integer, hardcore boolean, charClass text)'
    isHero = "select count(1) from heroes where heroId='{heroId}'"
    updateHero = "UPDATE heroes SET seasonal='{seasonal}', level='{level}', name='{name}', hardcore='{hardcore}', charClass='{charClass}' where heroId='{heroId}'"
    addHero = "INSERT INTO heroes (id, heroId, name, seasonal, level, hardcore, charClass) VALUES (NULL, '{heroId}', '{name}', '{seasonal}', '{level}', '{hardcore}', '{charClass}')"
    getHeroes = 'select name, bnet, hero from heroes'
    # items
    createItemTable = 'CREATE TABLE items (id integer primary key autoincrement, battleTag text, heroId text, itemId text, name text, icon text, displayColor text, tooltipParams text)'
    isItem = 'select count(1) from items where itemId="{itemId}" and tooltipParams="{tooltipParams}"'
    addItem = 'INSERT INTO items (id, battleTag, heroId, itemId, name, icon, displayColor, tooltipParams) VALUES (NULL, "{battleTag}", "{heroId}", "{itemId}", "{name}", "{icon}", "{displayColor}", "{tooltipParams}")'
    updateItem = 'UPDATE items SET battleTag="{battleTag}", heroId="{heroId}", name="{name}", icon="{icon}", displayColor="{displayColor}" where itemId="{itemId}" and tooltipParams="{tooltipParams}"'
    # paragon
    createParagonHistoryTable = 'CREATE TABLE paragonHistory (id integer primary key autoincrement, bnet text, level integer, checked datetime)'
    inParagon = "INSERT INTO paragon (`id`,`bnet`,`level`,`checked`) VALUES (NULL,'{bnet}', {paragon}, datetime('now'))"
    # app
    getConfig = 'select item, value from config'
    # proces queue
    createProcessingQueue = 'CREATE TABLE processingQueue (battleTag text primary key)' # TODO: verify this statement
    getProcessingQueue = 'select battleTag from processingQueue'
    deleteFromQueue = "delete from processingQueue where battleTag = '{battleTag}'"


class BattleNet:
    profile = 'https://us.api.battle.net/d3/profile/{battleTag}/?locale=en_US&apikey={bnetAPI}'
    hero = 'https://us.api.battle.net/d3/profile/{battleTag}/hero/{heroId}?locale=en_US&apikey={bnetAPI}'
    item = 'https://us.api.battle.net/d3/data/{tooltipString}?locale=en_US&apikey={bnetAPI}'


CONFIG = {}
CONFIG['BNET_API'] = None


conn = sqlite3.connect('d3.db')


def is_profile_db(battleTag):
    global conn
    query = SQL.isProfile.format(battleTag=battleTag)
    cursor = conn.execute(query)
    row = cursor.fetchone()
    if (row[0] == 0):
        return False

    return True

def is_hero_db(heroId):
    global conn
    query = SQL.isHero.format(heroId=heroId)
    cursor = conn.execute(query)
    row = cursor.fetchone()
    if (row[0] == 0):
        return False

    return True

def is_item_db(itemId, tooltipParams):
    global conn
    query = SQL.isItem.format(itemId=itemId, tooltipParams=tooltipParams)
    cursor = conn.execute(query)
    row = cursor.fetchone()
    if (row[0] == 0):
        return False

    return True


def get_profile_api(battleTag):
    request = BattleNet.profile.format(battleTag=battleTag, bnetAPI=CONFIG['BNET_API'])
    profile = get_json_data(request)
    if ('code' in profile):
        if (profile['code'] == 'NOTFOUND'):
            print 'cant find battleTag: {reason}'.format(reason=profile['reason'])
        else:
            print 'unknown code: {reason}'.format(reason=profile['reason'])

        return None

    return profile


def get_hero_api(battleTag, heroId):
    global URL
    request = BattleNet.hero.format(battleTag=battleTag, heroId=heroId, bnetAPI=CONFIG['BNET_API'])
    result = get_json_data(request)
    return result


def get_item_api(tooltipString):
    global URL
    request = BattleNet.item.format(tooltipString=tooltipString, bnetAPI=CONFIG['BNET_API'])
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
    global conn
    confData = conn.execute(SQL.getConfig)
    for item, value in confData:
        CONFIG[item] = value


def upsert_profile_db(battleTag):
    global conn
    profile = get_profile_api(battleTag)
    if (profile is None):
        return None

    # print profile
    if (is_profile_db(battleTag=battleTag)):
        conn.execute(SQL.updateProfile.format(
            battleTag=battleTag,
            guildName=profile['guildName'],
            paragonLevelSoftcore=profile['paragonLevel'],
            paragonLevelHardcore=profile['paragonLevelHardcore'],
            paragonLevelSeason=profile['paragonLevelSeason']
        ))
        print u'updated profile'
    else:
        conn.execute(SQL.addProfile.format(
            battleTag=battleTag,
            guildName=profile['guildName'],
            paragonLevelSoftcore=profile['paragonLevel'],
            paragonLevelHardcore=profile['paragonLevelHardcore'],
            paragonLevelSeason=profile['paragonLevelSeason']
        ))
        print(u'added profile')

    conn.commit()
    return profile

def upsert_hero_db(battleTag, heroRow):
    if (is_hero_db(heroId=heroRow['id'])):
        conn.execute(SQL.updateHero.format(
            heroId=heroRow['id'],
            name=heroRow['name'],
            seasonal=heroRow['seasonal'],
            level=heroRow['level'],
            hardcore=heroRow['hardcore'],
            charClass=heroRow['class']
        ))
    else:
        conn.execute(SQL.addHero.format(
            heroId=heroRow['id'],
            name=heroRow['name'],
            seasonal=heroRow['seasonal'],
            level=heroRow['level'],
            hardcore=heroRow['hardcore'],
            charClass=heroRow['class']
        ))

    conn.commit()
    return True

def get_processingQueue_db():
    global conn
    cursor = conn.execute(SQL.getProcessingQueue)
    print SQL.getProcessingQueue
    rows = cursor.fetchall()
    return rows

def upsert_items_db(battleTag, heroId):
    global conn
    hero = get_hero_api(battleTag=battleTag, heroId=heroId)
    for item in hero['items']:
        gear = hero['items'][item]
        if (is_item_db(itemId=gear['id'], tooltipParams=gear['tooltipParams'])):
            conn.execute(SQL.updateItem.format(
                battleTag=battleTag,
                heroId=heroId,
                itemId=gear['id'],
                name=gear['name'],
                icon=gear['icon'],
                displayColor=gear['displayColor'],
                tooltipParams=gear['tooltipParams']
            ))
        else:
            conn.execute(SQL.addItem.format(
                battleTag=battleTag,
                heroId=heroId,
                itemId=gear['id'],
                name=gear['name'],
                icon=gear['icon'],
                displayColor=gear['displayColor'],
                tooltipParams=gear['tooltipParams']
            ))

    conn.commit()


# this is meant to update everything so do your work here
def do_profile(battleTag):
    profile = upsert_profile_db(battleTag=battleTag)
    if (profile is None):
        return False

    for hero in profile['heroes']:
        upsert_hero_db(battleTag=battleTag, heroRow=hero)
        upsert_items_db(battleTag=battleTag, heroId=hero['id'])


def process_queue():
    battleTags = get_processingQueue_db()
    # battleTags = [('nihiven-1513',)]
    for battleTag in battleTags:
        profile = None
        do_profile(battleTag[0])
        conn.execute(SQL.deleteFromQueue.format(battleTag=battleTag[0]))

    conn.commit()

###
load_config()
if (CONFIG['BNET_API'] is None):
    sys.exit('Error loading config data!')
print 'Battle.Net API Key: {key}'.format(key=CONFIG['BNET_API'])
# load external processing queue


# load hero data
process_queue()

conn.close()
