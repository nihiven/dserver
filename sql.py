import sqlite3

# sql queries for import
class SQL:
    # profile
    createProfilesTable = "CREATE TABLE profiles (id integer primary key autoincrement, battleTag text, guildName text, paragonLevelSoftcore integer, paragonLevelHardcore integer, paragonLevelSeason integer, lastUpdate datetime)"
    isProfile = "select count(1) from profiles where battleTag='{battleTag}'"
    updateProfile = "UPDATE profiles SET guildName='{guildName}', paragonLevelSoftcore='{paragonLevelSoftcore}', paragonLevelHardcore='{paragonLevelHardcore}', paragonLevelSeason='{paragonLevelSeason}', lastUpdate=datetime('now') where battleTag = '{battleTag}'"
    addProfile = "INSERT INTO profiles (id, battleTag, guildName, paragonLevelSoftcore, paragonLevelHardcore, paragonLevelSeason, lastUpdate) VALUES (NULL, '{battleTag}', '{guildName}', '{paragonLevelSoftcore}', '{paragonLevelHardcore}', '{paragonLevelSeason}', datetime('now'))"
    allProfiles = "select battleTag, guildName from profiles"
    # hero
    createHeroesTable = 'CREATE TABLE heroes (id integer primary key autoincrement, heroId text, name text, seasonal boolean, level integer, hardcore boolean, charClass text)'
    isHero = "select count(1) from heroes where heroId='{heroId}'"
    updateHero = "UPDATE heroes SET seasonal='{seasonal}', level='{level}', name='{name}', hardcore='{hardcore}', charClass='{charClass}' where heroId='{heroId}'"
    addHero = "INSERT INTO heroes (id, heroId, name, seasonal, level, hardcore, charClass) VALUES (NULL, '{heroId}', '{name}', '{seasonal}', '{level}', '{hardcore}', '{charClass}')"
    getHeroes = 'select name, bnet, hero from heroes'
    # items
    createItemTable = 'CREATE TABLE items (tooltipParams text primary key, battleTag text, heroId text, itemId text, name text, icon text, displayColor text, ancientRank float)'
    isItem = 'select count(1) from items where tooltipParams="{tooltipParams}"'
    addItem = 'INSERT INTO items (battleTag, heroId, itemId, name, icon, displayColor, tooltipParams) VALUES ("{battleTag}", "{heroId}", "{itemId}", "{name}", "{icon}", "{displayColor}", "{tooltipParams}")'
    updateItem = 'UPDATE items SET battleTag="{battleTag}", heroId="{heroId}", name="{name}", icon="{icon}", displayColor="{displayColor}", itemId="{itemId}" where tooltipParams="{tooltipParams}"'
    # paragon
    createParagonHistoryTable = 'CREATE TABLE paragonHistory (id integer primary key autoincrement, bnet text, level integer, checked datetime)'
    inParagon = "INSERT INTO paragon (`id`,`bnet`,`level`,`checked`) VALUES (NULL,'{bnet}', {paragon}, datetime('now'))"
    # app
    getConfig = 'select item, value from config'
    # proces queue
    createProcessingQueue = 'CREATE TABLE processingQueue (battleTag text primary key)' # TODO: verify this statement
    getProcessingQueue = 'select battleTag from processingQueue'
    deleteFromQueue = "delete from processingQueue where battleTag = '{battleTag}'"
    # queue
    getQueue = "select battleTag from processingQueue"
    isQueued = "select count(1) from processingQueue where battleTag='{battleTag}'"
    enqueue = "INSERT INTO processingQueue (`battleTag`) VALUES ('{battleTag}')"


def dbConnect():
    return sqlite3.connect('d3.db')

def dbProfileExists(battleTag=None):
    if (battleTag is not None):
        conn = dbConnect()
        cursor = conn.execute(SQL.isQueued.format(battleTag=battleTag))
        data = cursor.fetchone()
        if (data[0] > 0):
            return True

    return False
