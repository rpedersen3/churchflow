import json

import scrapy
from scrapy_splash import SplashRequest

from quotesbot.processors.findChurchesGoogleSearch import FindChurchesGoogleSearch
from quotesbot.processors.findChurchesGooglePlaces import FindChurchesGooglePlaces

from quotesbot.processors.updateRDFWithCities import UpdateRDFWithCities
from quotesbot.processors.updateRDFWithChurches import UpdateRDFWithChurches


from quotesbot.processors.findChurchStaffWebPagesUsingSearch import FindChurchStaffWebPagesUsingSearch

class chcrawlerSpider(scrapy.Spider):

    name = "chcrawler"

    googleKey = 'abc'

    startURLs = [
        "https://calvarybible.com"
    ]

    # update rdf file with church data
    '''
    updateRDF = UpdateRDFWithCities()
    updateRDF.updateWithCities()

    updateRDF = UpdateRDFWithChurches()
    updateRDF.updateWithChurches()
    '''

    # add churches based on cities
    '''
    churchFinder = FindChurchesGoogleSearch(googleKey)
    churchFinder.findChurches()

    churchFinder = FindChurchesGooglePlaces(googleKey)
    churchFinder.findChurches()
    '''

    # process church info
    churches_file_path = "churches.json"
    with open(churches_file_path, "r") as file:
        churchesData = json.load(file)
    churches = churchesData["churches"]

    for church in churches:

        changed = FindChurchStaffWebPagesUsingSearch.findStaffWebPages(church, googleKey)

        if changed:
            
            # save to churches file
            churchesData["churches"] = churches
            with open(churches_file_path, "w") as json_file:
                json.dump(churchesData, json_file, indent=4)



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

