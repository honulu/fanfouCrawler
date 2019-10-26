from scrapy import Spider
from scrapy.http import FormRequest
from scrapy import Request
from scrapy.selector import Selector
import re

# commonUrl = "http://fanfou.com/~RLhcIDBjZAM/p."
commonUrl = "http://fanfou.com/wangxing/p."
def authentication_failed(response):
    # TODO: Check the contents of the response and return True if it failed
    # or False if it succeed.
    pass

class FanfouSpider(Spider):
    name = "fanfou"
    # the login url
    start_urls = [
        'http://fanfou.com/login',
    ]

    def parse(self, response):
        token = response.xpath('//input[@name="token"]/@value').get()
        userName = "***********"
        userPasswd = "***********"
        data = {
            "loginname": userName,
            "loginpass": userPasswd,
            "action": "login",
            "token": token
        }
        return FormRequest.from_response(response,
                                         formdata=data,
                                         callback=self.scrape_pages)


    def scrape_pages(self, response):
        if authentication_failed(response):
            self.logger.error("fanfou login failed")
            return
        # next_page_url = "http://fanfou.com/~RLhcIDBjZAM"
        next_page_url = "http://fanfou.com/wangxing"
        yield Request(next_page_url, callback=self.begin_scrape)

    def begin_scrape(self, response):
        print("@@@@@@@@@@@@@@@@@@@had scrapy ", response.url)
        for m in response.xpath('//ol/li'):
            xx = m.get()
            yield {
                # get the content using re
                "content" : re.sub("<.*?>","",Selector(text=xx).xpath('//span[@class="content"]').get()),
                # get the message photo
                "messPhoto" : Selector(text=xx).xpath('//span[@class="content"]/a[@class="photo zoom "]/@href').get(),
                # 转发回复人的id
                "ids" : Selector(text=xx).xpath('//a[@class="former"]/@href').getall(),
                # 转发回复的人
                "names" : Selector(text=xx).xpath('//a[@class="former"]/text()').getall(),
                # get the app this message used
                "app" : Selector(text=xx).xpath('//span[@class="method"]/a/text()').get(),
                # get the time that message sended
                "time" : Selector(text=xx).xpath('//a[@class="time"]/@title').get(),
                # get my id
                "myId" : Selector(text=xx).xpath('//a[@class="avatar"]/@href').getall(),
                # get my name
                "myName" : Selector(text=xx).xpath('//a[@class="avatar"]/@title').getall(),
                # get my photo
                "myPhoto" : Selector(text=xx).xpath('//img[@alt="myname"]/@src').get()
            }
        currentPage = int(response.xpath('//li[@class="current"]/text()').get())
        if "下一页" in response.xpath('//ul[@class="paginator"]').get():
            print("@@@@@@@@@@@@@@@@@@@will scrapy", str(currentPage+1), "page")
            yield Request(response.urljoin(commonUrl+str(currentPage+1)), callback=self.begin_scrape)
        else:
            print("@@@@@@@@@@@@@@@@@@@end scrapy, ALL page is ",currentPage)
        