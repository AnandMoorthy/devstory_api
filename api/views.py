from django.shortcuts import render
from django.http import JsonResponse
import json
import requests
import redis
import feedparser

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
feed_list = [
    "product_hunt",
    "coin_desk",
    "hacker_news",
    "tech_crunch",
    "reddit",
    "the_next_web",
    "mashable",
    "gizmodo",
    "lifehacker",
    "makeuseof",
]
feeds = [
    {
        "name": "product_hunt",
        "link": "https://www.producthunt.com/feed?category=tech"
    },
    {
        "name": "coin_desk",
        "link": "http://feeds.feedburner.com/CoinDesk"
    },
    {
        "name": "hacker_news",
        "link": "https://news.ycombinator.com/rss"
    },
    {
        "name": "tech_crunch",
        "link": "http://feeds.feedburner.com/TechCrunch/"
    },
    {
        "name": "reddit",
        "link": "https://www.reddit.com/.rss"
    },
    {
        "name": "the_next_web",
        "link": "https://thenextweb.com/feed/"
    },
    {
        "name": "mashable",
        "link": "http://feeds.mashable.com/Mashable"
    },
    {
        "name": "gizmodo",
        "link": "https://gizmodo.com/rss"
    },
    {
        "name": "lifehacker",
        "link": "https://lifehacker.com/rss"
    },
    {
        "name": "makeuseof",
        "link": "https://www.makeuseof.com/feed/"
    }
]

def dashboard(request):
    print(request.GET.get('data'))
    stories = request.GET.get('data', None)
    if stories is None:
        stories = feed_list
    else:
        stories = stories.split(',')
    result = []
    try:
        flash = redis.Redis(host='localhost', port=6379, db=0)
    except Exception as e:
        print(e)
        feed = []
    for feed in stories:
        hn = flash.get(feed).decode('utf-8')
        tmp = {
            "name": feed,
            "data": json.loads(hn)
        }
        result.append(tmp)
    bitcoin = flash.get('bitcoin')
    if bitcoin:
        bitcoin = bitcoin.decode('utf-8')
    return JsonResponse({
        "message": "Success",
        "data": result,
        "bitcoin": bitcoin
    })

def cron_job(requests):
    update_feeds()
    get_bitcoin()
    return JsonResponse({
        "message": "Updated"
    })

def get_bitcoin():
    url = 'https://api.coindesk.com/v1/bpi/currentprice.json'
    flash = redis.Redis(host='localhost', port=6379, db=0)
    res = requests.get(url)
    if res.status_code == 200:
        data = json.loads(res.text)
        price = data['bpi']['USD']['rate']
        flash.set('bitcoin', price)
    return "Done"

def update_feeds():
    flash = redis.Redis(host='localhost', port=6379, db=0)
    for feed in feeds:
        result = []
        tmp_titles = []
        count = 0
        feed_result = feedparser.parse(feed['link'])
        for data in feed_result['entries']:
            if data['title'] not in tmp_titles:
                tmp_titles.append(data['title'])
                count += 1
                tmp_res = {
                    "title": data['title'],
                    "link": data['link']
                }
                result.append(tmp_res)
            if count >= 5:
                break
        flash.set(feed['name'], json.dumps(result))

def get_hn():
    '''
    This functio  to get the Hacker News Latest Stories
    '''
    result = []
    flash = redis.Redis(host='localhost', port=6379, db=0)
    try:
        response = requests.get(HN_TOP_STORIES)
        stories = json.loads(response.text)[:5]
        for story_id in stories:
            url = HN_STORY_DETAIL+str(story_id)+'.json'
            story = json.loads(requests.get(url).text)
            if 'title' not in story or 'url' not in story:
                pass
            else:
                tmp_res = {
                    "title": story['title'],
                    "url": story.get('url', None)
                }
            result.append(tmp_res)
        flash.set('hn', json.dumps(result))
    except Exception as e:
        print(e)
    return result

def get_ph():
    '''
    This Function to get the Product Hunt Latest Stories
    '''
    flash = redis.Redis(host='localhost', port=6379, db=0)
    headers = {"Authorization": "Bearer "+PH_TOKEN}
    params = {
        "sort_by": "votes_count",
        "order": "desc",
        "search[featured]": True,
        "per_page": 5
    }
    result = []
    try:
        res = json.loads(requests.get(PH_TOP_STORIES, params=params, headers=headers).text)
        for data in res['posts'][:5]:
            tmp_res = {
                "name": data['name'],
                "tagline": data['tagline'],
                "url": data['discussion_url']
            }
            result.append(tmp_res)
        flash.set('ph', json.dumps(result))
    except Exception as e:
        print(e)
    return result


    


