# make requests
from pymongo import MongoClient
from dotenv import dotenv_values
from bson.objectid import ObjectId
from urllib.request import urlopen, Request
from PIL import Image
from loguru import logger


config = dotenv_values(".env")

client = MongoClient(config['DB_URI'])
db = client.samples
while True:
    posts = db.posts.find({ "isPortrait": 
    { "$exists": False }
    }).limit(200)
    for post in posts:
        # get the image dimension and update the db
        # 0 for true, 1 for false, 0 for unkown and delete
        try:
            req = Request(post['url'], headers={'User-Agent' : "Magic Browser"}) 
            con = urlopen(req)
            image = Image.open(con)
            width, height = image.size
            is_portrait = height > width
            # set as true/false
            db.posts.update_one({
                "_id": ObjectId(post["_id"])
            }, { "$set": {"isPortrait": is_portrait}})
            logger.info(f"Successfully update img ${post['url']}")
        except Exception as e:
            # delete item
            logger.error(f"Task failed for URL {post['url']}")
            db.posts.delete_one({
                "_id": ObjectId(post["_id"])
            })     
    if posts.retrieved == 0:
        break

client.close()

