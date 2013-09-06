pushd .
cd ~/condor
rm -rf data
mkdir data
python27 hotlist2.py $1 $2 $3 --group_clusters --num_results=40 > data/articles_12.json
mv data/articles_12.json data/articles.json

mkdir data/hashtags
python27 hotlist2.py $1 --hashtag=bospoli	--min --no_tweeters --num_results=5 > data/hashtags/bospoli.json
python27 hotlist2.py $1 --hashtag=mapoli 		--min --no_tweeters --num_results=5 > data/hashtags/mapoli.json
python27 hotlist2.py $1 --hashtag=bosmayor 	--min --no_tweeters --num_results=5 > data/hashtags/bosmayor.json
python27 hotlist2.py $1 --hashtag=redsox 		--min	--no_tweeters --num_results=5 > data/hashtags/redsox.json
python27 hotlist2.py $1 --hashtag=patriots 	--min --no_tweeters --num_results=5 > data/hashtags/patriots.json

mkdir data/leaders
python27 hotlist2.py --min --no_tweeters --num_results=10 --age=168 > data/leaders/week.json

mkdir data/domain_leaders
python top_domains.py --age=1 --num_results=25 > data/domain_leaders/domains_1.json

rm -rf www/json
mkdir www/json
python combine_json.py $1 $2 $3 data > www/json/data.json
cp data/leaders/week.json data/articles_168.json
cp -r data/* www/json
popd
