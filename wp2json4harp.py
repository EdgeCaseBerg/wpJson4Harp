"""
Author: Ethan Joachim Eldridge
Website: ejehardenberg.github.io
Contact me through my github.
"""

MYSQL_HOST="localhost"
MYSQL_USER=""
MYSQL_PASS=""
MYSQL_DB  =""
WP_PREFIX = "wp_"

#Required: MySQLdb python module
#On Linux: python-mysqldb
#Windows: http://sourceforge.net/projects/mysql-python/files/
#Mac: http://stackoverflow.com/questions/1448429/how-to-install-mysqldb-python-data-access-library-to-mysql-on-mac-os-x#1448476
import MySQLdb

import sys

def default(obj):
    """Default JSON serializer."""
    import calendar, datetime

    if not isinstance(obj, datetime.datetime):
    	return obj.__dict__
    if isinstance(obj, datetime.datetime):
        if obj.utcoffset() is not None:
            obj = obj - obj.utcoffset()
    
    	
    millis = int(
        calendar.timegm(obj.timetuple()) * 1000 +
        obj.microsecond / 1000
    )
    return millis

import datetime, json


class WP_Post(object):
	def to_JSON(self):
		return json.dumps(self, default=default, sort_keys=True, indent=4)

def databaseMigrate():
	#Verify database connection
	try:
		db = MySQLdb.connect(host=MYSQL_HOST,user=MYSQL_USER,passwd=MYSQL_PASS,  db=MYSQL_DB)
		db.close()
	except Exception as err:
		print err
		print "Could not connect to database. Aborting..."
		sys.exit(1)

	db = MySQLdb.connect(host=MYSQL_HOST,user=MYSQL_USER,passwd=MYSQL_PASS,  db=MYSQL_DB)
	curs = db.cursor()

	curs.execute("SELECT p.ID, p.post_author, p.post_date_gmt, p.post_content, p.post_title, p.post_status, pm.meta_key, pm.meta_value from %(WP_PREFIX)sposts p JOIN %(WP_PREFIX)spostmeta pm ON p.ID=pm.post_id ORDER BY p.ID"  % globals())

	placeholder = WP_Post()
	setattr(placeholder,'ID',-1)
	posts = [placeholder]
	for row in curs.fetchall():
		if posts[-1].ID != row[0]:
			posts.append(WP_Post())
		setattr(posts[-1],'ID',row[0])
		setattr(posts[-1],'author',row[1])
		setattr(posts[-1],'date',row[2])
		setattr(posts[-1],'content',row[3])
		setattr(posts[-1],'title',row[4])
		setattr(posts[-1],'status',row[5])
		setattr(posts[-1],row[6],row[7])

	del posts[0] #Remove placeholder
	print '['
	i=0
	for post in posts:
		print post.to_JSON()
		if i >= 0 and len(posts)-1!=i:
			print ','
		i+=1

	print ']'

		
if __name__ == "__main__":
	databaseMigrate()