import os
from django.shortcuts import render
from django.http import JsonResponse
import json
import requests
import redis
import feedparser
import random

# Create your views here.
HN_TOP_STORIES = 'https://hacker-news.firebaseio.com/v0/topstories.json?print=pretty'
HN_STORY_DETAIL = 'https://hacker-news.firebaseio.com/v0/item/'
PH_TOP_STORIES = 'https://api.producthunt.com/v1/posts/'
PH_TOKEN = 'xvyN2pVNtV0PAw-lUvtQtfizt1E9qdNriw9-AwDRgDs'


#RSS Feed Links
product_hunt = 'https://www.producthunt.com/feed?category=tech'
coin_desk = 'http://feeds.feedburner.com/CoinDesk'
hacker_news = 'https://news.ycombinator.com/rss'
tech_crunch = 'http://feeds.feedburner.com/TechCrunch/'
reddit = 'https://www.reddit.com/.rss'
bitcoin = 'https://api.coindesk.com/v1/bpi/currentprice.json'

categories = ['Technology', 'Design', 'Business']

feed_list = []

def construct_feed_list():
    cwd = os.getcwd()
    file = cwd+'/api/source.json'
    with open(file) as f:
        data = json.load(f)
        for feeds in data['data']:
            for source in feeds['sources']:
                feed_list.append(source['name_title'])
    

def dashboard(request):
    print(request.GET.get('data'))
    construct_feed_list()
    stories = request.GET.get('data', None)
    if stories is None:
        random.shuffle(feed_list)
        stories = feed_list[0:9]
    else:
        stories = stories.split(',')
    result = []
    try:
        flash = redis.Redis(host='redis-17256.c14.us-east-1-3.ec2.cloud.redislabs.com', port=17256, db=0, password='qhaH3zeAOgn6t6huFIxQhYx51iEGyEM2')
    except Exception as e:
        print(e)
    for feed in stories:
        print("Story is", feed)
        hn = flash.get(feed).decode('utf-8')
        tmp = {
            "name": feed,
            "data": json.loads(hn)
        }
        result.append(tmp)
    bitcoin_data = flash.get('bitcoin')
    if bitcoin_data:
        bitcoin_data = bitcoin_data.decode('utf-8')
    available_stories = json.loads(flash.get('categories').decode('utf-8'))
    return JsonResponse({
        "message": "Success",
        "data": result,
        "bitcoin": bitcoin_data,
        "available_stories": available_stories
    })

def cron_job(requests):
    update_feeds()
    get_bitcoin()
    return JsonResponse({
        "message": "Updated"
    })

def get_bitcoin():
    flash = redis.Redis(host='redis-17256.c14.us-east-1-3.ec2.cloud.redislabs.com', port=17256, db=0, password='qhaH3zeAOgn6t6huFIxQhYx51iEGyEM2')
    res = requests.get(bitcoin)
    if res.status_code == 200:
        data = json.loads(res.text)
        price = data['bpi']['USD']['rate']
        flash.set('bitcoin', price)
    return "Done"

def update_feeds():
    flash = redis.Redis(host='redis-17256.c14.us-east-1-3.ec2.cloud.redislabs.com', port=17256, db=0, password='qhaH3zeAOgn6t6huFIxQhYx51iEGyEM2')
    cwd = os.getcwd()
    file = cwd+'/api/source.json'
    with open(file) as f:
        data = json.load(f)
    to_file = {}
    for category in data['data']:
        current_category = category['category']
        sources = []
        for source in category['sources']:
            result = []
            tmp_titles = []
            count = 0
            feed_result = feedparser.parse(source['link'])
            sources.append(source['name_title'])
            for data in feed_result['entries']:
                if data['title'] not in tmp_titles:
                    tmp_titles.append(data['title'])
                    count += 1
                    tmp_res = {
                        "title": data['title'],
                        "link": data['link']
                    }
                    result.append(tmp_res)
                if count >= 20:
                    break
            to_file[current_category] = {
                "sources": sources
            }
            flash.set(source['name_title'], json.dumps(result))
    flash.set('categories', json.dumps(to_file))


    


