import json

import scrapy
from scrapy_splash import SplashRequest

from quotesbot.utilities.helpers import Helpers

from quotesbot.processors.findChurchesGoogleSearch import FindChurchesGoogleSearch
from quotesbot.processors.findChurchesGooglePlaces import FindChurchesGooglePlaces
from quotesbot.processors.findChurchesOpenStreetMapPlaces import FindChurchesOpenStreetMapPlaces
from quotesbot.processors.findChurchDuplicates import FindChurchDuplicates
from quotesbot.processors.findChurchWebsite import FindChurchWebsite

from quotesbot.processors.updateRDFWithCities import UpdateRDFWithCities
from quotesbot.processors.updateRDFWithChurches import UpdateRDFWithChurches
from quotesbot.processors.updateRDFWithMultiChurchOrgs import UpdateRDFWithMultiChurchOrgs
from quotesbot.processors.updateRDFWithDenominations import UpdateRDFWithDenominations

from quotesbot.processors.updatePersonInfo import UpdatePersonInfo
from quotesbot.processors.updateChurchDenomination import UpdateChurchDenomination

from quotesbot.processors.findChurchStaffWebPagesUsingSearch import FindChurchStaffWebPagesUsingSearch

from quotesbot.processors.updateChurchWithStaffFromStaffWebPages import UpdateChurchWithStaffFromWebPages

class chcrawlerSpider(scrapy.Spider):

    name = "chcrawler"

    googleKey = ""

    churches_file_path = "churches.json"
    with open(churches_file_path, "r") as file:
        churchesData = json.load(file)
    churches = churchesData["churches"]


    startURLs = [
        "https://calvarybible.com"
    ]

    # update rdf file with church data

    '''
    
    updateRDF = UpdateRDFWithDenominations()
    updateRDF.updateRDFWithDenominations()

    updateRDF = UpdateRDFWithCities()
    updateRDF.updateWithCities()

    updateRDF = UpdateRDFWithChurches()
    updateRDF.updateWithChurches()

    

    
    
    updateRDF = UpdateRDFWithMultiChurchOrgs()
    updateRDF.updateRDFWithMultiChurchOrgs()

    updateRDF = UpdateRDFWithColocatedChurches()
    updateRDF.updateRDFWithColocatedChurches()
    '''
    # add churches based on cities
    '''
    churchFinder = FindChurchesGoogleSearch()
    churchFinder.findChurches(googleKey)

    churchFinder = FindChurchesGooglePlaces()
    churchFinder.findChurches(googleKey)


    churchFinder = FindChurchesOpenStreetMapPlaces()
    churchFinder.findChurches()


    churchFinder = FindChurchDuplicates()
    churchFinder.findChurchDuplicates()


    churchFinder = FindChurchWebsite()
    churchFinder.findChurchWebsite()

    '''
    # process church info


    '''
    name = "cindy norton"
    url = "https://thechurchco-production.s3.amazonaws.com/uploads/sites/6087/2023/02/CelebrationChurchHeadshotsAlecSavig-22-800x800.jpg"
    updatePersonInfo = UpdatePersonInfo()
    fullname, firstname, lastname, nameRace, nameRacePercent = updatePersonInfo.extractNameFromText(name)
    print("*********** name", fullname, ", ", nameRace, ", ", nameRacePercent)

    photoRace, photoRacePercent, age, gender = updatePersonInfo.extractRaceFromPhoto(url)
    print("*********** race", photoRace, ", ", photoRacePercent, ", ", age, ", ", gender)
    

    updatePersonInfo = UpdatePersonInfo()
    updatePersonInfo.extractRaceFromPhoto(
        "https://www.houseofhopeaurora.org/wp-content/uploads/2022/04/Pastor-Richard-Lewis-e1649862402960.jpg")
    '''

    count = 0
    for church in churches:


        if count > 10000:
            break

        changed = False

        '''
        find = FindChurchStaffWebPagesUsingSearch()
        changed = find.findStaffWebPages(church, googleKey)

        updateWithStaff = UpdateChurchWithStaffFromWebPages()
        updateWithStaff.appendWebPagesBasedOnStaff(church, startURLs)
        '''


        if "name" in church:

            if church["name"] == "Calvary Church Monument":

                count = count + 1

                '''
                churchFinder = FindChurchesGooglePlaces()
                changed = churchFinder.updateChurch(church, googleKey)
                
    
                updatePersonInfo = UpdatePersonInfo()
                changed = updatePersonInfo.updateContactInfo(church)
                
                '''
                updateChurchInfo = UpdateChurchDenomination()
                changed = updateChurchInfo.updateChurchDenomination(church)

                if changed:

                    # save to churches file
                    churchesData["churches"] = churches
                    with open(churches_file_path, "w") as json_file:
                        json.dump(churchesData, json_file, indent=4)



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

        helpers = Helpers()
        church, isHomePage = helpers.findChurch(self.churches, response.url)
        if church is not None and "name" in church:

            changed = False

            '''
            updateWithStaff = UpdateChurchWithStaffFromWebPages()
            changed = updateWithStaff.updateChurchWithStaffFromWebPages(church, response)
            '''

            if changed:
                # save to churches file
                self.churchesData["churches"] = self.churches
                with open(self.churches_file_path, "w") as json_file:
                    json.dump(self.churchesData, json_file, indent=4)

        pass

