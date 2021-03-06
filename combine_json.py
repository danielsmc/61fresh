	#!/usr/bin/python

from boto.s3.connection import S3Connection
from boto.s3.key import Key
import datetime
import json
import MySQLdb
import MySQLdb.cursors
from urllib import quote
import urllib2
import sys
import re
import optparse
import os

directory = sys.argv[1]
out_file = sys.argv[2]
out = {}
import os, os.path

CONDOR_ENV = os.environ['CONDOR_ENV']
CONDOR_HOME = env = os.environ['CONDOR_HOME']

if not CONDOR_ENV:
	print "you must set the CONDOR_ENV bash variable (production, test, etc)"
if not CONDOR_HOME:
	condor_home="~/condor"

try:
	with open("%s/config/config-%s.json" % (CONDOR_HOME,CONDOR_ENV)) as fh:
		config = json.load(fh)
except IOError:
	with open('%s/config/config.json' % CONDOR_HOME) as fh:
		config = json.load(fh)


# parser = optparse.OptionParser()
# parser.add_option('-a', '--age', help='max age of urls in hours. default value is 12',default='12')
# parser.add_option('-d', '--days_ago', help='Placebo, because it gets passed',default='0')
# parser.add_option('-p', '--popularity_weight', help='multiplier for popularity - higher values will give greater emphasis to popular articles over fresh articles. default is 100',default='100')
# parser.add_option('-i', '--ignore_age', help='ignore recency & just return a straight popularity rank for the time period, default is false',default=False)
# parser.add_option('-n', '--no_tweeters', help="don't return array of tweeters with each url - saves file size. default is False (tweeters will be returned).",default=False)
# parser.add_option('-m', '--min', help="minimize file size. includes only title, url, age, source, first_tweeted, hotness",default=False)
# parser.add_option('-r', '--num_results', help="number of results to return, default value is 50.",default=50)
# parser.add_option('-t', '--hashtag', help="filter by the given hashtag, not domain list, default is false",default=False)
# parser.add_option('-o', '--no_s3', help="don't upload to s3",default=False)
# parser.add_option('-c', '--no_classify', help="don't run sports classifier",default=False)

# (opts, args) = parser.parse_args()


#def upload_to_s3(key,s): 
#	s3_conn = S3Connection(config['aws-s3']['access-key-id'],config['aws-s3']['secret-access-key']) 
#	k = Key(s3_conn.get_bucket(config['aws-s3']['bucket-name']))
#	k.key = key
#	print "key %s" % k.key
#	k.set_contents_from_string(s)
#	k.set_acl('public-read')



for root, _, files in os.walk(directory):
	for f in files:
		fullpath = os.path.join(root, f)
		elems = re.split('\W+',fullpath)
		f = open(fullpath, 'r')
		text = f.read()
		if len(elems)==3:
			# ex: json_stage/articles.json
			out[elems[1]]=json.loads(text)
#			upload_to_s3('json/'+elems[1]+'.json',text)
			
		if len(elems)==4:
			# ex: json_stage/hashtags/articles.json
			if elems[1] not in out:
				out[elems[1]]=[]
#			upload_to_s3('json/'+elems[1]+'/'+elems[2]+'.json',text)
			_json = json.loads(text)
			out[elems[1]].append({'name':elems[2],'data':_json})

out['generated_at'] = datetime.datetime.utcnow().isoformat() + "Z"

with open(out_file,'w') as fh:
	json.dump(out,fh,indent=1)

