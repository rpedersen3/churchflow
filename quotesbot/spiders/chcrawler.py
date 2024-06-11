import scrapy
from scrapy_splash import SplashRequest

from quotesbot.findChurchesGoogleSearch import FindChurchesGoogleSearch
from quotesbot.findChurchesGooglePlaces import FindChurchesGooglePlaces

class chcrawlerSpider(scrapy.Spider):

    name = "chcrawler"

    startURLs = [
        "https://calvarybible.com"
    ]

    churchFinder = FindChurchesGoogleSearch()
    churchFinder.findChurches()

    churchFinder = FindChurchesGooglePlaces()
    churchFinder.findChurches()

    # churchFinder.findChurchesUsingSpreadsheet()
    # churchFinder.findChurchesUsingGooglePlaces()
    # churchFinder.findChurchesUsingNonProfitData()
    # churchFinder.findCityDemographicsFromCensusData()
    # churchFinder.findCityDemographics()
    # churchFinder.findCities()
    # churchFinder.findChurches()
    # churchFinder.findCounties()



    def start_requests(self):
        print("............ start_requests ..........")

        lua_script_template = """
                function main(splash, args)  

                    print("url: ", args.url)

                    splash:on_request(function(request)
                    print("request: ", request.url)

                    if request.url ~= 'PAGE_URL' then
                            print("pg: ", request.url)
                            request.abort()
                            return { status = 404, }
                    end


                end)


                    print("go to url", args.url)
                    splash:go(args.url)

                    -- custom rendering script logic...

                    return splash:html()
                end
                """

        for startUrl in self.startURLs:
            print(" request URL: ", startUrl)
            lua_script = lua_script_template.replace("PAGE_URL", startUrl)
            yield SplashRequest(startUrl, self.parse, endpoint='execute',
                                args={
                                    'wait': 0.1,
                                    'images': 1,
                                    'response_body': 1,
                                    'har': 1,
                                    'lua_source': lua_script,
                                })

    def parse(self, response):
        print("parse response")
        pass

