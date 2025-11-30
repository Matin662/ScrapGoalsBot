import aiohttp
import random
from configs.settings import NITTER_INSTANCES
from helpers.cleaner import clean_caption

async def get_latest_tweets(username: str, since_id: int = 0):
    instance = random.choice(NITTER_INSTANCES)
    url = f"{instance}/{username}/rss"
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url, timeout=15) as resp:
                if resp.status != 200:
                    return []
                text = await resp.text()
        except:
            return []

    import xml.etree.ElementTree as ET
    from bs4 import BeautifulSoup
    
    try:
        root = ET.fromstring(text)
    except:
        return []

    tweets = []
    for item in root.findall("./channel/item"):
        title = item.find("title").text
        link = item.find("link").text
        tweet_id = int(link.split("/")[-1].split("#")[0])
        
        if tweet_id <= since_id:
            continue

        description = item.find("description").text or ""
        soup = BeautifulSoup(description, "html.parser")
        
        video_tag = soup.find("video")
        if not video_tag or not video_tag.find("source"):
            continue
            
        video_url = video_tag.find("source")["src"]
        if not video_url.startswith("http"):
            video_url = instance.rstrip("/") + video_url

        caption = clean_caption(title)
        
        tweets.append({
            "id": tweet_id,
            "video_url": video_url,
            "caption": caption
        })
    
    return sorted(tweets, key=lambda x: x["id"], reverse=True)
