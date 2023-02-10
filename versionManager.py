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


# Apply SQL file
def applySQLFile(data) :
    cur.execute(data)
    conn.commit()


# Apply version to DB
def applyVersion(vers) :
    # Actual
    version = getActualVersion()

    # Available
    dirs = getVersions()

    # Apply
    if vers > version : # New version
        for v in range(version + 1, vers + 1) :
            dir = dirs[v]

            files = os.listdir(config['pathToFiles'] + '/' + dir)
            print(files)
            
            upFiles = []
            for i in range(len(files)) :
                if files[i].count('.sql') != 0 and files[i].count('up') != 0:
                    upFiles.append(files[i])
            print(upFiles)

            # Apply vers
            if len(upFiles) > 0 :
                file = open(upFiles[0], 'r')

                applySQLFile(file.read())
                applySQLFile(f"INSERT INTO __migrations(version) VALUES ({v});")

                file.close()

                print(f'Upgraded to V{v}')
            else :
                print(f'No migration UP file for version {v}')
    elif vers > version : # Rollback to old version
        for v in range(version, vers) :
            dir = dirs[v]

            files = os.listdir(config['pathToFiles'] + '/' + dir)
            print(files)

            downFiles = []
            for i in range(len(files)) :
                if files[i].count('.sql') != 0 and files[i].count('down') != 0:
                    downFiles.append(files[i])
            print(downFiles)

            # Apply vers
            if len(downFiles) > 0 :
                file = open(downFiles[0], 'r')

                applySQLFile(file.read())
                applySQLFile(f"DELETE FROM __migrations WHERE version={v};")

                file.close()

                print(f'Downgraded to V{v-1}')
            else :
                print(f'No migration DOWN file for version {v}')
    else :
        print('Version already installed !')