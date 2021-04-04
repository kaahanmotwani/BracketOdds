#!/usr/bin/env python
from lib.bracket import Bracket, BracketType
from lib.bracket.sample import Sample
import random, time, datetime, binascii, os
import mysql.connector as dbconnect
import toml

file_path = 'cfg.toml'

class db:
    def __init__(self):
        db = toml.load(file_path)['database']
        self.host = db['host']
        self.user = db['username']
        self.password = db['password']
        self.name = db['name']
        self.table = db['table']

def connect(database: db):
    db_connection = dbconnect.connect(host=database.host,
            user=database.user,
            passwd=database.password,
            db=database.name)
    return db_connection

def timestamp():
    return datetime.datetime.utcfromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')

def uid():
    return binascii.b2a_hex(os.urandom(8))
        
def insert(database: db, bracket: Bracket):
    db_connection = connect(database)
    cursor = db_connection.cursor()
    u = uid()
    t = timestamp()
    command = ("INSERT INTO {0}.{1} "
              "(timestamp, id, bitstring, sfn, type) "
              "VALUES (\"{2}\",\"{3}\",\"{4}\", \"{5}\", \"{6}\")".format(database.name, database.table, t, u.decode("utf-8"), 
            bracket.bits(), bracket.sfn, bracket.bracket_type.value))
    try:
        cursor.execute(command)
        db_connection.commit()
    except dbconnect.Error as e:
        db_connection.rollback()
        raise e
    finally:
        db_connection.close()
        cursor.close()
    return u, t

def select(database: db, uid: str=None) -> dict:
    db_connection = connect(database)
    cursor = db_connection.cursor()
    command = ('''SELECT *
        FROM {0}.{1} 
        WHERE id=\"{2}\"'''.format(database.name, database.table, uid))
    cursor.execute(command)
    row = cursor.fetchone()
    if not row:
        return None
    out = Bracket.from_bitstring(BracketType(row[4]), str(row[2])).to_json()
    out['isNew'] = False
    out['id'] = row[1]
    out['timestamp'] = row[0]
    out['sfn'] = row[3]
    db_connection.close()
    cursor.close()
    return out

def getBracket(uid: str=None, bracket_type: Bracket=BracketType.MEN,
        sampling_fn: Sample=None) -> dict:
    if uid:
        return select(db(), uid)
    else:
        b = Bracket(bracket_type, sampling_fn)
        b.run()
        success = False
        uid = None
        timestamp = None
        while not success:
            try:
                uid, timestamp = insert(db(), b)
                success = True
            except dbconnect.Error as e:
                raise e
        out = b.to_json()
        out['timestamp'] = timestamp
        out['isNew'] = True
        out['id'] = uid.decode("utf-8")
        return out