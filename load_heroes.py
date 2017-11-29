import json
import urllib2
import sqlite3
import sys
from dbmapping import DMItem, _db, dbMap  # database field mapping
from sql import SQL
from battlenet import BattleNet

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


def is_item_db(tooltipParams):
    global conn
    query = SQL.isItem.format(tooltipParams=tooltipParams)
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


def get_item_api(tooltipParams):
    global URL
    request = BattleNet.item.format(tooltipParams=tooltipParams, bnetAPI=CONFIG['BNET_API'])
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


def upsert_item_detail_db(tooltipParams):
    global conn, DMItem
    data = get_item_api(tooltipParams=tooltipParams)
    for field in data:
        db = _db(field)
        if (db is None):
            print '*** DMItem["{field}"] = ""'.format(field=field)
        else:
            print '{field}: {value}'.format(field=field, value=data[field]).encode('utf8')


def upsert_items_db(battleTag, heroId):
    global conn
    hero = get_hero_api(battleTag=battleTag, heroId=heroId)
    for item in hero['items']:
        gear = hero['items'][item]
        if (is_item_db(tooltipParams=gear['tooltipParams'])):
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

        # is this where we call this? i think so......?
        upsert_item_detail_db(gear['tooltipParams'])

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
    # battleTags = get_processingQueue_db()
    battleTags = [('nihiven-1513',)]
    for battleTag in battleTags:
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
