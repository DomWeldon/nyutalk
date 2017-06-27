# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class PubItem(scrapy.Item):
    # define the fields for your item here like:
    source_pub_id = scrapy.Field()

    name = scrapy.Field()
    address = scrapy.Field()
    website = scrapy.Field()

    facilities = scrapy.Field()

    bite_user_rating = scrapy.Field()
    bite_number_ratings = scrapy.Field()

    nearby_tube_stations = scrapy.Field()
    nearby_train_stations = scrapy.Field()

    last_scraped = scrapy.Field()
    source_url = scrapy.Field()

class CommentItem(scrapy.Item):
    source_comment_id = scrapy.Field()
    source_pub_id = scrapy.Field()
    comment = scrapy.Field()
    username = scrapy.Field()
    created = scrapy.Field()
