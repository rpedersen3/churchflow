# -*- coding: utf-8 -*-
import scrapy
from scrapy import Selector
import time


from scrapy.http import HtmlResponse
from scrapy.selector import Selector
from bs4 import BeautifulSoup
import re
from quotesbot.profileextractor import ProfileExtractor
from quotesbot.profilecheck import ProfileCheck
from quotesbot.groupcheck import GroupCheck
from quotesbot.churchfinder import ChurchFinder
from quotesbot.photo import Photo
from quotesbot.graphconvert import GraphConvert

import json
from urllib.parse import urlparse
from lxml import etree
import spacy
import pandas as pd
import requests

import http.client, urllib.parse
import json

from datetime import datetime

from googleapiclient.discovery import build

from scrapy_splash import SplashRequest


import json
import base64
from io import BytesIO
from PIL import Image


import pathlib
import textwrap

import os
from openai import AzureOpenAI
from azure.identity import DefaultAzureCredential

import google.generativeai as genai

import locationtagger


nlp = spacy.load("en_core_web_sm")
pd.set_option("display.max_rows", 200)

churches_file_path = "churches.json"
with open(churches_file_path, "r") as file:
    churchesData = json.load(file)
churches = churchesData["churches"]

class DivCount:
    def __init__(self, div, level, className, count):
        self.div = div
        self.level = level
        self.className = className
        self.count = count

class ChurchCrawler(scrapy.Spider):
    name = "crawler"


    def checkIfNeedsProcessing(currentChurch, processor, url):

        if "processed" not in currentChurch:
            currentChurch["processed"] = {}

        if processor not in currentChurch["processed"]:
            currentChurch["processed"][processor] = []

        needsToBeProcessed = True
        for processed in currentChurch["processed"][processor]:
            if processed["page"] == url:
                if "datetime" in processed:

                    datetimeStr = processed["datetime"]
                    dt = datetime.strptime(datetimeStr, "%Y-%m-%d %H:%M:%S.%f")
                    if dt.date() >= datetime.today().date():
                        needsToBeProcessed = False

        return needsToBeProcessed



    converter = GraphConvert()
    g2 = converter.setupRDFFile()
    converter.addCities(g2)
    converter.saveRDFFile(g2)


    #crawl church sites

    startURLs = []

    converter = GraphConvert()
    g2 = converter.setupRDFFile()

    i = 0
    foundlink = True
    for church in churches:

        print("...... church: ", church["name"])
        converter.addChurch(church, g2)

        #if "pages" not in church:
        link = None
        if "link" in church:
            link = church["link"]

        if link is None and "websiteUri" in church:
            link = church["websiteUri"]

        if link is not None:

            if link == 'https://www.ststephensaurora.org/':
                foundlink = True

            if foundlink:

                #processor = "extract-location-information-from-webpage"
                processor = "extract-chms-information-from-webpage"
                needsToBeProcessed = checkIfNeedsProcessing(church, processor, link)

                if needsToBeProcessed:
                    #if "addressInfo" not in church:
                    startURLs.append(link)

        i = i + 1
        if i > 1000000:
            break

    converter.saveRDFFile(g2)



    '''
    #crawl church center sites

    startURLs = []

    for church in churches:

        chmss = None
        if "chmss" in church:
            chmss = church["chmss"]

            for chms in chmss:
                if chms["type"] == "churchcenter":

                    pageUrl =  chms["pages"][0]["url"]
                    pageUrl = pageUrl.replace("https://", "")
                    churchCenterName = pageUrl.split(".")[0]

                    homeUrl = "https://" + churchCenterName + ".churchcenter.com/home"
                    #if churchCenterName == 'yes2god':
                    startURLs.append(homeUrl)
    '''

    '''
    # crawl church staff pages
    startURLs = []

    foundFirstUrl = False
    firstUrl = "https://www.pinewood.church/ourteam"
    i = 1
    for currentChurch in churches:
        #if "pages" in currentChurch and "contacts" not in currentChurch:
        if "pages" in currentChurch:
            for page in currentChurch["pages"][:3]:

                if "url" in page and "type" in page:
                    url = page["url"]
                    typ = page["type"]

                    if typ == "staff" and url.find(".pdf") == -1:

                        if url.find('staff') >= 0 or \
                                url.find('about') >= 0 or \
                                url.find('leader') >= 0 or \
                                url.find('contact') >= 0 or \
                                url.find('team') >= 0 or \
                                url.find('leader') >= 0 or \
                                url.find('who-we-are') >= 0 or \
                                url.find('pastor') >= 0:

                            print('**************** process page: ', url)

                            if url == firstUrl:
                                foundFirstUrl = True

                            if foundFirstUrl and i > 0:
                                startURLs.append(url)
                                print('urls: ', str(url))

        if i > 5000000:
            break

        i = i + 1
    '''


    '''
    # crawl church reference sites
    startURLs = []

    i = 1
    for church in churches:
        if "references" in church:
            references = church["references"]
            for reference in references:

                if i > 0:
                    site = reference["site"]
                    url = reference["url"]

                    if site == "faithstreet":
                        startURLs.append(url)
                        print('urls: ', str(url))

                if i > 100:
                    break

            i = i + 1

    '''


    #crawl specific url
    startURLs = [
        #"https://calvarybible.com"
        "https://www.thehillsdenver.com/"
        #"https://woodmenvalley.org"
        #"https://missionhills.org/"
        #"https://www.greeleymosaic.com/who-we-are"
        #"https://www.kog-arvada.org/staff"
        #"https://rimrockchurch.org/contact-us"
        #"https://www.stjohnsbreck.org/parish-leadership"
        #"https://emmausanglican.org"
        #"https://avivadenver.org/"
        #"https://yourawakening.org/leadership"
        #"https://bethelmennonite.org/about/"
        #"https://www.cmpc.church/about-us"
        #"https://christchurchcc.org/our-staff-and-leadership"
        #"https://cclongmont.com/church-staff"
        #"https://www.crosscrownchurch.org/our-pastors"
        #"https://www.dwelldenver.org/our-leaders"
        #"https://firstbaptistlafayette.org/team/"
        #"https://www.gracemountainco.org/who-our-leaders-are"
        #"https://hotschurch.org/our-leadership/"
        #"https://hillsidedenver.org/leadership"
        #"https://hopechurchdenver.org/staff/"
        #"https://www.journeyoflongmont.org/staff"
        #"https://kogaz.org/about/our-team/"
        #"https://lifeicm.org/who-we-are"
        #"https://www.littletonsdachurch.org/about-us/leadership/"
        #"https://livinghopecov.com/leadership"
        #"https://www.lpumc.org/leadership/"
        #"https://www.newhopeaurora.org/about-us"
        #"https://newspringcos.org/team"
        #"https://www.odmdenver.org/meet-team"
        #"https://www.peacecolorado.com/our-pastor"
        #"https://reclamationdenver.com/about"
        #"https://sgcco.org/about/leadership/"
        #"https://www.stphilip-co.org/meet-the-staff/"
        #"https://www.pwclc.org/meet-the-staff/"
        #"https://southeast-church.org/about-us/leadership"
        #"https://gccdenver.org/leadership" # boundary issues,  name before picture and switching with boundaries
        #"https://www.agapeoutpost.org"
        #"https://www.fcucc.org/about/our-team"
        #"https://www.foccs.net/about-foc/our-staff/"
        #"https://monumenthillchurch.org/our-team/"
        #"https://www.blackforestcommunitychurch.org/about-us#ministryteam"
        #"https://www.v7pc.org/staff"
        #"https://www.towercommunity.church/who-we-are/"
        #"https://www.ziontemplechurch.org/aboutus"
        #"https://www.agapeoutpost.org/about"
        #"https://newdenver.org/about/"
        #"https://www.valleyfellowship.church/leadership"
        #"https://www.ziontemplechurch.org/aboutus"
        #"https://www.ststephensaurora.org/clergy-staff"
        #"https://www.agapeoutpost.org/about"
        #"https://www.valleylifefraser.org/about-us"
        #"https://www.resiliencechurch.org/our-team"
        #"https://www.fellowshipdenver.org/leadership"
        #"https://www.fellowshipdenver.org/leadership/" # blocked 404 error
        #"https://www.windsorca.org/faculty-and-staff"
        #"https://mcleanbible.org/montgomery-county/leadership/"
        #"https://mynorthlandchurch.org/about/our-team"
        #"https://pikespeakchristianchurch.com/about/"
        #"https://www.thechurchatwoodmoor.com/staff/"
        #"https://www.accncosprings.com/"
        #"https://www.calvary-umc.org/"
        #"https://www.christthekingdenver.org/"
        #"https://calvaryco.church/staff/"
        #"https://www.christchurchdenver.org/staff/"
        #"https://southeast-church.org/about-us/leadership/"
        #"https://nowfaithdenver.com/about-now-faith/leadership/"
        #"https://www.westyrpc.org/our-leadership/"
        #"https://www.redemptioncitychurch.com/about-us/"
        #"https://crossingchurch.org/staff/"
        #"https://www.crossroadsdenver.org/our-team"
        #"https://flccs.net/about-us/staff/"
        #"https://www.flatironschurch.com/leadership/"
        #"https://www.cccgreeley.org/staff-directory/"
        #"https://victory.com/team-pastors/"
        #"https://calvarybible.com/staff/"
        #"https://www.missionhills.org/im-new/staff-elders/"
        #"https://www.missionhills.org/"
        #"https://christianservices.org/",
        #"https://christianservices.org/contact-us/"
    ]



    def checkCommonDiv(self, el1, el2):
        s1 = str(el1)
        s2 = str(el2)

        if (s1 == s2):
            return True
        return False
    def commonDivCount(self, el1, el2):

        ancestors1 = el1.xpath('ancestor::div')
        ancestors2 = el2.xpath('ancestor::div')

        # print('look for common div 1: ', ancestors1)
        # print('look for common div 2: ', ancestors2)

        common_ancestor_div = None
        count = 1
        for ancestor1 in ancestors1[::-1]:
            s1 = str(ancestor1)
            # print('look for common div 1: ', s1)
            for ancestor2 in ancestors2[::-1]:
                s2 = str(ancestor2)
                # print('look for common div 2: ', s2)
                if s1 == s2:
                    common_ancestor_div = ancestor1
                    break
            if common_ancestor_div:
                break

            count = count + 1

        cnt = 0
        if common_ancestor_div != None:
            cnt = len(ancestors1) - count

        return cnt

    def commonDiv(self, el1, el2):

        ancestors1 = el1.xpath('ancestor::div')
        ancestors2 = el2.xpath('ancestor::div')

        # print('look for common div 1: ', ancestors1)
        # print('look for common div 2: ', ancestors2)

        common_ancestor_div = None
        common_ancestor_count = None
        common_ancestor_class = None

        count = 1
        for ancestor1 in ancestors1[::-1]:
            s1 = str(ancestor1)
            # print('look for common div 1: ', s1)
            previousClassName = ""
            for ancestor2 in ancestors2[::-1]:
                s2 = str(ancestor2)
                # print('look for common div 2: ', s2)

                if s1 == s2:
                    #print('s1: ', s1)
                    print('class ', previousClassName.split()[0])
                    common_ancestor_div = ancestor1
                    common_ancestor_class = previousClassName.split()[0]
                    break

                previousClassName = ancestor2.attrib.get("class", "")
            if common_ancestor_div:
                break

            count = count + 1

        cnt = 0
        if common_ancestor_div != None:
            common_ancestor_count = len(ancestors1) - count
            #common_ancestor_class = common_ancestor_div.xpath('//div/@class')

        print('classname: ', common_ancestor_class)
        return common_ancestor_div, common_ancestor_count, common_ancestor_class


    def getBoundingDiv(self, els):
        print("look for lowest common div")
        lastEl = None
        divCounts = []
        for el1 in els[:5]:
            if lastEl != None:
                cDiv, cDivLevel, cClassName = self.commonDiv(el1, lastEl)
                #cDivLevel = self.commonDivCount(el1, lastEl)

                divCount = DivCount(cDiv, cDivLevel, cClassName, 1)
                matching_items = [item for item in divCounts if item.level == cDivLevel and item.className == cClassName]
                if (len(matching_items) == 0):
                    divCounts.append(divCount)
                else:
                    matching_items[0].count = matching_items[0].count + 1

            lastEl = el1

        sortedDivCounts = sorted(divCounts, reverse=True,  key=lambda x: x.count)
        bestDivLevel = sortedDivCounts[0].level
        bestClassName = sortedDivCounts[0].className
        bestDiv = sortedDivCounts[0].div

        print("lowest: ", bestDivLevel)
        return bestDiv, bestClassName





    def replace_multiple_spaces(self, text):
        # Replace multiple spaces with just one space
        cleaned_text = re.sub(r'\s+', ' ', text)
        return cleaned_text

    def saveChurches(self):

        # save to churches file
        churchesData["churches"] = churches
        with open(churches_file_path, "w") as json_file:
            json.dump(churchesData, json_file, indent=4)


    def getPage(self, pages, type, url):

        for page in pages:
            if page["type"] == type and page["url"] == url:
                return page

        return None

    def count_numbers(self, input_string):
        count = 0
        for char in input_string:
            if char.isdigit():
                count += 1
        return count

    def split_on_chars(self, input_string, split_chars):
        pattern = '|'.join(re.escape(char) for char in split_chars)
        return re.split(pattern, input_string)

    def detectName(self, response):
        titles = response.xpath("//title/text()").extract()
        if len(titles) > 0:

            title = titles[0]

            split_chars = ["-", "|"]
            parts = self.split_on_chars(title, split_chars)
            for part in parts:

                #print("part: ", part)
                doc = nlp(part)
                for ent in doc.ents:
                    #print("label: ", ent.label_, ", text: ", ent.text)
                    if ent.label_ == "ORG":
                        name = ent.text
                        return name


        return None

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

    def updateChurchWithGoogleResults(self, currentChurch, data):

        if "id" in data:
            currentChurch["googlePlaceId"] = data["id"]
            print("google place id: ", currentChurch["googlePlaceId"])

        if "displayName" in data:
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
            currentChurch["websiteUri"] = data["websiteUri"]
            print("google websiteUri: ", data["websiteUri"])

        if "nationalPhoneNumber" in data:
            currentChurch["nationalPhoneNumber"] = data["nationalPhoneNumber"]
            print("google nationalPhoneNumber: ", data["nationalPhoneNumber"])

        if "businessStatus" in data:
            currentChurch["businessStatus"] = data["businessStatus"]
            print("google businessStatus: ", data["businessStatus"])

    def getChurchProfileUsingGooglePlaces(self, currentChurch, isHomePage):

        # needs to be home page url
        if isHomePage == False:
            return

        # we use url to search google api
        if "link" not in currentChurch:
            return

        # already called google api
        if "addressInfo" in currentChurch:
            return


        url = currentChurch["link"]
        url = url.replace("https://", "")

        #https://developers.google.com/maps/documentation/places/web-service/text-search?apix_params=%7B%22fields%22%3A%22*%22%2C%22resource%22%3A%7B%22textQuery%22%3A%22calvary-umc.org%22%7D%7D#try-it
        # get google api usage
        # https://console.cloud.google.com/google/maps-apis/quotas?hl=en&project=my-project-1712412027646

        api_key = 'abcdef'
        endpoint = 'https://places.googleapis.com/v1/places:searchText' + "?fields=*&key=" + api_key
        payload = {
            "textQuery": url
        }
        if api_key == '':
            print("api key is not set for getAddressInfoUsingGooglePlaces")
            return

        time.sleep(1)


        response = requests.post(url=endpoint, json=payload)
        data = response.json()

        #print("************* json returned: ", data)

        if "places" in data:
            places = data["places"]
            if len(places) > 0:
                place = places[0]

                self.updateChurchWithGoogleResults(currentChurch, place)

    def getLeadPastorInfoUsingAzureAI(self, currentChurch):

        subscriptionKey = ''
        host = 'api.bing.microsoft.com'
        #path = '/v7.0/entities'
        path = '/v7.0/search'
        mkt = 'en-US'
        query = 'lead pastor of mission hills church+site:missionhills.org'

        quote = urllib.parse.quote(query)
        print("quote: ", quote)
        params = '?mkt=' + mkt + '&q=' + urllib.parse.quote(query)

        #params = '?mkt=' + mkt + '&q=Lead Pastor of Mission &responseFilter=entities'

        headers = {'Ocp-Apim-Subscription-Key': subscriptionKey}
        conn = http.client.HTTPSConnection(host)
        conn.request("GET", path + params, None, headers)
        response = conn.getresponse()
        result =  response.read()

        print(json.dumps(json.loads(result), indent=4))

        '''

        credential = DefaultAzureCredential()

        #endpoint = "https://docs-test-001.openai.azure.com/"
        endpoint = "https://richcanvas.openai.azure.com/"
        # Set the API type to `azure_ad`
        os.environ["OPENAI_API_TYPE"] = "azure_ad"
        # Set the API_KEY to the token from the Azure credential
        os.environ["OPENAI_API_KEY"] = ""

        client = AzureOpenAI(
            azure_endpoint=endpoint,
            api_key="abcdef",
            api_version="2024-03-01-preview"
        )

        response = client.chat.completions.create(
            #model="gpt-35-turbo",
            model="gpt-4-0125-preview",
            # Model = should match the deployment name you chose for your 0125-Preview model deployment
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": "You are a helpful assistant designed to output JSON."},
                {"role": "user", "content": "Who is the Pastor for Calvary Bible Church Erie Campus"}
            ]
        )
        print(response.choices[0].message.content)
        '''


    def getLeadPastorInfoUsingGoogleGemini(self, currentChurch):

        api_key = ''

        leadPastor = {}
        #if "leadPastor" in currentChurch:
        #    leadPastor = currentChurch["leadPastor"]

        if "name" in currentChurch and "addressInfo" in currentChurch and "city" in currentChurch["addressInfo"]:

            #innerQuery = "pastors from Salt and Light Reformed Presbyterian Church, Longmont, colorado"
            innerQuery = "Pikes Peak Christian Church information including pastors"
            #innerQuery = "from church " + currentChurch["name"] + " in city " + currentChurch["addressInfo"]["city"] + " Colorado and website " + currentChurch["link"]
            query = innerQuery # + " using this JSON schema: \{ \"type\": \"object\", \"properties\": \{ \"fullname\": \{ \"type\": \"string\" \}, \"title\": \{ \"type\": \"string\" \}, \"email\": \{ \"type\": \"string\" \}, \"phone-number\": \{ \"type\": \"string\" \}\}\}"

            print("query: ", query)
            #query = "Lead Pastor from " + currentChurch["name"] + ", " + currentChurch["addressInfo"]["city"] + " using this JSON schema: \{ \"type\": \"object\", \"properties\": \{ \"fullname\": \{ \"type\": \"string\" \}, \"title\": \{ \"type\": \"string\" \}, \"email\": \{ \"type\": \"string\" \}, \"phone-number\": \{ \"type\": \"string\" \}\}\}"
            endpoint = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro-latest:generateContent?key=" + api_key
            #endpoint = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.0-ultra:generateContent?key=" + api_key

            payload = { "contents":[{
                "parts":[{"text": query }] }],
              "generationConfig": {
                "response_mime_type": "application/json",
              } }
            if api_key == '':
                print("api key is not set for getAddressInfoUsingGooglePlaces")
                return

            time.sleep(1)

            response = requests.post(url=endpoint, json=payload)
            data = response.json()

            print("************* json returned: ", data)

            if "candidates" in data:
                for candidate in data["candidates"]:
                    if "content" in candidate:
                        if "parts" in candidate["content"]:
                            for part in candidate["content"]["parts"]:
                                if "text" in part:
                                    text = part["text"]
                                    print('text: ', text)
                                    pastors = json.loads(text)
                                    if (len(pastors) > 0):

                                        pastor = pastors[0]



                                        if "fullname" in pastor:
                                            leadPastor["name"] = pastor["fullname"]
                                        if "title" in pastor:
                                            leadPastor["title"] = pastor["title"]
                                        if "email" in pastor:
                                            leadPastor["email"] = pastor["email"]
                                        if "phone-number" in pastor:
                                            leadPastor["phoneNumber"] = pastor["phone-number"]


                                break
                    break

        currentChurch["leadPastor"] = leadPastor





    def getAddressInfoUsingGooglePlaces(self, address, currentChurch):

        # already called google api
        if "addressInfo" in currentChurch:
            return

        #print("address: ", address)

        api_key = 'abcdef'
        endpoint = 'https://maps.googleapis.com/maps/api/geocode/json'

        if api_key == '':
            print("api key is not set for getAddressInfoUsingGooglePlaces")
            return

        time.sleep(1)

        params = {
            'address': address,
            'key': api_key
        }

        response = requests.get(endpoint, params=params)
        data = response.json()

        #print("************* json returned: ", data)

        if "results" in data:
            results = data["results"]
            if len(results) > 0:
                result = results[0]

                if "place_id" in result:
                    placeId = result["place_id"]
                    #print("place id: ", placeId)

                    endpoint = "https://places.googleapis.com/v1/places/" + placeId + "?fields=*&key=" + api_key
                    response = requests.get(endpoint)
                    data = response.json()


                    print("xxxxxxxxxxxxxxxxxxxxxx new place: ", data)

                    currentChurch["googlePlaceId"] = placeId

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

                    if "addressComponents" in data:
                        self.setAddressInfoWithGoogleAddressComponents(data["addressComponents"], currentChurch)

                    if "websiteUri" in data:
                        currentChurch["websiteUri"] = data["websiteUri"]
                        print("google websiteUri: ", data["websiteUri"])

                    if "nationalPhoneNumber" in data:
                        currentChurch["nationalPhoneNumber"] = data["nationalPhoneNumber"]
                        print("google nationalPhoneNumber: ", data["nationalPhoneNumber"])

                    if "businessStatus" in data:
                        currentChurch["businessStatus"] = data["businessStatus"]
                        print("google businessStatus: ", data["businessStatus"])





    def detectAddress(self, response):

        invisible_chars_regex = r'[\x00-\x1F\x7F-\x9F\r\n]'

        # detect address
        txt = None
        prevTxt = None

        query = "//text()[contains(normalize-space(), ', CO 80')]"
        if len(response.xpath(query)) == 0:
            query = "//text()[contains(normalize-space(), ' CO, 80')]"
            if len(response.xpath(query)) == 0:
                query = "//text()[contains(normalize-space(), ' CO, 81')]"
                if len(response.xpath(query)) == 0:
                    query = "//text()[contains(normalize-space(), ' CO, 81')]"
                    if len(response.xpath(query)) == 0:
                        query = "//text()[contains(normalize-space(), ', CO')]"
                        if len(response.xpath(query)) == 0:
                            query = "//text()[contains(normalize-space(), ' CO, ')]"
                            if len(response.xpath(query)) == 0:
                                return None

        for address in response.xpath(query):
            priorElQuery = query + "/preceding-sibling::text()"
            for prevEl in response.xpath(priorElQuery):
                prevTxt = prevEl.extract().replace(",", "")
                #print("prev :", prevTxt)

            txt = address.extract()
            txt = txt.strip()[:200]
            txt = re.sub(invisible_chars_regex, ' ', txt)
            txt = txt.replace("\n", " ")
            txt = txt.replace("| ", ", ")


            #print('txt 1: ', txt, ", prev: ", prevTxt)


        if txt is not None:

            #print("found address: ", txt)

            split_chars = ["'", "-"]   # ["-", "|", "'", "\""]
            parts = self.split_on_chars(txt, split_chars)

            for part in parts:
                part = re.sub(invisible_chars_regex, '', part)
                if len(part) > 5:
                    # if has city and has numbers and is less than 100 characters
                    part = part[:200]
                    place_entity = locationtagger.find_locations(text=part)
                    if len(place_entity.city_mentions) > 0:
                        numberOfNumbers = self.count_numbers(part)
                        if numberOfNumbers > 0:
                            addStr = part.strip()
                            addStr = addStr.replace("\n", " ")

                            # either starts with some knows letters like P.O.  or numbers
                            if addStr.find("P.O.") >= 0:
                                rtnAddress = addStr
                                return rtnAddress

                            # get part of string starting with number
                            numbers = re.findall(r'\d+', addStr)
                            #print("numbers: ", numbers)
                            if (len(numbers) > 0):
                                #print("numbers: ", numbers[0])
                                offset = addStr.find(numbers[0])
                                rtnAddress = addStr[offset:1000]

                                # make sure it is not just a number
                                if rtnAddress != numbers[0]:
                                    return rtnAddress
                                else:
                                    # add previous section to
                                    if prevTxt is not None:
                                        rtnAddress = prevTxt + ", " + addStr
                                        #print('just number 1 prev section: ', addStr)
                                        return rtnAddress

                                    #print('just number 1: ', addStr)



        return None

    def detectPhone(self, response, parts):

        invisible_chars_regex = r'[\x00-\x1F\x7F-\x9F]'

        for part in parts:

            part = re.sub(invisible_chars_regex, '', part)

            codeFind = "(" + part + ")"
            code = "'" + codeFind + "'"
            path = "//text()[starts-with(normalize-space(), " + code + ")]"
            phoneNumbers = response.xpath(path).extract()
            if len(phoneNumbers) == 0:
                path = "//text()[contains(normalize-space(), " + code + ")]"
                phoneNumbers = response.xpath(path).extract()
            if len(phoneNumbers) > 0 and len(phoneNumbers[0]) < 300:
                phoneNumber = phoneNumbers[0]
                #print("ph1: ", phoneNumber)
                offset = phoneNumber.find(codeFind)
                #print("offset: ", offset)
                if offset >= 0:
                    phoneNumber = phoneNumber[offset:offset+14]
                return phoneNumber

            codeFind = part + "."
            code = "'" + codeFind + "'"
            path = "//text()[starts-with(normalize-space(), " + code + ")]"
            phoneNumbers = response.xpath(path).extract()
            if len(phoneNumbers) == 0:
                path = "//text()[contains(normalize-space(), " + code + ")]"
                phoneNumbers = response.xpath(path).extract()
            if len(phoneNumbers) > 0 and len(phoneNumbers[0]) < 300:
                phoneNumber = phoneNumbers[0]
                offset = phoneNumber.find(codeFind)
                #print("ph2: ", phoneNumber)
                if offset >= 0:
                    phoneNumber = phoneNumber[offset:offset+13]
                return phoneNumber

            codeFind = part + "-"
            code = "'" + codeFind + "'"
            path = "//text()[starts-with(normalize-space(), " + code + ")]"
            phoneNumbers = response.xpath(path).extract()
            if len(phoneNumbers) == 0:
                path = "//text()[contains(normalize-space(), " + code + ")]"
                phoneNumbers = response.xpath(path).extract()
            phoneNumbers = response.xpath(path).extract()
            if len(phoneNumbers) > 0 and len(phoneNumbers[0]) < 300:
                phoneNumber = phoneNumbers[0]
                offset = phoneNumber.find(codeFind)
                #print("ph3: ", phoneNumber)
                if offset >= 0:
                    phoneNumber = phoneNumber[offset:offset+13]
                return phoneNumber

        return None

    def detectEmail(self, response):

        "//a[starts-with(@href, 'mailto')]/text()"
        "//a[starts-with(@href, 'mailto')]/text()"
        "//*[contains(text(), '@')]"
        "//@href[starts-with(., 'mailto:')]"
        emails = response.xpath("//a[starts-with(@href, 'mailto')]/text()").extract()
        if len(emails) > 0:
            #print("email 1:", emails)
            if len(emails[0]) > 5:
                email = emails[0].replace("mailto:", "").strip()
                if len(email) > 0:
                    return email

        emails = response.xpath("//@href[starts-with(., 'mailto:')]").extract()
        if len(emails) > 0:
            #print("email 2:", emails)
            if len(emails[0]) > 5:
                email = emails[0].replace("mailto:", "").strip()
                if len(email) > 0:
                    return email

        return None

    def crawlFaithStreet(self, currentChurch, response):

        print('**************** process page: ', response.url)
        # itemtype="https://schema.org/Church"
        non_visible_pattern = re.compile(
            r'[\t\n\r\f\v]')  # matches tabs, newlines, carriage returns, form feeds, vertical tabs, and whitespace


        churchName = response.xpath("//h1[@itemprop='name']/text()").extract()[0]
        churchName = non_visible_pattern.sub('', churchName)
        print("church name: ", churchName)

        description = response.xpath(
            "//div[@itemprop='description']//p/text()").extract()[0]
        description = non_visible_pattern.sub('', description)
        print("church description: ", description)

        # https://schema.org/PostalAddress
        streetAddress = response.xpath("//span[@itemprop='streetAddress']/text()").extract()[0]
        print("church streetAddress: ", streetAddress)

        addressLocality = response.xpath("//span[@itemprop='addressLocality']/text()").extract()[0]
        print("church addressLocality: ", addressLocality)

        addressRegion = response.xpath("//span[@itemprop='addressRegion']/text()").extract()[0]
        print("church addressRegion: ", addressRegion)

        postalCode = response.xpath("//span[@itemprop='postalCode']/text()").extract()[0]
        print("church postalCode: ", postalCode)

        latitude = response.xpath("//meta[@itemprop='latitude']/@content").extract()[0]
        print("church latitude: ", latitude)

        longitude = response.xpath("//meta[@itemprop='longitude']/@content").extract()[0]
        print("church longitude: ", longitude)

        vibes = response.xpath("//dt[text()='Vibe']/following-sibling::dd//a/text()").extract()
        vibesStr = ""
        for vibe in vibes:
            if vibesStr == "":
                vibesStr = vibesStr + vibe
            else:
                vibesStr = vibesStr + ", " + vibe
        print("church vibe: ", vibesStr)

        programs = response.xpath("//dt[text()='Programs']/following-sibling::dd//a/text()").extract()
        programsStr = ""
        for program in programs:
            if programsStr == "":
                programsStr = programsStr + program
            else:
                programsStr = programsStr + ", " + program
        print("church programs: ", programsStr)

        musics = response.xpath("//dt[text()='Music']/following-sibling::dd//a/text()").extract()
        musicStr = ""
        for music in musics:
            if musicStr == "":
                musicStr = musicStr + music
            else:
                musicStr = musicStr + ", " + music
        print("church music: ", musicStr)

        denominations = response.xpath("//dt[text()='Denomination']/following-sibling::dd//a/text()").extract()
        denominationsStr = ""
        for denomination in denominations:
            if denominationsStr == "":
                denominationsStr = denominationsStr + denomination
            else:
                denominationsStr = denominationsStr + ", " + denomination
        print("church denomination: ", denominationsStr)

        size = ""
        sizes = response.xpath("//dt[text()='Size']/following-sibling::dd/text()").extract()
        if len(sizes) > 0:
            size = sizes[0]
        print("church size: ", size)

        languages = response.xpath("//dt[text()='Language']/following-sibling::dd//a/text()").extract()
        languagesStr = ""
        for language in languages:
            if languagesStr == "":
                languagesStr = languagesStr + language
            else:
                languagesStr = languagesStr + ", " + language
        print("church language: ", languagesStr)



        founded = ""
        foundeds = response.xpath("//dt[text()='Founded']/following-sibling::dd/text()").extract()
        if len(foundeds) > 0:
            founded = foundeds[0]
        print("church founded: ", founded)


        siteUrl = ""
        url_href = response.xpath("//div[contains(@class, 'church__description')]//a[@class='text-link' and @target='_blank']/@href").extract()
        if url_href is not None and len(url_href) > 0:
            siteUrl = url_href[0]
            print('church site href: ', siteUrl)

        phone = ""
        phone_href = response.xpath(
            "//div[contains(@class, 'church__description')]//a[@class='text-link' and not(@target='_blank')]/@href").extract()
        if phone_href is not None and len(phone_href) > 0:
            phone = phone_href[0].replace("tel:", "")
            print('church phone href: ', phone)

        currentChurch["name"] = churchName
        if "description" not in currentChurch:
            currentChurch["description"] = description
        if "street" not in currentChurch:
            currentChurch["street"] = streetAddress
        if "city" not in currentChurch:
            currentChurch["city"] = addressLocality
        if "state" not in currentChurch:
            currentChurch["state"] = addressRegion
        if "zip" not in currentChurch:
            currentChurch["zip"] = postalCode
        if "latitude" not in currentChurch:
            currentChurch["latitude"] = latitude
        if "longitude" not in currentChurch:
            currentChurch["longitude"] = longitude

        currentChurch["vibe"] = vibesStr
        currentChurch["programs"] = programsStr
        currentChurch["music"] = musicStr
        currentChurch["denomination"] = denominationsStr
        currentChurch["size"] = size
        currentChurch["language"] = languagesStr
        currentChurch["founded"] = founded

        if "link" not in currentChurch:
            currentChurch["link"] = siteUrl
        if "phone" not in currentChurch:
            currentChurch["phone"] = phone

        self.saveChurches()


    def addChurchSearchTerm(self, currentChurch, searchTerm):

        link = None
        if "link" in currentChurch:
            link = currentChurch["link"]
        elif "websiteUri" in currentChurch:
            link = currentChurch["websiteUri"]

        pages = []

        chmss = []
        if "chmss" in currentChurch:
            chmss = currentChurch["chmss"]
        else:
            currentChurch["chmss"] = chmss

        pages = []
        currentChms = None
        for chms in chmss:
            if chms["type"] == searchTerm:
                currentChms = chms
                if "pages" in currentChms:
                    pages = currentChms["pages"]

                break



        print(' query: ', link, ", for search term: ", searchTerm)
        if link is not None:

            processor = "extract-" + searchTerm + "-from-site"
            needsToBeProcessed = self.checkIfNeedsProcessing(currentChurch, processor, link)

            print("needs: ", needsToBeProcessed)

            if needsToBeProcessed:

                if link != "" and link.find("facebook") == -1:

                    api_key = "abcdef"
                    service = build(
                        "customsearch", "v1", developerKey=api_key
                    )

                    parsed_url = urlparse(link)
                    domain = parsed_url.netloc.replace("www.", "")

                    time.sleep(0.2)

                    query = '"' + searchTerm + '"'
                    res = (
                        service.cse()
                        .list(
                            q=query,
                            cx="d744719d644574dd7",
                            siteSearch=domain,
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

                            foundPage = False
                            for page in pages:
                                if page["type"] == searchTerm and page["url"] == link:
                                    foundPage = True
                                    break

                            if foundPage == False:
                                page = {
                                    "type": searchTerm,
                                    "url": link
                                }
                                print("************************ add page: ", link, ', search term: ', searchTerm)
                                pages.append(page)

                            break

                # if no pages then remove chms splash from list
                if len(pages) > 0:

                    if currentChms is None:

                        currentChms = {
                            "type": searchTerm
                        }
                        currentChms["pages"] = pages
                        currentChurch["chmss"].append(currentChms)

                needsToBeProcessed = self.markAsProcessed(currentChurch, processor, link)

            self.saveChurches()

    def addChurchStaffPages(self, currentChurch):

        link = None
        if "link" in currentChurch:
            link = currentChurch["link"]
        elif "websiteUri" in currentChurch:
            link = currentChurch["websiteUri"]

        #if link != "https://calvarycherrycreek.org/":
        #    return

        print(' process link: ', link)
        if link is not None:

            if link.startswith("http://"):
                link = link.replace("http://", "https://")

                currentChurch["link"] = link
                currentChurch["websiteUri"] = link
                self.saveChurches()


            processor = "extract-staff-pages-from-webpage"
            needsToBeProcessed = self.checkIfNeedsProcessing(currentChurch, processor, link)

            print("needs: ", needsToBeProcessed)

            if needsToBeProcessed:

                print("process: ", link)
                if link != "" and link.find("facebook") == -1:


                    pages = []
                    if "pages" in currentChurch:
                        pages = currentChurch["pages"]

                    if len(pages) == 0:

                        time.sleep(1)
                        api_key = "abcdefg"
                        service = build(
                            "customsearch", "v1", developerKey=api_key
                        )

                        parsed_url = urlparse(link)
                        domain = parsed_url.netloc.replace("www.", "")

                        names = "pastor", "elder"; #, "deacon", "minister"

                        for name in names:

                            print("query for: ", name)
                            time.sleep(0.5)

                            query = name
                            res = (
                                service.cse()
                                .list(
                                    q=query,
                                    cx="d744719d644574dd7",
                                    siteSearch=domain,
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

                                    # check for lots of down pages
                                    count = link.count("/")
                                    if count < 6:

                                        # check for name part
                                        if link.find('staff') >= 0 or \
                                                link.find('about') >= 0 or \
                                                link.find('leader') >= 0 or \
                                                link.find('contact') >= 0 or \
                                                link.find('team') >= 0 or \
                                                link.find('leader') >= 0 or \
                                                link.find('who-we-are') >= 0 or \
                                                link.find('pastor') >= 0:


                                            page = self.getPage(pages, "staff", link)
                                            if page is None:
                                                page = {
                                                    "type": "staff",
                                                    "url": link
                                                }
                                                pages.append(page)

                            if len(pages) > 0:
                                print("found pages: ", pages)
                                currentChurch["pages"] = pages

                                break

                    needsToBeProcessed = self.markAsProcessed(currentChurch, processor, link)
                self.saveChurches()


    def addChurchCenterInfo(self, currentChurch, response):

        name = None
        if "name" in currentChurch:
            print("--------------------------")
            print("name: ", currentChurch["name"])
            name = currentChurch["name"]

        link = None
        if "link" in currentChurch:
            link = currentChurch["link"]
        elif "websiteUri" in currentChurch:
            link = currentChurch["websiteUri"]

        if link is not None and name is not None:
            props = response.xpath('//div/@data-react-props').extract()
            print("props: ", props)

            churchCenter = None
            for chms in currentChurch["chmss"]:
                if chms["type"] == "churchcenter":
                    churchCenter = chms
                    break




            if len(props) > 0:
                js = json.loads(props[0])

                if "home" in js and "navigation_items" in js["home"]:
                    items = js["home"]["navigation_items"]
                    for item in items:
                        if "path" in item:
                            print("path: ", item["path"])

                            foundPage = False
                            href = response.url.replace("/home", item["path"])
                            churchCenterPage = {
                                "url": href,
                                "type": "churchcenter"
                            }
                            for page in churchCenter["pages"]:
                                if page["url"] == href:
                                    foundPage = True
                                    churchCenterPage = page
                                    break

                            if foundPage == False:
                                churchCenter["pages"].append(churchCenterPage)



                if "layout" in js:
                    layout = js["layout"]
                    if "organization_name" in layout:
                        churchCenter["name"] = layout["organization_name"]
                        print("organization_name: ", layout["organization_name"])
                    if "organization_contact_email" in layout:
                        churchCenter["email"] = layout["organization_contact_email"]
                        print("organization_contact_email: ", layout["organization_contact_email"])
                    if "organization_contact_phone" in layout:
                        churchCenter["phone"] = layout["organization_contact_phone"]
                        print("organization_contact_phone: ", layout["organization_contact_phone"])

            # needsToBeProcessed = self.markAsProcessed(currentChurch, processor, link)
            self.saveChurches()



    def addSchemaInfo(self, currentChurch, response):

        datas = response.xpath("//script[@type='application/ld+json']/text()").extract()
        for data in datas:
            jsonData = json.loads(data)
            if "@type" in jsonData:

                type = jsonData["@type"]


                # add page to list
                schemaTypes = []
                if "schemaTypes" in currentChurch:
                    schemaTypes = currentChurch["schemaTypes"]

                found = False
                for schemaType in schemaTypes:
                    if schemaType == type:
                        found = True
                        break

                if found == False:
                    schemaTypes.append(type)

                currentChurch["schemaTypes"] = schemaTypes



    def addChmsInfo(self, currentChurch, response, type, path, term):

        name = None
        if "name" in currentChurch:
            #print("--------------------------")
            #print("name: ", currentChurch["name"])
            name = currentChurch["name"]



        link = None
        if "link" in currentChurch:
            link = currentChurch["link"]
        elif "websiteUri" in currentChurch:
            link = currentChurch["websiteUri"]

        if link is not None and name is not None:
            dataTypes = response.xpath(path).extract()
            for dataType in dataTypes:
                if dataType.find(term) >= 0:
                    print("found: ", type, ", link: ", link)

                    # add page to list
                    chmss = []
                    if "chmss" in currentChurch:
                        chmss = currentChurch["chmss"]

                    currentCms = {
                        "name": name,
                        "type": type
                    }

                    found = False
                    for chms in chmss:
                        if chms["type"] == type:
                            found = True
                            currentCms = chms
                            break

                    if found == False:
                        chmss.append(currentCms)

                    # set page in pages
                    currentPages = []
                    if "pages" in currentPages:
                        currentPages = currentCms["pages"]

                    foundPage = False
                    currentPage = {
                        "url": link,
                        "type": type
                    }
                    for page in currentPages:
                        if page["url"] == link:
                            foundPage = True
                            currentPage = page
                            break

                    if foundPage == False:
                        currentPages.append(currentPage)

                    currentCms["pages"] = currentPages
                    currentChurch["chmss"] = chmss






            #needsToBeProcessed = self.markAsProcessed(currentChurch, processor, link)

    def addChurchCenterChmsInfo(self, currentChurch, processor, response):

        name = None
        if "name" in currentChurch:
            print("--------------------------")
            print("name: ", currentChurch["name"])
            name = currentChurch["name"]



        link = None
        if "link" in currentChurch:
            link = currentChurch["link"]
        elif "websiteUri" in currentChurch:
            link = currentChurch["websiteUri"]

        if link is not None and name is not None:
            hrefs = response.xpath('//a/@href').extract()
            for href in hrefs:
                if href.find("churchcenter.com") >= 0:

                    chmss = []
                    if "chmss" in currentChurch:
                        chmss = currentChurch["chmss"]

                    churchCenter = {
                        "name": name,
                        "type": "churchcenter"
                    }

                    found = False
                    for chms in chmss:
                        if chms["type"] == "churchcenter":
                            found = True
                            churchCenter = chms
                            break

                    if found == False:
                        chmss.append(churchCenter)


                    # set page in pages
                    churchCenterPages = []
                    if "pages" in churchCenter:
                        churchCenterPages = churchCenter["pages"]


                    foundPage = False
                    churchCenterPage = {
                        "url": href,
                        "type": "churchcenter"
                    }
                    for page in churchCenterPages:
                        if page["url"] == href:
                            foundPage = True
                            churchCenterPage = page
                            break

                    if foundPage == False:
                        churchCenterPages.append(churchCenterPage)

                    churchCenter["pages"] = churchCenterPages

                    currentChurch["chmss"] = chmss

                    print("found church center link: ", link)

            #needsToBeProcessed = self.markAsProcessed(currentChurch, processor, link)
            self.saveChurches()

    def searchForChurchLeadPastorInfo(self, currentChurch):



        # and "leadPastor" not in currentChurch
        if "name" in currentChurch and "addressInfo" in currentChurch:
            print("search for lead pastor at: ", currentChurch["name"])
            self.getLeadPastorInfoUsingGoogleGemini(currentChurch)
            #self.saveChurches()



    def searchForChurchProfileInfo(self, currentChurch):

        if "address" not in currentChurch and "street" in currentChurch and "city" in currentChurch:
            address = currentChurch["street"] + " " + currentChurch["city"] + ", Colorado"
            self.getAddressInfoUsingGooglePlaces(address, currentChurch)
            currentChurch["address"] = address
            self.saveChurches()


    def searchForSiteProfileInfo(self, currentChurch, url, response, isHomePage):

        print('**************** process page: ', url)

        # church name
        # website link
        # phone number
        # address (street, city, state, zipcode)
        # social links,  facebook, instagram, youtube, flickr

        if "addressInfo" in currentChurch:
            return

        if url.find(".pdf") >= 0:
            return

        foundUrlTag = False
        if isHomePage or url.find("contact") >= 0:
            foundUrlTag = True

        if foundUrlTag:

            self.getChurchProfileUsingGooglePlaces(currentChurch, isHomePage)

            if response is not None:
                try:
                    # detect phone number
                    phoneNumber = self.detectPhone(response, ["303", "720", "719"])
                    if phoneNumber is not None and "phone" not in currentChurch:
                        print('phone: ', phoneNumber)
                        currentChurch["phone"] = phoneNumber

                    # detect address
                    name = self.detectName(response)
                    if name is not None and "name" not in currentChurch:
                        print("name: ", name)
                        currentChurch["name"] = name

                    # detect email address
                    email = self.detectEmail(response)
                    if email is not None and "email" not in currentChurch:
                        print("email: ", email)
                        currentChurch["email"] = email

                    # detect address
                    address = self.detectAddress(response)
                    if address is not None and "address" not in currentChurch:
                        print("address: ", address)
                        currentChurch["address"] = address

                    if "address" in currentChurch:
                        address = currentChurch["address"]
                        self.getAddressInfoUsingGooglePlaces(address, currentChurch)

                except Exception as e:
                    print("error getting address for ", response.url, ", error: ", e)



    def searchForGroups(self, response):

        groupCheck = GroupCheck()




        if response.url.find('group') != -1:
            print('**************** search group page: ', response.url)

            groupElements = []

            path = response.xpath('//h1 | //h2 | //h3 | //h4 | //strong | //p | //span ')
            for el in path:
                # print("--------------- Look for Profile Info -----------------------")

                visible_text = el.xpath('.//text()[normalize-space()]').extract()
                for text in visible_text:
                    #print("check text for group name: ", text)
                    #print("text: ", text[:50])
                    if groupCheck.isGroupName(text):
                        groupElements.append(el)
                        print("group name: ", text)

            if len(groupElements) > 1:
                #print("get bounding div: ", len(groupElements))
                boundingDiv, boundingClassName = self.getBoundingDiv(groupElements)
                html = str(boundingDiv)
                print('div class name: ', boundingClassName)
                groupCheck.lookForGroupNames(html, boundingClassName)

    def findCurrentChurch(self, url):

        isHomePage = False
        currentChurch = None
        for church in churches:

            if "link" in church:
                churchParse = urlparse(church["link"])
                churchDomain = churchParse.netloc.replace("www.", "")

                urlParse = urlparse(url)
                urlDomain = urlParse.netloc.replace("www.", "")

                if churchDomain == urlDomain:
                    currentChurch = church

                    #print("path: ", urlParse.path)
                    if urlParse.path == '' or urlParse.path == '/':
                        isHomePage = True

                    break


        return currentChurch, isHomePage

    def findCurrentChurchReference(self, url):
        currentChurch = None
        for church in churches:

            if "references" in church:
                references = church["references"]
                for reference in references:
                    if "url" in reference:
                        if reference["url"] == url:
                            currentChurch = church
                            break

        return currentChurch

    def findCurrentChurchFromChmsPages(self, url):
        url = url.replace("/home", "")
        currentChurch = None
        for church in churches:

            if "chmss" in church:
                chmss = church["chmss"]
                for chms in chmss:
                    if "pages" in chms:
                        pages = chms["pages"]
                        for page in pages:
                            if page["url"].startswith(url):
                                currentChurch = church
                                break

        return currentChurch




    def checkIfNeedsProcessing(self, currentChurch, processor, url):

        if "processed" not in currentChurch:
            currentChurch["processed"] = {}

        if processor not in currentChurch["processed"]:
            currentChurch["processed"][processor] = []

        needsToBeProcessed = True
        for processed in currentChurch["processed"][processor]:
            if processed["page"] == url:
                if "datetime" in processed:

                    datetimeStr = processed["datetime"]
                    dt = datetime.strptime(datetimeStr, "%Y-%m-%d %H:%M:%S.%f")
                    if dt.date() >= datetime.today().date():
                        needsToBeProcessed = False

        return needsToBeProcessed

    def markAsProcessed(self, currentChurch, processor, url):

        processed = {
                    "page": url,
                    "datetime": str(datetime.now())
                }
        currentChurch["processed"][processor].append(processed)



    def start_requests(self):


        print("............ start_requests ..........")



        lua_script_template = """
            function main(splash, args)  
            
                print("url: ", args.url)
                
                splash:on_request(function(request)
                    print("request: ", request.url)

                    if request.url ~= 'PAGE_URL' then
                    
                        local aa, _ = request.url:find("%%")
                        if aa ~= nil then
                            print("............ has % in it: ", request.url)
                            request.abort()
                            return { status = 404, }
                        end
                    
                        local start, _ = request.url:find("%wixpress%")
                        if start == nil then
                            start, _ = request.url:find("%jpg%")
                        end
                        if start == nil then
                            start, _ = request.url:find("%png%")
                        end

                        
                        if start == nil then
                            print("pg: ", request.url)
                            request.abort()
                            return { status = 404, }
                        end
                    end

                    
                end)
                
                print("go to url", args.url)
                splash:go(args.url)
    
                -- custom rendering script logic...

                return splash:html()
            end
            """

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



    def save_image(self, response):

        try:

            # Extract the image name from the URL

            urlValue = response.url.split('/')[-1]
            image_name = urlValue.split('/')[-1]

            destination_folder = ".scrapy/imagefiles"
            os.makedirs(destination_folder, exist_ok=True)
            destination_file_path = os.path.join(destination_folder, os.path.basename(image_name)) + ".png"

            imgdata = base64.b64decode(response.data['png'])
            image = Image.open(BytesIO(imgdata))
            image.save(destination_file_path)

            #print(destination_file_path)
            #print('screenshot done...')

        except:
            print('..')


    def parse(self, response):


        print("response: ", response.url)
        #print("body: ", response.body)


        if response.url.find(".pdf") >= 0 or \
           response.url.find(".zip") >= 0:
                print("pdf or zip file so return")
                return

        profileExtractor = ProfileExtractor()

        churchFinder = ChurchFinder()
        #churchFinder.findChurchesUsingSpreadsheet()
        #churchFinder.findChurchesUsingGooglePlaces()
        #churchFinder.findChurchesUsingNonProfitData()
        #churchFinder.findCityDemographicsFromCensusData()
        #churchFinder.findCityDemographics()
        #churchFinder.findCities()
        #churchFinder.findChurches()
        #churchFinder.findCounties()

        #print("body: ", response.body)





        '''
        # extract contacts from staff web pages
        currentChurch, isHomePage = self.findCurrentChurch(response.url)
        if currentChurch is not None and "name" in currentChurch:

            print("process church: ", currentChurch["name"])

            processor = "extract-profile-contacts-from-webpage"
            needsToBeProcessed = self.checkIfNeedsProcessing(currentChurch, processor, response.url)

            if needsToBeProcessed == True:

                # crawl page and get schema
                schema = profileExtractor.extractProfilesFromWebPage(currentChurch, response, None, None, None, None)
                profileExtractor.extractProfilesUsingSchema(currentChurch, response, schema)

                self.markAsProcessed(currentChurch, processor, response.url)
                self.saveChurches()



                # save images to directory
                lua_script_template = """
                                    function main(splash, args)  

                                          splash.private_mode_enabled = false
                                          splash.images_enabled = true
                                          splash:set_user_agent("Different User Agent")
                                          splash.plugins_enabled = true
                                          splash.html5_media_enabled = true
                                          assert(splash:go(args.url))

                                        print("urla cccccc: ", args.url)
                                          return {
                                            png = splash:png()
                                          }


                                    end
                                    """

                image_urls = response.xpath('//img')

                # Process each image URL
                for el in image_urls:

                    # get image source
                    img_src = None
                    # get photo inside elements
                    if el.xpath('@src').get():
                        img_src = el.xpath('@src').get()

                        # if this is an svg thing like popupbox then set to None
                        if img_src.find("data:image/svg+xml") >= 0:
                            img_src = None

                    if img_src is None and el.xpath('@data-src').get():
                        img_src = el.xpath('@data-src').get()

                        # if this is an svg thing like popupbox then set to None
                        if img_src.find("data:image/svg+xml") >= 0:
                            img_src = None

                    if img_src is None and el.xpath('@style').get():
                        st = el.xpath('@style').get()
                        if st.find("background:url") >= 0:
                            parts = re.findall(r'\((.*?)\)', st)
                            if len(parts) > 0:
                                img_src = parts[0]
                        elif st.find("background-image:url") >= 0:
                            parts = re.findall(r'\((.*?)\)', st)
                            if len(parts) > 0:
                                img_src = parts[0]

                    if el.xpath('@data-src').get():
                        img_src = el.xpath('@data-src | @srcset').get()

                    if el.xpath('@srcset').get():
                        # get highest resolution image if one exists
                        img_src = el.xpath('@srcset').get()
                        imgEls = img_src.split(",")
                        img_src = imgEls[-1].split()[0]

                    if img_src is not None:
                        print("splash request ............. ", img_src)
                        try:
                            lua_script = lua_script_template.replace("PAGE_URL", img_src)
                            yield SplashRequest(img_src, self.save_image, endpoint='execute',
                                                args={
                                                    "render_all": 1,
                                                    "wait": 5,
                                                    "png": 1,
                                                    'lua_source': lua_script
                                                })

                        except Exception as e:
                            print(".")


            else:
                print("processing not needed")



            # self.getLeadPastorInfoUsingAzureAI(currentChurch)
            #self.searchForContacts(currentChurch, response)
            

        '''

        '''
        #crawl reference urls
        print("parse site: ", response.url)
        currentChurch = self.findCurrentChurchReference(response.url)
        if currentChurch == None:
            print("not found church for url: ", response.url)
            return

        if "vibe" not in currentChurch:
            self.crawlFaithStreet(currentChurch, response)

        '''

        '''
        # cycle through churches that don't have links and try to resolve them
        for church in churches:
            self.searchForChurchProfileInfo(church)
        '''


        '''
        # crawl church center urls
        #print("parse site subsplash: ", response.url)
        currentChurch, isHomePage = self.findCurrentChurch(response.url)
        if currentChurch != None and isHomePage == True:
            #self.addChurchSearchTerm(currentChurch, 'pushpay')
            self.addChurchSearchTerm(currentChurch, 'onrealm.org')
            #self.addChurchSearchTerm(currentChurch, 'tithe.ly')
            #self.addChurchSearchTerm(currentChurch, 'ccbchurch')
        '''


        '''
        currentChurch, isHomePage = self.findCurrentChurch(response.url)
        #if currentChurch != None and isHomePage == True:
        if currentChurch != None:
            print("process url: ", response.url)


            self.addChmsInfo(currentChurch, response, 'wordpress', '//style/@id', 'wp-block')
            self.addChmsInfo(currentChurch, response, 'wordpress', '//link/@id', 'wp-block')
            self.addChmsInfo(currentChurch, response, 'wordpress', '//link/@href', 'wp-content')
            self.addChmsInfo(currentChurch, response, 'wordpress', '//meta/@content', 'wp-content')
            self.addChmsInfo(currentChurch, response, 'squarespace', '//link/@href', 'squarespace')
            self.addChmsInfo(currentChurch, response, 'moto', '//link/@id', "moto-website-style")
            self.addChmsInfo(currentChurch, response, 'joomla', '//meta/@content', "Joomla")
            self.addChmsInfo(currentChurch, response, 'clover', '//meta/@content', "clover")
            self.addChmsInfo(currentChurch, response, 'woocommerce', '//link/@id', "woocommerce-layout-css")
            self.addChmsInfo(currentChurch, response, 'wix', '//meta/@content', "Wix")
            self.addChmsInfo(currentChurch, response, 'weebly', '//link/@href', "weebly")


            self.addChmsInfo(currentChurch, response, 'finalweb', '//div/@id', 'finalweb')  # https://www.finalweb.com/
            self.addChmsInfo(currentChurch, response, 'thechurchco', '//link/@id', "thechurchco-theme-css")
            self.addChmsInfo(currentChurch, response, 'churchcenter', '//a/@href', "churchcenter")
            self.addChmsInfo(currentChurch, response, 'churchcenter', '//link/@href', "churchcenter")
            self.addChmsInfo(currentChurch, response, 'rockrms', '//meta/@content', "Rock v")  ## triggering on Rock in the name
            self.addChmsInfo(currentChurch, response, 'breeze', '//a/@href', "breeze")
            self.addChmsInfo(currentChurch, response, 'breeze', '//div/@id', "breeze")
            self.addChmsInfo(currentChurch, response, 'breeze', '//script/@src', "breeze")
            self.addChmsInfo(currentChurch, response, 'ecatholic', '//link/@href', "ecatholic")
            self.addChmsInfo(currentChurch, response, 'ekklesia', '//a/@href', "ekklesia")
            self.addChmsInfo(currentChurch, response, 'ekklesia', '//script/@src', "ekklesia")
            self.addChmsInfo(currentChurch, response, 'pushpay', '//a/@href', "pushpay")
            self.addChmsInfo(currentChurch, response, 'tithely', '//a/@href', "tithe.ly")
            self.addChmsInfo(currentChurch, response, 'givelify', '//a/@href', "givelify")
            self.addChmsInfo(currentChurch, response, 'faithdirect', '//a/@href', "faithdirect")
            self.addChmsInfo(currentChurch, response, 'ccbchurch', '//a/@href', "ccbchurch")
            self.addChmsInfo(currentChurch, response, 'subsplash', '//div/@data-type', 'subsplash_media')
            self.addChmsInfo(currentChurch, response, 'onrealm', '//a/@href', "onrealm.org")
            self.addChmsInfo(currentChurch, response, 'sharefaith', '//a/@href', "sharefaith")
            self.addChmsInfo(currentChurch, response, 'easytithe', '//a/@href', "easytithe")
            self.addChmsInfo(currentChurch, response, 'vancopayments', '//iframe/@src', "myvanco")
            self.addChmsInfo(currentChurch, response, 'vancopayments', '//a/@href', "myvanco")
            self.addChmsInfo(currentChurch, response, 'vancopayments', '//a/@href', "eservicepayments")
            self.addChmsInfo(currentChurch, response, 'subsplash', '//iframe/@src', "subsplash")
            self.addChmsInfo(currentChurch, response, 'subsplash', '//meta/@content', "snappages")
            self.addChmsInfo(currentChurch, response, 'bboxdonation', '//div/@id', "bboxdonation")
            self.addChmsInfo(currentChurch, response, 'paypal', '//a/@href', "paypal")
            self.addChmsInfo(currentChurch, response, 'paypal', '//form/@action', "paypal")
            self.addChmsInfo(currentChurch, response, 'gloo', '//script/text()', "gloo.us")
            self.addChmsInfo(currentChurch, response, 'clover', '//a/@href', "clovergive")

            self.addSchemaInfo(currentChurch, response)

            self.saveChurches()
        else:
            print("not a church url: ", response.url)

        '''

        '''
        # crawl church center urls
        print("parse site chms: ", response.url)
        currentChurch, isHomePage = self.findCurrentChurch(response.url)
        if currentChurch == None or isHomePage == False:
            print("not found church for url: ", response.url)
            return

        processor = "extract-chms-information-from-webpage"
        self.addChurchCenterChmsInfo(currentChurch, processor, response)
        '''

        '''
        print("parse site church center site: ", response.url)
        currentChurch = self.findCurrentChurchFromChmsPages(response.url)
        if currentChurch == None:
            print("not found church for url: ", response.url)
            return

        self.addChurchCenterInfo(currentChurch, response)
        '''

        '''
        # cycle through churches and add staff pages
        print("............  add church staff pages ...............")
        start = False
        for church in churches:

            if "link" in church:
                if church["link"] == "https://calvaryberthoud.com/":
                    start = True

            if start == True:
                self.addChurchStaffPages(church)
        '''

        '''
        # cycle through churches and update lead pastor information
        i = 0
        for church in churches:
            if church["name"] == "Mission Hills Church Littleton Campus":
                self.searchForChurchLeadPastorInfo(church)

                i = i+1
                if i > 1:
                    break
        '''


        '''
        # get google places associated with websites
        for church in churches:
            link = None
            if "link" in church:
                link = church["link"]
            if link is None and "websiteUrl" in church:
                link = church["websiteUrl"]

            if link is not None:

                processor = "extract-location-information-from-webpage"
                needsToBeProcessed = self.checkIfNeedsProcessing(church, processor, link)

                if needsToBeProcessed == True:
                    if "addressInfo" not in church:
                        print("search for site location info")
                        self.searchForSiteProfileInfo(church, link, None, True)

                        needsToBeProcessed = self.markAsProcessed(church, processor, link)
                        self.saveChurches()
        '''

        '''

        # crawl church home page urls for location info
        print("")
        print("parse site urls: ", response.url)
        currentChurch, isHomePage = self.findCurrentChurch(response.url)
        print("done looking")
        if currentChurch is not None and isHomePage:

            processor = "extract-location-information-from-webpage"
            needsToBeProcessed = self.checkIfNeedsProcessing(currentChurch, processor, response.url)

            if needsToBeProcessed == True:
                if "addressInfo" not in currentChurch:
                    print("search for site location info")
                    self.searchForSiteProfileInfo(currentChurch, response.url, response, isHomePage)

                needsToBeProcessed = self.markAsProcessed(currentChurch, processor, response.url)
                self.saveChurches()

        '''

        '''
        #self.searchForGroups(response)
        '''

        '''
        if isHomePage:
            links = response.xpath('//a/@href').extract()
            for link in links:

                #if link.find("https:") == -1 or link.find(response.url) >= 0:
                if link.find(response.url) >= 0 or (link.find("https:") == -1 and link.find("http:") == -1):

                    # Make sure the link is within the same domain to avoid crawling external sites
                    pageLink = link.replace(response.url, "")
                    count = pageLink.count("/")

                    # pageLink.startswith('/') and  \
                    if pageLink != "" and \
                            pageLink != "/" and  \
                            pageLink.find('?') == -1 and \
                            pageLink.find('mailto:') == -1 and \
                            pageLink.find('javascript:') == -1 and \
                            pageLink.find('tel:') == -1 and \
                            pageLink.startswith('#') == False and \
                            count < 4:

                        yield scrapy.Request(response.urljoin(pageLink), callback=self.parse)

        '''

