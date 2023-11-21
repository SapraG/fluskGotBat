import sqlite3

connect = sqlite3.connect("db.db")
cursor = connect.cursor()

cursor.execute('''CREATE TABLE IF NOT EXISTS  "users" ("id"	INTEGER,"login"	TEXT,"password"	TEXT,PRIMARY KEY("id" AUTOINCREMENT));''')
connect.commit()
cursor.execute('''CREATE TABLE IF NOT EXISTS "links_types" ("id"	INTEGER,"type"	TEXT,PRIMARY KEY("id" AUTOINCREMENT));''')
connect.commit()
cursor.execute('''
 CREATE TABLE IF NOT EXISTS "links" (
	"id"	INTEGER,
	"link"	TEXT,
	"hreflink"	TEXT,
	"user_id"	INTEGER,
	"link_type_id"	INTEGER,
	PRIMARY KEY("id" AUTOINCREMENT)
    FOREIGN KEY (user_id)  REFERENCES users (id),
    FOREIGN KEY (link_type_id)  REFERENCES links_types (id)
);
''')
connect.commit()
cursor.execute('''INSERT INTO `links_types` (`id`, `type`) VALUES (NULL, 'public'), (NULL, 'general'), (NULL, 'privat');''')
connect.commit()



