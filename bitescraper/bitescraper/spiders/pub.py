from datetime import datetime
import re
import scrapy
from time import time

from ..items import PubItem, CommentItem

class PubSpider(scrapy.Spider):
    name = 'pubspider'
    start_urls = ['http://www.beerintheevening.com/pubs/results.shtml?l=London']
    base_url = 'http://www.beerintheevening.com'

    def parse(self, response):
        """parse the response to return items"""
        # find pub links
        pubs = response.xpath((
            '//table[@class="pubtable"]'
            '//tr[@class="pubtable"]'
            '/td/b[contains(text(), "Name:")]'
            '/a[1]/@href'
            )).extract()
        for pub in pubs:
            yield scrapy.Request(self.base_url + pub, callback = self.parsePub)
        # go to next page?
        try:
            # yes
            next_page_url = response.xpath('//a[contains(text(), ">> next 20 >>")]/@href').extract()[0]
            yield scrapy.Request(self.base_url + next_page_url, callback = self.parse)
        except IndexError:
            # no
            pass

    def parsePub(self, response):
        """parse the pub response into an item"""
        # get the pub info
        pub = PubItem()
        # this regex is integral to how we link data, no point in catching
        # since data which fails it is useless to us
        pub['source_url'] = response.url
        pub['source_pub_id'] = int(re.match(r'.*\/([0-9]+)\/.*', response.url).group(1))
        # if this fails, we have no name so it's worthless
        pn = response.xpath('//h1[1]/text()').extract()[0]
        try:
            # if this fails, the name is non standard
            pub['name'] = response.xpath('//h1[1]/text()').extract()[0].split(',')[0].strip()
        except IndexError:
            # but still good to keep
            pub['name'] = pn.strip()
        # address should be good for all, else it's a bit pointless
        pub['address'] = response.xpath('//div[contains(@class, "info")]/p/b[text()="Address:"]/following-sibling::text()[1]').extract()[0].strip()
        # not all pubs have websites
        try:
            pub['website'] = response.xpath('//div[contains(@class, "info")]/p/b[contains(text(), "Website:")]/following-sibling::a/@href').extract()[0]
        except IndexError:
            pass
        try:
            pub['chain'] =  response.xpath('//div[contains(@class, "info")]/p/b[contains(text(), "Chain:")]/following-sibling::a/text()').extract()[0]
        except:
            pass

        # nearby tubes
        l = response.xpath('//p/img[@alt="Nearest tube stations"]/following-sibling::a/text()').extract()
        pub['nearby_tube_stations'] = [
            {
                'name': t[0],
                'distance': t[1],
            }
            for t in zip(l[::2], l[1::2])
        ]
        l = response.xpath('//p/img[@alt="Nearest trains stations"]/following-sibling::a/text()').extract()
        pub['nearby_train_stations'] = [
            {
                'name': t[0],
                'distance': t[1],
            }
            for t in zip(l[::2], l[1::2])
        ]
        # don't hate me for loving listcomps
        pub['facilities'] = [
            f.strip()
            for f in ','.join(
                response.xpath('//li[contains(@class, "factype-")]/text()').extract()
            ).split(',')
        ]


        try:
            pub['bite_user_rating'] = float(response.xpath('//div[@class="suggested-info"][contains(text(), "Current user rating:")]/b/text()').extract()[0].split('/')[0])
            pub['bite_number_ratings'] = int(response.xpath('//div[@class="suggested-info"][contains(text(), "Current user rating:")]/b/following-sibling::text()').extract()[0].split(' ')[-2])
        except:
            pass

        pub['last_scraped'] = int(time())

        yield pub

        # scrape comments?

        try:
            # yes
            comments_url = '/pubs/comments.shtml/' + str(pub['source_pub_id'])
            yield scrapy.Request(self.base_url + comments_url, callback = self.parseComments)
        except IndexError:
            # no
            pass

    def parseComments(self, response):
        """parse a comments page"""
        td = response.xpath('//table[@class="pubtable"]//tr[@class="pubtable"]/td')
        for cr in td:
            # loop through and turn into comments

            comment = CommentItem()
            comment['source_pub_id'] = int(response.url.split('/')[-1])
            comment['source_comment_id'] = int(cr.xpath('div/small/a[text()="Report this for removal"]/@href').extract()[0].split('=')[-1])
            comment['comment'] =  ' '.join(cr.xpath('text()').extract()).strip()
            try:
                comment['username'] = cr.xpath('div/small/a[contains(@href, "user_profile")]/text()').extract()[0]
                comment['created'] = datetime.strptime(
                    cr.xpath(
                        'div[2]/small/text()'
                    ).extract()[0].split('-')[-1].strip(),
                    '%d %b %Y %H:%M'
                )
            except IndexError:
                comment['username'] = 'anonymous'

            yield comment
