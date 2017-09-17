import sqlite3
import os

if not os.path.exists('data'):
    os.makedirs('data')

db = sqlite3.connect('data/bot_database.db')
cursor = db.cursor()
cursor.execute('CREATE TABLE users (user_id INTEGER PRIMARY KEY, chat_id VARCHAR(20) UNIQUE)')
db.commit()

cursor.execute('CREATE TABLE settings (set_id INTEGER PRIMARY KEY, setname VARCHAR(20) UNIQUE)')
db.commit()

cursor.execute('CREATE TABLE user_settings (user_id INTEGER, set_id INTEGER, setvalue VARCHAR(20), PRIMARY KEY(user_id, set_id))')
db.commit()

cursor.execute('INSERT INTO settings (setname) VALUES ("show_photo");')
db.commit()

cursor.execute('INSERT INTO settings (setname) VALUES ("show_url");')
db.commit()




