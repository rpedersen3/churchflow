
import os
import json
from googleapiclient.discovery import build
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import time

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
            if (name.find(city["name"]) >= 0):
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
        search_engine = service.cse().list(cx=search_engine_id, version=api_version)

        query = "zenserp API tutorials"
        search_engine.q = query
        response = search_engine.execute()
        results = response["items"]

        print("results: ", results)
        '''

        def findChurchesUsingNonProfitData(self):

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
            non_profit_file_path = 'cities.txt'

            # Read data from file
            with open(non_profit_file_path, 'r') as file:
                nonProfitLines = file.readlines()

                data = []
                frontRangeData = []

                for nonProfitLine in nonProfitLines:
                    nonProfitLine = nonProfitLine.rstrip('\r\n')
                    nonProfitParts = nonProfitLine.split('\t')

                    # description of codes  https://www.irs.gov/pub/irs-soi/eo-info.pdf
                    ein = nonProfitParts[0]
                    name = nonProfitParts[1]
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

                    if foundation == "10":
                        selectedCity = self.getCity(cities, city)
                        if selectedCity is not None:
                            query = "'" + selectedCity["name"] + " " + name + " " + street
                            print("query: ", query)
                            res = (
                                service.cse()
                                .list(
                                    q=query,
                                    cx="d744719d644574dd7",
                                    start=1
                                    # cx="01757666212468239146:omuauf_lfve",
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
                                        link.find(".edu") == -1 and \
                                        link.find(".gov") == -1:

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

                                    break

