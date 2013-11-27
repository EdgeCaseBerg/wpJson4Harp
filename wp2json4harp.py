#!/usr/bin/env python2.7.3
# -*- coding: UTF-8 -*-

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
ONLY_PUBLISHED = False
GENERATE_PAGES = True
GENERATE_POSTS = True
ROOT_DIR = 'test/'		#Leave empty for the folder you're in, specify otherwise otherwise.
ENCODING = 'latin' #irritating unicode
OUTPUT_ENCODING = 'latin'
PAGES_DIR = 'pages'
BLOG_DIR = 'blog'
NAV_DIR = 'nav'
COMMENTS_DIR = 'comments'
EXAMPLE_FILE = 'example.jade'
STRIP_NON_ASCII = True
PULL_TYPES = True
STOP_ON_ERR = False

#Required: MySQLdb python module
#On Linux: python-mysqldb
#Windows: http://sourceforge.net/projects/mysql-python/files/
#Mac: http://stackoverflow.com/questions/1448429/how-to-install-mysqldb-python-data-access-library-to-mysql-on-mac-os-x#1448476
import MySQLdb

#You'll need phpserialize for the deserialization of the objects from php
#install: pip install phpserialize
import phpserialize

import sys
import calendar, datetime
import os
import sets
import re
import codecs

serializedArrayReg = r"^a:[0-9]+:{"
serializedArraySearch = re.compile(serializedArrayReg)

stripNewLines = r"\n"
stripper = re.compile(stripNewLines)

#Need to give the json serializer it's own function because
#datetimes will complain about not having a __dict__ method
def default(obj):
    """Default JSON serializer."""
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

import json

def strip_non_ascii(string):
    ''' Returns the string without non ASCII characters'''
    stripped = (c for c in string if 0 < ord(c) < 127)
    return ''.join(stripped)

def writeEncoded(fd,string):
	if STRIP_NON_ASCII:
		fd.write((strip_non_ascii(string).encode(OUTPUT_ENCODING)))
	else:
		fd.write(string.encode(OUTPUT_ENCODING))
	

def writeStrip(fd,string):
	if STRIP_NON_ASCII:
		fd.write( strip_non_ascii(stripper.sub('', strip_non_ascii(string).encode(OUTPUT_ENCODING) ) ))
	else:
		fd.write( stripper.sub('', string.encode(OUTPUT_ENCODING) ) )

def checkAndMakeDir(path):
	if not os.path.exists(path):
		os.makedirs(path)

def makeExampleFile(post_types):
	#Generate a little bit of layout for the user to get started:
	example = open("%s%s" %(ROOT_DIR, EXAMPLE_FILE),'w')
	writeEncoded(example,('h1 This is an example page to show your wp\n'))
	if not PULL_TYPES:
		writeEncoded(example,('ul\n'))
		writeEncoded(example,('  each navitem in public.%(NAV_DIR)s._data\n' % globals()))
		writeEncoded(example,('    li\n'))
		#This slug below might not be very good. 
		writeEncoded(example,('      a(href="#{navitem.slug}") #{navitem.title}\n'))
		writeEncoded(example,('h2 Your Pages\n'))
		writeEncoded(example,('ul\n'))
		writeEncoded(example,('  each pagedata inpublic.%(PAGES_DIR)s._data\n' % globals()) )
		writeEncoded(example,('    li\n'))
		writeEncoded(example,'      a(href="%(PAGES_DIR)s/#{pagedata.slug}") #{pagedata.title} #{pagedata.date}\n' % globals())
		writeEncoded(example,'      #{pagedata.content}\n')
		writeEncoded(example,'h2 Recents Posts\n')
		writeEncoded(example,'ul\n')
		writeEncoded(example,'  each blogpost in public.%(BLOG_DIR)s._data\n' % globals())
		writeEncoded(example,'    li\n')
		writeEncoded(example,"      a(href=\"%(BLOG_DIR)s/#{blogpost.slug}\") #{blogpost.title} #{blogpost.date}\n" % globals())
		writeEncoded(example,'      #{blogpost.content}\n')
	else:
		for ptype in post_types:
			writeEncoded(example,'h2 Your %s\n' % ptype)
			writeEncoded(example,'ul\n')
			writeEncoded(example,'  each blogpost in public.%(ptype)s._data\n' % locals())
			writeEncoded(example,'    li\n')
			writeEncoded(example,'      if(blogpost.slug)\n')
			writeEncoded(example,'        a(href="%(ptype)s/#{blogpost.slug}") #{blogpost.title} #{blogpost.date}\n' % locals())
		
	example.close()

#This is just a placeholder object that we attach tons of
#dynamic fields to in order to make objects so our data
#is a little bit easier to play with.
class WP_Object(object):
	def to_JSON(self):
		return json.dumps(self, default=default, sort_keys=True, indent=4, ensure_ascii=False, encoding=OUTPUT_ENCODING)

	def __init__(self,**kwargs):
		for k,v in kwargs.iteritems():
			setattr(self,k,v)

def obj_hook(name,d):
	cls = {name : WP_Object}[name]	
	d= phpserialize.convert_member_dict(d)
	return cls(**d)

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

	curs.execute("SELECT p.ID, u.meta_value AS nickname , p.post_date_gmt, p.post_content, REPLACE(REPLACE(REPLACE(post_title, '\t', ''), '\r', ''), '\n', ''), p.post_status, pm.meta_key, pm.meta_value, p.post_type, p.post_name from %(WP_PREFIX)sposts p LEFT JOIN %(WP_PREFIX)spostmeta pm ON p.ID=pm.post_id LEFT JOIN %(WP_PREFIX)susermeta u ON p.post_author=u.user_id WHERE u.meta_key='nickname' ORDER BY p.ID"  % globals())

	post_types = sets.Set()
	placeholder = WP_Object()
	setattr(placeholder,'ID',-1)
	posts = [placeholder]
	for row in curs.fetchall():
		if posts[-1].ID != row[0]:
			posts.append(WP_Object())
		setattr(posts[-1],'ID',row[0])
		setattr(posts[-1],'author',row[1].decode(ENCODING))
		setattr(posts[-1],'date',row[2])
		setattr(posts[-1],'content',row[3].decode(ENCODING))
		setattr(posts[-1],'title',row[4].decode(ENCODING))
		setattr(posts[-1],'status',row[5].decode(ENCODING))
		if row[6] and row[7]:
			if not serializedArraySearch.match(row[7]):
				setattr(posts[-1],row[6].decode(ENCODING),row[7].decode(ENCODING))
			else:
				try:
					setattr(posts[-1],row[6], phpserialize.loads(row[7], object_hook=obj_hook))
				except ValueError, e:
					pass #If a failure occurs here it's probably a corrupt object
					print "Failed to load: ",row[7]
					if STOP_ON_ERR:
						curs.close()
						db.close()
						sys.exit()
		setattr(posts[-1],'ptype',row[8].decode(ENCODING))
		if row[9]:
			setattr(posts[-1],'slug',row[9].decode(ENCODING))
		else:
			setattr(posts[-1],'slug',row[0])
		post_types.add(row[8])
	del posts[0] #Remove placeholder
	

	if PULL_TYPES:
		ptypeCount = {}
		ptypeTotal = {}
		for ptype in post_types:
			checkAndMakeDir("%s%s" % (ROOT_DIR,ptype))
			p = open("%s%s/_data.json" % (ROOT_DIR, ptype),'w')
			writeEncoded(p,'{')
			p.close()
			ptypeCount[ptype] = 0
			ptypeTotal[ptype] = sum(map(lambda x: x.ptype == ptype ,posts))
		for post in posts:
			if GENERATE_POSTS:
				tmp = open("%s%s/%s.md" % (ROOT_DIR, post.ptype, post.slug),'w+')
				writeEncoded(tmp,"#%s\n\n" % json.dumps(post.title.strip()))
				if(hasattr(post,'content')):
					writeEncoded(tmp,post.content)
					delattr(post,'content')
				tmp.close()
			p = open("%s%s/_data.json" % (ROOT_DIR, post.ptype),'a')
			tobeprocessed = " %s : %s " % (json.dumps("%s%d" % (post.title.strip(),post.ID)), post.to_JSON())
			writeEncoded(p, tobeprocessed )
			if ptypeTotal[post.ptype]-1 != ptypeCount[post.ptype]:
				writeEncoded(p,',')
			ptypeCount[post.ptype]+=1
			p.close()
		for ptype in post_types:
			p = open("%s%s/_data.json" % (ROOT_DIR, ptype),'a+')
			writeEncoded(p,'}')
			p.close()
	else:
		checkAndMakeDir("%(ROOT_DIR)s%(PAGES_DIR)s" % globals())
		checkAndMakeDir("%(ROOT_DIR)s%(BLOG_DIR)s" % globals())
		checkAndMakeDir("%(ROOT_DIR)s%(NAV_DIR)s" % globals())

		p = open("%(ROOT_DIR)s%(PAGES_DIR)s/_data.json" % globals(),'w')
		b = open('%(ROOT_DIR)s%(BLOG_DIR)s/_data.json' % globals(),'w')
		n = open('%(ROOT_DIR)s%(NAV_DIR)s/_data.json' % globals(),'w')
		pcount = 0
		bcount = 0
		ncount = 0
		totalPages = sum(map(lambda x: x.ptype == "page",posts))
		totalPosts = sum(map(lambda x: x.ptype == "post",posts))
		totalNavs = sum(map(lambda x: x.ptype == "nav_menu_item" ,posts))
		
		writeEncoded(p,'{')
		writeEncoded(b,'{')
		writeEncoded(n,'{')
		for post in posts:
			if ONLY_PUBLISHED and hasattr(post,'status') and post.status != "publish":
					continue
			if post.ptype == "page":
				#Throw the id onto the string to ensure unique ness of the title
				if GENERATE_PAGES:
					tmp = open("%s%s/%s.md" % (ROOT_DIR, PAGES_DIR, post.slug),'w')
					writeEncoded(tmp,"#%s\n\n" % post.title)
					writeEncoded(tmp,post.content)
					tmp.close()
					delattr(post,'content')
				writeEncoded(p," %s : %s " % (json.dumps("%s%d" % (post.title.strip(),post.ID)),  post.to_JSON()) )
				if totalPages-1 != pcount:
					writeEncoded(p,',')
				pcount+=1
			elif post.ptype == "post":
				if GENERATE_POSTS:
					tmp = open("%s%s/%s.md" % (ROOT_DIR, BLOG_DIR, post.slug),'w')
					writeEncoded(tmp,"#%s\n\n" % post.title)
					writeEncoded(tmp,post.content)
					tmp.close()
					delattr(post,'content')
				writeEncoded(b," %s : %s " % (json.dumps("%s%d" % (post.title.strip(),post.ID)), post.to_JSON()) )
				if totalPosts-1 != bcount:
					writeEncoded(b,',')
				bcount+=1
			elif post.ptype == "nav_menu_item" :
				if post._menu_item_object == "custom":
					post.slug = post._menu_item_url
				elif post._menu_item_object == "page":
					for temp_post in posts:
						if int(temp_post.ID) == int(post._menu_item_object_id):
							post.slug = "%s/%s" % (PAGES_DIR,temp_post.slug)
							post.title = temp_post.title
				writeEncoded(n,"%s : %s " % (json.dumps( "%s%d" % (post.title.strip(),post.ID) ),post.to_JSON()))
				if totalNavs-1 != ncount:
					writeEncoded(n,',')
				ncount+=1
			else:
				#I'm just printing to look at the objects to decide to convert them into something or not.
				#print(post.to_JSON())
				pass
				#do what you will with the other types

		writeEncoded(p,'}')
		writeEncoded(b,'}')
		writeEncoded(n,'}')
		p.close()
		b.close()
		n.close()

	curs.execute("SELECT c.comment_ID, c.comment_post_ID, c.comment_author, c.comment_author_email, c.comment_author_url, c.comment_date, c.comment_content, c.user_id, u.meta_value as nickname, cm.meta_key, cm.meta_value FROM %(WP_PREFIX)scomments c LEFT JOIN %(WP_PREFIX)scommentmeta cm ON c.comment_ID=cm.comment_id JOIN %(WP_PREFIX)susermeta u ON c.user_id in (u.user_id,0) WHERE u.meta_key='nickname' ORDER BY c.comment_post_ID " % globals())
	placeholder = WP_Object()
	setattr(placeholder,'ID',-1)
	comments = [placeholder]
	for row in curs.fetchall():
		if comments[-1].ID != row[0]:
			comments.append(WP_Object())
		setattr(comments[-1],'ID',row[0])
		setattr(comments[-1],'post_ID',row[1])
		setattr(comments[-1],'author',row[2].decode(ENCODING))
		setattr(comments[-1],'author_email',row[3].decode(ENCODING))
		setattr(comments[-1],'author_url',row[4].decode(ENCODING))
		setattr(comments[-1],'date',row[5])
		setattr(comments[-1],'content',row[6].decode(ENCODING))
		setattr(comments[-1],'user_id',row[7])
		setattr(comments[-1],'nickname',row[8].decode(ENCODING))
		if row[9] is not None and row[10] is not None:

			setattr(comments[-1],row[9], row[10])
	del comments[0]

	checkAndMakeDir("%(ROOT_DIR)s%(COMMENTS_DIR)s" % globals())
	c = open("%(ROOT_DIR)s%(COMMENTS_DIR)s/_data.json" % globals() ,'w' )
	writeEncoded(c,'{')
	ccount = 0
	cTotal = len(comments)
	for comment in comments:
		writeEncoded(c,"\"%d-%d-%d\" : %s" % (comment.post_ID, (comment.date - datetime.datetime(1970,1,1)).total_seconds(), comment.ID, comment.to_JSON()) )
		if cTotal-1 != ccount:
			writeEncoded(c,',')
		ccount+=1
	writeEncoded(c,'}')
	c.close()

	
	makeExampleFile(post_types)

		
if __name__ == "__main__":
	databaseMigrate()
