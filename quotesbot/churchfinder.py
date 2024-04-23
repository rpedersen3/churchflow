
import os
import json
from googleapiclient.discovery import build
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import time
from urllib.parse import urlparse
import re

class ChurchInfo:
    name = "churchinfo"


    name: str
    description: str
    link: str

    def __init__(self, name: str, description: str, link: str) -> None:
        self.name = name
        self.description = description
        self.link = link

class ChurchFinder:
    name = "churchfinder"

    churches_file_path = "churches.json"
    with open(churches_file_path, "r") as file:
        churchesData = json.load(file)
    churches = churchesData["churches"]

    def findCurrentChurch(self, churches, url, street, zipcode):



        urlParse = urlparse(url)
        urlDomain = urlParse.netloc.replace("www.", "")

        isHomePage = False
        currentChurch = None
        for church in churches:

            if "link" in church:
                churchParse = urlparse(church["link"])
                churchDomain = churchParse.netloc.replace("www.", "")

                if churchDomain == urlDomain:
                    currentChurch = church

                    return currentChurch

        #street match
        for church in churches:

            if "addressInfo" in church and "street" in church["addressInfo"] and \
                    street is not None and street != "" and \
                    zipcode is not None and zipcode != "":

                churchStreetParts = church["addressInfo"]["street"].split()
                streetParts = street.split()

                if len(churchStreetParts) > 0 and len(streetParts) > 0:

                    if churchStreetParts[0].lower() == streetParts[0].lower():

                        if church["addressInfo"]["zipcode"] == zipcode:

                            print("*** street match: ", church["addressInfo"]["street"], ", to list: ", street)
                            currentChurch = church

                            return currentChurch



        return currentChurch

    def findChurchesUsingSpreadsheet(self):

        # get churches
        churches = self.churches

        # get cities
        file_path = "coloradoFrontRangeCities.json"
        with open(file_path, "r") as file:
            citiesData = json.load(file)

        # cycle through cities looking for church web sites
        cities = citiesData["cities"]

        # get spreadsheet
        spreadsheet_path = 'ChurchListExportv20.txt'


        # Read data from file
        with open(spreadsheet_path, 'r') as file:
            spreadsheetLines = file.readlines()

            data = []
            frontRangeData = []

            found = 0
            process = False
            for spreadsheetLine in spreadsheetLines:

                spreadsheetLine = spreadsheetLine.rstrip('\r\n')
                spreadsheetParts = spreadsheetLine.split('\t')

                id = spreadsheetParts[0]
                active = spreadsheetParts[2]
                name = spreadsheetParts[4]
                url = spreadsheetParts[5]
                attendance = spreadsheetParts[6]
                size = spreadsheetParts[7]
                denomination = spreadsheetParts[8]
                location = spreadsheetParts[9]
                pastor = spreadsheetParts[15]
                email = spreadsheetParts[16]
                phone = spreadsheetParts[17]
                linkedin = spreadsheetParts[19]
                firstname = spreadsheetParts[23]
                lastname = spreadsheetParts[24]

                churchname = spreadsheetParts[26]
                street = spreadsheetParts[27]
                city = spreadsheetParts[28]
                state = spreadsheetParts[29]
                zipcode = spreadsheetParts[30]

                process = True


                if url != "" and active == "1":

                    if url.find("https://") == -1:
                        url = "https://" + url

                    url = url.strip()
                    url = re.sub(r'\s+', ' ', url)


                    match = False

                    print("url: ", url)
                    selectedChurch = self.findCurrentChurch(churches, url, street, zipcode)
                    if (selectedChurch is not None):
                        if "name" in selectedChurch:
                            link = ""
                            if "link" in selectedChurch:
                                link = selectedChurch["link"]
                            print("MATCH name: ", selectedChurch["name"], ", list name: ", name, ", active: ", active)
                            print("pastor: ", pastor, ", email: ", email)
                            #print("url     : ", link)
                            #print("list url: ", url)
                            print("")

                            leadPastor = {
                                "name": pastor,
                                "listId": id
                            }

                            if email != "":
                                leadPastor["email"] = email

                            if linkedin != "":
                                leadPastor["linkedin"] = linkedin

                            selectedChurch["leadPastor"] = leadPastor
                            selectedChurch["listId"] = id

                            match = True

                    if match == False:

                        # create new record
                        church = {
                            "name": name,
                            "link": url
                        }

                        leadPastor = {
                            "name": pastor,
                            "listId": id
                        }

                        if street != "":
                            church["address"] = street + ", " + city + ", " + state + ", " + zipcode

                        if email != "":
                            leadPastor["email"] = email

                        if linkedin != "":
                            leadPastor["linkedin"] = linkedin

                        church["leadPastor"] = leadPastor
                        church["listId"] = id

                        churches.append(church)


        self.saveChurches()




    def findCities(self):
        #data from https://www.gigasheet.com/sample-data/spreadsheet-list-of-all-cities-in-coloradocsv

        cities_file_path = 'cities.txt'

        frontRangeLatMin = 38.2
        frontRangeLatMax = 40.7

        frontRangeLonMin = -105.5
        frontRangeLonMax = -104.5

        # Read data from file
        with open(cities_file_path, 'r') as file:
            cityLines = file.readlines()


            data = []
            frontRangeData = []

            for cityLine in cityLines:

                cityLine = cityLine.rstrip('\r\n')
                cityParts = cityLine.split('\t')

                # Append parsed data to the list
                city = {
                    "name": cityParts[0],
                    "fips": cityParts[3],
                    "lat": float(cityParts[6]),
                    "lon": float(cityParts[7]),
                    "population": int(cityParts[8])
                }
                data.append(city)

                if city["lat"] > frontRangeLatMin and city["lat"] < frontRangeLatMax and city["lon"] > frontRangeLonMin and city["lon"] < frontRangeLonMax:
                    frontRangeData.append(city)



            '''
            file_path = "coloradoCities.json"
            citiesData = {}
            citiesData["cities"] = data

            with open(file_path, "w") as json_file:
                json.dump(citiesData, json_file, indent=4)
            '''

            file_path = "coloradoFrontRangeCities.json"
            citiesData = {}
            citiesData["cities"] = frontRangeData

            with open(file_path, "w") as json_file:
                json.dump(citiesData, json_file, indent=4)


    def getValue(self, soup, type):

        value = None
        select = 'tr[data-mnemonic="' + type + '"]'
        tr_elements = soup.select(select)
        for row in tr_elements:
            cells = row.select('td[data-isnumeric="1"]')
            for cell in cells:
                value = cell.get("data-value")

        return value

    def getValueByClass(self, soup, elType, clName):

        value = None
        select = elType + '[class="' + clName + '"]'

        print("select: ", select)
        elements = soup.select(select)
        for el in elements:
            value = el.text
            if value != None and value != "":
                break

        return value

    def getCity(self, cities, name):
        for city in cities:
            if (name.lower().find(city["name"].lower()) >= 0):
                return city

        return None
    def findCityDemographicsFromCensusData(self):

        file_path = "coloradoFrontRangeCities.json"
        with open(file_path, "r") as file:
            citiesData = json.load(file)

        cities = citiesData["cities"]


        # https://www.census.gov
        # https://data.census.gov/table/DECENNIALDP2020.DP1?g=040XX00US08,08$1600000&y=2020&d=DEC%20Demographic%20Profile
        data_file_path = 'coloradodemographics.txt'

        # Read data from file
        with open(data_file_path, 'r') as file:

            dataLines = file.readlines()

            data = []
            frontRangeData = []

            print("data lines: ", len(dataLines))

            i = 0
            for dataLine in dataLines:

                dataLine = dataLine.rstrip('\r\n')
                dataParts = dataLine.split('\t')

                cityName = dataParts[1]
                selectedCity = self.getCity(cities, cityName)


                #if selectedCity == None:
                    #print("city not found: ", cityName)

                if selectedCity != None:
                    print("update city data: ", cityName)

                    totalPopulation = int(dataParts[2])

                    #print("pop: ", selectedCity["population2020"], ", value: ", totalPopulation)
                    selectedCity["population2020"] = totalPopulation

                    #selectedCity["population2010"] = int(0)

                    under5 = int(dataParts[3])
                    age5to9 = int(dataParts[4])
                    age10to14 = int(dataParts[5])
                    age15to19 = int(dataParts[6])
                    ageOver18 = int(dataParts[22])
                    ageUnder18 = totalPopulation - ageOver18

                    under5Percent = float(dataParts[163])
                    over18Percent = float(dataParts[182])

                    #print("under5Percent: ", selectedCity["under5Percent"], ", value: ", under5Percent)
                    selectedCity["under5Percent"] = under5Percent
                    #print("under18Percent: ", selectedCity["under18Percent"], ", value: ", 100.0 - over18Percent)
                    selectedCity["under18Percent"] = 100.0 - over18Percent


                    age65to69 = int(dataParts[16])
                    age70to74 = int(dataParts[17])
                    age75to79 = int(dataParts[18])
                    age80to84 = int(dataParts[19])
                    age85plus = int(dataParts[20])
                    over65 = int(dataParts[25])
                    over65Percent = (over65 * 100.0) / totalPopulation

                    #print("over65Percent: ", selectedCity["over65Percent"], ", value: ", over65Percent)
                    selectedCity["over65Percent"] = float(over65Percent)

                    males = int(dataParts[26])
                    malePercentage = (males * 100.0) / totalPopulation
                    femalePercentage = 100.0 - malePercentage

                    selectedCity["malePercentage"] = float(malePercentage)
                    selectedCity["femalePercentage"] = float(femalePercentage)

                    raceCount = int(dataParts[86])
                    raceWhite = int(dataParts[87])
                    raceBlack = int(dataParts[88])
                    raceIndian = int(dataParts[89])
                    raceAsian = int(dataParts[90])


                    whitePercent = float(dataParts[239])
                    blackPercent = float(dataParts[240])
                    indianPercent = float(dataParts[241])
                    asianPercent = float(dataParts[242])

                    hispanicPercent = float(dataParts[254])

                    #print("white: ", selectedCity["whitePercent"], ", value: ", whitePercent)
                    selectedCity["whitePercent"] = whitePercent
                    #print("blackPercent: ", selectedCity["blackPercent"], ", value: ", blackPercent)
                    selectedCity["blackPercent"] = blackPercent
                    selectedCity["indianPercent"] = indianPercent
                    selectedCity["asianPercent"] = asianPercent

                    #print("hispanic: ", selectedCity["hispanicPercent"], ", value: ", hispanicPercent)
                    selectedCity["hispanicPercent"] = hispanicPercent

                    '''
                    #selectedCity["veterans"] = int(veterans)

                    households = int(dataParts[133])
                    selectedCity["households"] = int(households)

                    selectedCity["householdsWithComputerPercent"] = float(householdsWithComputerPercent)

                    selectedCity["householdsWithInternetPercent"] = float(householdsWithInternetPercent)

                    selectedCity["highSchoolPercent"] = float(highSchoolPercent)

                    selectedCity["bachelorsPercent"] = float(bachelorsPercent)

                    selectedCity["retailSalesPerCapita"] = float(retailSalesPerCapita)

                    selectedCity["householdIncome"] = float(householdIncome)

                    selectedCity["populationPerSquareMile"] = float(populationPerSquareMile)

                    selectedCity["censusFips"] = fipsCode
                    
                    '''

            citiesData["cities"] = cities

            with open(file_path, "w") as json_file:
                json.dump(citiesData, json_file, indent=4)



    def findCityDemographics(self):

        # https://www.census.gov
        service = build(
            "customsearch", "v1", developerKey=""
        )

        file_path = "coloradoFrontRangeCities.json"
        with open(file_path, "r") as file:
            citiesData = json.load(file)

        cities = citiesData["cities"]
        selectedCity = None
        for city in cities:

            selectedCity = city

            html = ""

            # get url and then HTML
            # https://programmablesearchengine.google.com/controlpanel/all
            firstPartOfName = selectedCity["name"].split()[0].lower()
            query = "quickfacts " + selectedCity["name"] + " colorado"
            print("google query for: ", query)
            res = (
                service.cse()
                .list(
                    q=query,
                    cx="877445d005a4d4258"
                )
                .execute()
            )

            if "items" in res:

                for item in res["items"]:

                    link = item["link"]
                    if link.find("quickfacts") >= 0 and \
                            link.find("colorado") >= 0 and \
                            link.find("PST") >= 0 and \
                            link.find(firstPartOfName) >= 0:
                        print("link: ", link)


                        user_agent = {'User-agent': 'Mozilla/5.0'}
                        response = requests.get(link, headers = user_agent, allow_redirects=True)
                        if response.status_code != 200:
                            print("bad response: ", response.status_code)

                        if response.status_code == 200:
                            html = response.text
                            break

                soup = BeautifulSoup(html, 'html.parser')

                population2020 = self.getValue(soup, "POP010220")
                population2010 = self.getValue(soup, "POP010210")

                under5 = self.getValue(soup, "AGE135222")
                under18 = self.getValue(soup, "AGE295222")
                over65 = self.getValue(soup, "AGE775222")
                female = self.getValue(soup, "SEX255222")

                white = self.getValue(soup, "RHI125222")
                black = self.getValue(soup, "RHI225222")
                indian = self.getValue(soup, "RHI325222")
                asian = self.getValue(soup, "RHI425222")
                hispanic = self.getValue(soup, "RHI725222")

                veterans = self.getValue(soup, "VET605222")

                households = self.getValue(soup, "HSD410222")
                personsPerHousehold = self.getValue(soup, "HSD310222")
                languageOtherThanEnglishPercent = self.getValue(soup, "POP815222")
                householdsWithComputerPercent = self.getValue(soup, "COM100222")
                householdsWithInternetPercent = self.getValue(soup, "INT100222")

                highSchoolPercent = self.getValue(soup, "EDU635222")
                bachelorsPercent = self.getValue(soup, "EDU685222")

                retailSalesPerCapita = self.getValue(soup, "RTN131217")
                householdIncome = self.getValue(soup, "INC110222")

                populationPerSquareMile = self.getValue(soup, "POP060220")

                fipsCode = self.getValue(soup, "fips")


                if population2020 != None:
                    print("has 2020 population")
                    selectedCity["population2020"] = int(population2020)
                elif "population2020" in selectedCity:
                    del selectedCity["population2020"]

                if population2010 != None:
                    selectedCity["population2010"] = int(population2010)
                elif "population2010" in selectedCity:
                    del selectedCity["population2010"]

                if under5 != None:
                    selectedCity["under5Percent"] = float(under5)
                elif "under5Percent" in selectedCity:
                    del selectedCity["under5Percent"]

                if under18 != None:
                    selectedCity["under18Percent"] = float(under18)
                elif "under18Percent" in selectedCity:
                    del selectedCity["under18Percent"]
                if over65 != None:
                    selectedCity["over65Percent"] = float(over65)
                elif "over65Percent" in selectedCity:
                    del selectedCity["over65Percent"]
                if female != None:
                    selectedCity["femalePercent"] = float(female)
                elif "femalePercent" in selectedCity:
                    del selectedCity["femalePercent"]

                if white != None:
                    selectedCity["whitePercent"] = float(white)
                elif "whitePercent" in selectedCity:
                    del selectedCity["whitePercent"]
                if black != None:
                    selectedCity["blackPercent"] = float(black)
                elif "blackPercent" in selectedCity:
                    del selectedCity["blackPercent"]
                if indian != None:
                    selectedCity["indianPercent"] = float(indian)
                elif "indianPercent" in selectedCity:
                    del selectedCity["indianPercent"]
                if asian != None:
                    selectedCity["asianPercent"] = float(asian)
                elif "asianPercent" in selectedCity:
                    del selectedCity["asianPercent"]
                if hispanic != None:
                    selectedCity["hispanicPercent"] = float(hispanic)
                elif "hispanicPercent" in selectedCity:
                    del selectedCity["hispanicPercent"]

                if veterans != None:
                    selectedCity["veterans"] = int(veterans)
                elif "veterans" in selectedCity:
                    del selectedCity["veterans"]
                if households != None:
                    selectedCity["households"] = int(households)
                elif "households" in selectedCity:
                    del selectedCity["households"]
                if householdsWithComputerPercent != None:
                    selectedCity["householdsWithComputerPercent"] = float(householdsWithComputerPercent)
                elif "householdsWithComputerPercent" in selectedCity:
                    del selectedCity["householdsWithComputerPercent"]
                if householdsWithInternetPercent != None:
                    selectedCity["householdsWithInternetPercent"] = float(householdsWithInternetPercent)
                elif "householdsWithInternetPercent" in selectedCity:
                    del selectedCity["householdsWithInternetPercent"]
                if highSchoolPercent != None:
                    selectedCity["highSchoolPercent"] = float(highSchoolPercent)
                elif "highSchoolPercent" in selectedCity:
                    del selectedCity["highSchoolPercent"]
                if bachelorsPercent != None:
                    selectedCity["bachelorsPercent"] = float(bachelorsPercent)
                elif "bachelorsPercent" in selectedCity:
                    del selectedCity["bachelorsPercent"]
                if retailSalesPerCapita != None:
                    selectedCity["retailSalesPerCapita"] = float(retailSalesPerCapita)
                elif "retailSalesPerCapita" in selectedCity:
                    del selectedCity["retailSalesPerCapita"]
                if householdIncome != None:
                    selectedCity["householdIncome"] = float(householdIncome)
                elif "householdIncome" in selectedCity:
                    del selectedCity["householdIncome"]
                if populationPerSquareMile != None:
                    selectedCity["populationPerSquareMile"] = float(populationPerSquareMile)
                elif "populationPerSquareMile" in selectedCity:
                    del selectedCity["populationPerSquareMile"]
                if fipsCode != None:
                    selectedCity["censusFips"] = fipsCode
                elif "censusFips" in selectedCity:
                    del selectedCity["censusFips"]

                file_path = "coloradoFrontRangeCities.json"
                citiesData = {}
                citiesData["cities"] = cities

                with open(file_path, "w") as json_file:
                    json.dump(citiesData, json_file, indent=4)



    def setAddressInfoWithGoogleAddressComponents(self, components, currentChurch):

        addressInfo = {}
        if "addressInfo" in currentChurch:
            addressInfo = currentChurch["addressInfo"]

        streetNumber = None
        streetRoute = None
        city = None
        county = None
        state = None
        country = None
        zipcode = None

        for component in components:

            if component["types"][0] == "street_number":
                streetNumber =  component["longText"]
            if component["types"][0] == "route":
                streetRoute =  component["longText"]
            if component["types"][0] == "locality":
                city = component["longText"]
            if component["types"][0] == "administrative_area_level_2":
                county = component["longText"]
            if component["types"][0] == "administrative_area_level_1":
                state = component["shortText"]
            if component["types"][0] == "country":
                country = component["shortText"]
            if component["types"][0] == "postal_code":
                zipcode = component["shortText"]

            if streetNumber is not None and streetRoute is not None:
                addressInfo["street"] = streetNumber + " " + streetRoute
            if city is not None:
                addressInfo["city"] = city
            if county is not None:
                addressInfo["county"] = county
            if state is not None:
                addressInfo["state"] = state
            if country is not None:
                addressInfo["country"] = country
            if zipcode is not None:
                addressInfo["zipcode"] = zipcode

        currentChurch["addressInfo"] = addressInfo

    def saveChurches(self):

        # save to churches file
        self.churchesData["churches"] = self.churches
        with open(self.churches_file_path, "w") as json_file:
            json.dump(self.churchesData, json_file, indent=4)

    def updateChurchWithGoogleResults(self, currentChurch, data):

        if "id" in data:
            currentChurch["googlePlaceId"] = data["id"]
            print("google place id: ", currentChurch["googlePlaceId"])

        if "displayName" in data:
            currentChurch["name"] = data["displayName"]["text"]
            currentChurch["displayName"] = data["displayName"]["text"]
            print("google display name: ", currentChurch["displayName"])

        if "formattedAddress" in data:
            currentChurch["formattedAddress"] = data["formattedAddress"]
            print("google add: ", data["formattedAddress"])

        if "primaryType" in data:
            currentChurch["propertyType"] = data["primaryType"]
            print("google primaryType: ", data["primaryType"])
        elif "types" in data and len(data["types"]) > 0:
            propertyType = data["types"][0]
            currentChurch["propertyType"] = propertyType
            print("google propertyType: ", propertyType)

        if "location" in data:
            currentChurch["latitude"] = str(data["location"]["latitude"])
            currentChurch["longitude"] = str(data["location"]["longitude"])
            print("google latitude: ", str(data["location"]["latitude"]))

        if "rating" in data:
            currentChurch["rating"] = str(data["rating"])
            print("google rating: ", currentChurch["rating"])

        if "addressComponents" in data:
            self.setAddressInfoWithGoogleAddressComponents(data["addressComponents"], currentChurch)

        if "websiteUri" in data:
            currentChurch["link"] = data["websiteUri"]
            currentChurch["websiteUri"] = data["websiteUri"]
            print("google websiteUri: ", data["websiteUri"])

        if "nationalPhoneNumber" in data:
            currentChurch["phone"] = data["nationalPhoneNumber"]
            currentChurch["nationalPhoneNumber"] = data["nationalPhoneNumber"]
            print("google nationalPhoneNumber: ", data["nationalPhoneNumber"])

        if "businessStatus" in data:
            currentChurch["businessStatus"] = data["businessStatus"]
            print("google businessStatus: ", data["businessStatus"])


    def getChurchByGoogleId(self, googleId):

        for church in self.churches:
            if "googlePlaceId" in church:
                if church["googlePlaceId"] == googleId:
                    return church

        return None
    def findChurchesUsingGooglePlaces(self):

        # get cities
        file_path = "coloradoFrontRangeCities.json"
        with open(file_path, "r") as file:
            citiesData = json.load(file)

        # cycle through cities looking for church web sites
        cities = citiesData["cities"]
        selectedCity = None
        count = 1
        for city in cities:

            if "crawled-google-places" not in city:

                city["crawled-google-places"] = str(datetime.now())

                time.sleep(1)

                api_key = 'abcdef'
                endpoint = 'https://places.googleapis.com/v1/places:searchText' + "?fields=*&key=" + api_key

                query = city["name"] + " Colorado, Church"
                payload = {
                    "textQuery": query
                }
                if api_key == '':
                    print("api key is not set for getAddressInfoUsingGooglePlaces")
                    return

                time.sleep(1)


                response = requests.post(url=endpoint, json=payload)
                data = response.json()

                print("************* json returned: ", data)

                if "places" in data:
                    places = data["places"]
                    for place in places:

                        id = place["id"]
                        currentChurch = self.getChurchByGoogleId(id)

                        if currentChurch is None:
                            print("add church")
                            currentChurch = {}
                            self.updateChurchWithGoogleResults(currentChurch, place)

                            self.churches.append(currentChurch)
                            self.saveChurches()

    def findChurches(self):

        #https://programmablesearchengine.google.com/controlpanel/overview?cx=d744719d644574dd7
        service = build(
            "customsearch", "v1", developerKey=""
        )

        # get churches
        churchesData = None
        churches_file_path = "churches.json"
        with open(churches_file_path, "r") as file:
            churchesData = json.load(file)

        churches = churchesData["churches"]
        if churches == None:
            churches = []

        # get cities
        file_path = "coloradoFrontRangeCities.json"
        with open(file_path, "r") as file:
            citiesData = json.load(file)

        # cycle through cities looking for church web sites
        cities = citiesData["cities"]
        selectedCity = None
        count = 1
        for city in cities:

            if "crawled" not in city:

                city["crawled"] = str(datetime.now())
                city["crawled-city"] = city["name"]

                time.sleep(5)

                count = count + 1
                if count > 100:
                    break

                starts = [1, 11, 21, 31, 41, 51]

                for st in starts:

                    query = "'" + city["name"] + "' colorado christian church websites"
                    print("query: ", query)
                    res = (
                        service.cse()
                        .list(
                            q=query,
                            cx="d744719d644574dd7",
                            start=st
                            #cx="01757666212468239146:omuauf_lfve",
                        )
                        .execute()
                    )
                    print("--------------------------------------")
                    print(res)
                    print("--------------------------------------")

                    found = 0
                    for item in res["items"]:

                        link = item["link"]
                        dashCount = len(link.split("/"))
                        print("link: ", link, ",  dashCount: ", dashCount)
                        if link.find('?') == -1 and \
                                link.find('&') == -1 and \
                                dashCount <= 4 and \
                                link.find("linkedin") == -1 and \
                                link.find(".gov") == -1 :

                            found = found + 1

                            name = item["displayLink"]
                            name = name.replace('www.', '')
                            name = name.replace('.com', '')
                            name = name.replace('.org', '')
                            name = name.replace('.net', '')
                            name = name.replace('.church', '')

                            # looking for existing church with this link
                            selectedChurch = None
                            for church in churches:
                                if church["link"] == link:
                                    selectedChurch = church
                                    break

                            if selectedChurch == None:
                                print("add church: ", name)
                                church = {
                                    "link": link,
                                    "name": name
                                }
                                churches.append(church)

                                print('link: ', item["link"])

                            # save to churches file
                            churchesData["churches"] = churches
                            with open(churches_file_path, "w") as json_file:
                                json.dump(churchesData, json_file, indent=4)

                            # save cities crawled
                            citiesData["cities"] = cities
                            with open(file_path, "w") as json_file:
                                json.dump(citiesData, json_file, indent=4)


                    if found < 7:
                        break

        '''
        
        service = build("customsearch", "v1", developerKey=api_key)

        search_engine_id = "d744719d644574dd7"
        api_version = "v1"
        search_engine = service.cse().liste_(cx=search_enginid, version=api_version)

        query = "zenserp API tutorials"
        search_engine.q = query
        response = search_engine.execute()
        results = response["items"]

        print("results: ", results)
        '''

    def findChurchesUsingNonProfitData(self):

        #ends at https://www.ccsk12.com/

        # https://programmablesearchengine.google.com/controlpanel/overview?cx=d744719d644574dd7
        service = build(
            "customsearch", "v1", developerKey=""
        )

        # get churches
        churchesData = None
        churches_file_path = "churches.json"
        with open(churches_file_path, "r") as file:
            churchesData = json.load(file)

        churches = churchesData["churches"]
        if churches == None:
            churches = []

        # get cities
        file_path = "coloradoFrontRangeCities.json"
        with open(file_path, "r") as file:
            citiesData = json.load(file)

        # cycle through cities looking for church web sites
        cities = citiesData["cities"]

        # get non-profit data
        non_profit_file_path = 'non_profit_co.txt'

        # Read data from file
        with open(non_profit_file_path, 'r') as file:
            nonProfitLines = file.readlines()

            data = []
            frontRangeData = []

            found = 0
            process = False
            for nonProfitLine in nonProfitLines:

                nonProfitLine = nonProfitLine.rstrip('\r\n')
                nonProfitParts = nonProfitLine.split('\t')

                # description of codes  https://www.irs.gov/pub/irs-soi/eo-info.pdf
                ein = nonProfitParts[0]
                churchName = nonProfitParts[1]
                ico = nonProfitParts[2]
                street  = nonProfitParts[3]
                city = nonProfitParts[4]
                state = nonProfitParts[5]
                zip = nonProfitParts[6]
                group = nonProfitParts[7]           # Group Exemption Number, if affiliation is 9 then look for grouping of churches
                subsection = nonProfitParts[8]      # 3 for Charitable, Religious, Educational, Scientific, Literary, Testing for Public Safety, to Foster National or International Amateur Sports Competition, or Prevention of Cruelty to Children or Animals Organizations
                affiliation = nonProfitParts[9]     # Affiliation Code,  9 if under an umbrella group
                classification = nonProfitParts[10] # Classification Code(s), 7000
                ruling = nonProfitParts[11]         # Ruling Date
                deductibility = nonProfitParts[12]  # Deductibility Code
                foundation = nonProfitParts[13]     # Foundation Code, 10 Church,
                activity = nonProfitParts[14]       # 3, 10, 15, 17
                organization = nonProfitParts[15]
                status = nonProfitParts[16]
                taxPeriod = nonProfitParts[17]
                assetCD = nonProfitParts[18]
                incomeCD = nonProfitParts[19]
                filingReqCD = nonProfitParts[20]
                pfFilingReqCD = nonProfitParts[21]
                acctPD = nonProfitParts[22]
                assetAmt = nonProfitParts[23]
                incomeAmt = nonProfitParts[24]
                revenueAmt = nonProfitParts[25]
                nteeCD = nonProfitParts[26]
                sortName = nonProfitParts[27]

                '''
                if street == "620 SOUTHPARK DR":
                    print("************** start processing ****************")
                    process = True
                '''

                process = True

                # looking for existing church with this link
                selectedChurch = None
                for church in churches:
                    '''
                    if church["name"].lower().find(churchName.lower()) >= 0:
                        if "addressInfo" in church and \
                                "zipcode" in church["addressInfo"] and \
                                zip.lower().find(church["addressInfo"]["zipcode"].lower()) >= 0:

                            selectedChurch = church
                        break
                    '''

                    if "ein" not in church and \
                            "addressInfo" in church and "street" in church["addressInfo"] and \
                            street.lower() == church["addressInfo"]["street"].lower() and \
                            "zipcode" in church["addressInfo"] and \
                            zip.lower().find(church["addressInfo"]["zipcode"].lower()) >= 0:
                        selectedChurch = church

                if process and selectedChurch is not None and \
                        foundation == "10" and \
                        classification.startswith("7"):

                    selectedCity = self.getCity(cities, city)
                    if selectedCity is not None:
                        print("church: ", selectedChurch["name"])
                        print("ein: ", ein, "city: ", city, ", name: ", churchName, ", foundation: ", foundation)

                        selectedChurch["ein"] = ein

                        churchesData["churches"] = churches
                        with open(churches_file_path, "w") as json_file:
                            json.dump(churchesData, json_file, indent=4)

                        # get 501c information from https://projects.propublica.org/nonprofits/api/v2/organizations/846023484.json

                        '''
                        time.sleep(3)
                        query = "'" + selectedCity["name"] + " " + street
                        print("query: ", query)
                        res = (
                            service.cse()
                            .list(
                                q=query,
                                cx="318dd8aea896d44fe",
                                start=1
                            )
                            .execute()
                        )
                        #print("--------------------------------------")
                        #print(res)
                        #print("--------------------------------------")

                        if "items" in res:
                            for item in res["items"]:
                                link = item["link"]
                                tag = city.lower() + "-co"
                                if link.find(tag) >= 0:

                                    dashCount = len(link.split("/"))
                                    print("link: ", link, ",  dashCount: ", dashCount)

                                    found = found + 1
                                    if dashCount > 4:


                                        name = item["displayLink"]
                                        name = name.replace('www.', '')
                                        name = name.replace('.com', '')
                                        name = name.replace('.org', '')
                                        name = name.replace('.net', '')
                                        name = name.replace('.church', '')



                                        if selectedChurch == None:
                                            print("add church: ", churchName, ", link: ", item["link"])
                                            selectedChurch = {
                                                "name": churchName
                                            }
                                            churches.append(selectedChurch)

                                            print('link: ', item["link"])

                                        selectedChurch["ein"] = ein
                                        selectedChurch["street"] = street
                                        selectedChurch["city"] = city
                                        selectedChurch["state"] = "Colorado"

                                        if "references" not in selectedChurch:
                                            selectedChurch["references"] = [{
                                                    "site": "faithstreet",
                                                    "type": "search",
                                                    "url": item["link"]
                                                }]

                                        # save to churches file
                                        churchesData["churches"] = churches
                                        with open(churches_file_path, "w") as json_file:
                                            json.dump(churchesData, json_file, indent=4)

                                        # save cities crawled
                                        citiesData["cities"] = cities
                                        with open(file_path, "w") as json_file:
                                            json.dump(citiesData, json_file, indent=4)

                                    break
                        '''

