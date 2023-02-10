# Modules
import psycopg2
import json
import os

# Config file
cgFile = open('config.json', 'r')
config = json.load(cgFile)

# Connection
conn = psycopg2.connect(
    database = config['defaultSQLDatabase'], 
    user = config['defaultSQLUser'], 
    password = config['defaultSQLPassword'], 
    host = config['serverIP'], 
    port = "5432"
)
cur = conn.cursor()


# List versions available
def getVersions() :
    files = os.listdir(config['pathToFiles'])
    
    dirsReturn = []
    for i in range(len(files)) :
        if files[i].count('.') == 0 :
            dirsReturn.append(files[i])

    return dirsReturn

# Get version in DB
def getActualVersion() :
    cur.execute('SELECT * FROM __migrations ORDER BY version DESC;')
    res = cur.fetchall()

    if len(res) > 0 :
        return res[0][0]
    else :
        return -1