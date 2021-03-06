#!/usr/bin/python

from boto.s3.connection import S3Connection
from boto.s3.key import Key
import datetime
import json
import MySQLdb
from urllib import quote
import urllib2

conn = MySQLdb.connect(
	host='***REMOVED***',
 	user='condor',
 	passwd='condor',
 	db ='condor',
	use_unicode=True,
    charset="utf8")
cur = conn.cursor()

cur.execute("SET time_zone='+0:00'")

recent_query = 'select real_url, count(distinct user_id) as num, real_url_hash, domain, embedly_blob from tweeted_urls left join url_info using(real_url_hash) where created_at > DATE_SUB(NOW(), INTERVAL 4 HOUR) and domain in ("somerville.patch.com","metrowestdailynews.com","metro.us","dotnews.com","mbta.com","boston.eater.com","commonhealth.wbur.org","patriotledger.com","boston.redsox.mlb.com","news.harvard.edu","bostonrestaurants.blogspot.com","boston.craigslist.org","artery.wbur.org","patriots.com","bpdnews.com","bu.edu","digboston.com","universalhub.com","web.mit.edu","wgbhnews.org","wbur.org","necn.com","boston.cbslocal.com","nesn.com","bostonherald.com","bostonmagazine.com","bostonglobe.com","boston.com","radioboston.wbur.org","weather.boston.cbslocal.com","somervillebeat.com","live.boston.com","thecrimson.com","thesomervillenews.com","gazettenet.com","backbay.patch.com","barstoolsports.com","scoutsomerville.com","jewishboston.com","wgbh.org","somervillema.gov","commonwealthmagazine.org","publicartboston.com","epaper.bostonglobe.com","boston.sportsthenandnow.com","cambridgema.gov","stats.boston.cbslocal.com","allstonpudding.com","martywalsh.org","thebostoncalendar.com","vanyaland.com","weei.com","providencejournal.com") group by real_url'
background_query = 'select real_url, count(distinct user_id) as num from tweeted_urls where created_at > DATE_SUB(NOW(), INTERVAL 7 DAY) and domain in ("somerville.patch.com","metrowestdailynews.com","metro.us","dotnews.com","mbta.com","boston.eater.com","commonhealth.wbur.org","patriotledger.com","boston.redsox.mlb.com","news.harvard.edu","bostonrestaurants.blogspot.com","boston.craigslist.org","artery.wbur.org","patriots.com","bpdnews.com","bu.edu","digboston.com","universalhub.com","web.mit.edu","wgbhnews.org","wbur.org","necn.com","boston.cbslocal.com","nesn.com","bostonherald.com","bostonmagazine.com","bostonglobe.com","boston.com","radioboston.wbur.org","weather.boston.cbslocal.com","somervillebeat.com","live.boston.com","thecrimson.com","thesomervillenews.com","gazettenet.com","backbay.patch.com","barstoolsports.com","scoutsomerville.com","jewishboston.com","wgbh.org","somervillema.gov","commonwealthmagazine.org","publicartboston.com","epaper.bostonglobe.com","boston.sportsthenandnow.com","cambridgema.gov","stats.boston.cbslocal.com","allstonpudding.com","martywalsh.org","thebostoncalendar.com","vanyaland.com","weei.com","providencejournal.com") group by real_url'

background_popularity = {}

cur.execute(background_query)
for row in cur:
	background_popularity[row[0]] = float(row[1])


links = []

cur.execute(recent_query)
for row in cur:
	# out.append({'url':row[0], 'hotness': row[1]-background_popularity[row[0]]})
	links.append({'url':row[0], 'hotness': (row[1]*row[1])/background_popularity[row[0]], 'hash':row[2], 'source':row[3], 'embedly_blob':row[4]})

links.sort(key=lambda x: x['hotness'],reverse=True)

links = links[:10]

to_get_from_embedly = [x for x in links if x['embedly_blob'] is None]

if len(to_get_from_embedly) > 0:
	embedly_list = json.load(urllib2.urlopen("http://api.embed.ly/1/extract?key=***REMOVED***&urls=" + ','.join([quote(x['url']) for x in to_get_from_embedly])))

	for (link,embedly) in zip(to_get_from_embedly,embedly_list):
		embedly_blob = json.dumps(embedly)
		cur.execute("insert into url_info (real_url_hash,embedly_blob) values (%s,%s) on duplicate key update embedly_blob = %s",(link['hash'],embedly_blob,embedly_blob))
		for target in links:
			if target['hash'] == link['hash']:
				target['embedly_blob'] = embedly_blob
				break
	conn.commit()

for link in links:
	embedly = json.loads(link['embedly_blob'])
	del link['embedly_blob']
	cur.execute("select count(distinct user_id), min(created_at) from tweeted_urls where real_url_hash = %s",(link['hash']))
	for row in cur:
		link['total_tweets'] = row[0]
		link['first_tweeted'] = row[1].isoformat()
	link['title'] = embedly['title']
	link['description'] = embedly['description']
	for img in embedly['images']:
		if img['width'] > 300:
			link['image_url'] = img['url']
			break
	link['tweeters'] = []
	cur.execute("select screen_name, name, followers_count, profile_image_url, text, tweet_id, tweeted_urls.created_at from users join tweeted_urls using(user_id) join tweets using(tweet_id) where real_url_hash = %s group by tweeted_urls.user_id order by followers_count desc",(link['hash']))
	for row in cur:
		link['tweeters'].append({'screen_name': row[0], 'name': row[1], 'followers_count': row[2], 'profile_image_url': row[3], 'text':row[4], 'tweet_id':str(row[5]), 'created_at':row[6].isoformat()})
	del link['hash']

out = {	'generated_at': datetime.datetime.utcnow().isoformat(),
		'articles':links[:10]}

# print json.dumps(out,indent=1)

s3_conn = S3Connection('***REMOVED***', '***REMOVED***')
k = Key(s3_conn.get_bucket('condor.globe.com'))
k.key = 'json/hotlist.json'
k.set_contents_from_string(json.dumps(out,indent=1))
k.set_acl('public-read')