import json
import re
import base64
from io import BytesIO
from PIL import Image
import os
import urllib.parse

from quotesbot.utilities.helpers import Helpers

from quotesbot.utilities.profileextractor import ProfileExtractor

from scrapy_splash import SplashRequest

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup


import time
import requests


class UpdateChurchWithSocialData:

    helpers = Helpers()

    # get churches
    churches_file_path = "churches.json"
    with open(churches_file_path, "r") as file:
        churchesData = json.load(file)

    churches = churchesData["churches"]
    if churches == None:
        churches = []


    def appendWebPagesBasedOnSocial(self, church, startURLs):

        if "link" in church and "is-primary" in church and church["is-primary"] == "yes":
            print("add to urls: ", church["link"])
            startURLs.append(church["link"])

            #if "social" in church and "facebookUrl" in church["social"]:
            #    facebookUrl = church["social"]["facebookUrl"]
            #    startURLs.append(facebookUrl)

    def processYoutubeAbout(self, url, social):



        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service)

        url = url + "/about"
        driver.get(url)

        # Wait for the page to load completely
        time.sleep(10)  # Increase this if necessary for your connection


        # Get the page source and parse it with BeautifulSoup
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        driver.quit()

        print("soup: ", soup)
        for link in soup.find_all('span'):
            linkValue = link.get_text()
            previous_span = link.find_previous_sibling('span')
            previous_span_text = previous_span.get_text() if previous_span else None

            if previous_span_text == "Website" and "websiteUrl" not in social:
                social["websiteUrl"] = "https://" + linkValue
                print(previous_span_text)
                print("website: ", linkValue)

            if previous_span_text == "Facebook" and "facebookUrl" not in social:
                social["facebookUrl"] = "https://" + linkValue
                print(previous_span_text)
                print("facebook: ", linkValue)

            if previous_span_text == "Instagram" and "instagramUrl" not in social:
                social["instagramUrl"] = "https://" + linkValue
                print(previous_span_text)
                print("instagram: ", linkValue)

            if previous_span_text == "TikTok" and "tiktokUrl" not in social:
                social["tiktokUrl"] = "https://" + linkValue
                print(previous_span_text)
                print("tiktok: ", linkValue)

            if previous_span_text == "Pinterest" and "pinterestUrl" not in social:
                social["pinterestUrl"] = "https://" + linkValue
                print(previous_span_text)
                print("pinterest: ", linkValue)

        for tr in soup.find_all('tr', class_ ="description-item"):
            for td in tr.find_all('td', class_ ="style-scope"):

                ytIcon = td.find("yt-icon")
                if ytIcon != None:
                    icon = ytIcon.get("icon")

                    nextTd = td.find_next_sibling('td')
                    if nextTd != None and icon != None:

                        youtube = {}
                        if "youtube" in social:
                            youtube = social["youtube"]

                        text = nextTd.get_text().strip("\n")

                        if icon == "language":
                            youtube["url"] = text
                            print("youtube url: ", text)


                        if icon == "person_radar":
                            youtube["subscribers"] = text
                            print("subscribers: ", text)

                        if icon == "my_videos":
                            youtube["videos"] = text
                            print("videos: ", text)

                        if icon == "trending_up":
                            youtube["views"] = text
                            print("views: ", text)

                        if icon == "info_outline":
                            youtube["joined"] = text
                            print("joined: ", text)

                        social["youtube"] = youtube



    def processFacebook(self, url, social):

        print("process facebook .....................")
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service)

        driver.get(url)

        # Wait for the page to load completely
        time.sleep(1)  # Increase this if necessary for your connection

        # Get the page source and parse it with BeautifulSoup
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        driver.quit()

        facebook = {}
        if "facebook" in social:
            facebook = social["facebook"]

        # print("soup: ", soup)
        changed = False
        for span in soup.find_all('span'):
            txt = span.get_text()

            if txt.find("Page") >= 0:
                changed = True
                type = txt.replace("Page \u00b7", "").strip()
                facebook["type"] = type
                print("type: ", type)

            if txt.find("Colorado") >= 0 and txt.find("United States") >= 0:
                changed = True
                address = txt
                facebook["address"] = address
                print("address: ", address)

            if txt.find("(") < txt.find(")") and txt.find(")") < txt.find("-"):
                changed = True
                phoneNumber = txt
                facebook["phoneNumber"] = phoneNumber
                print("phoneNumber: ", phoneNumber)

            pattern = re.compile(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$')
            if pattern.match(txt) is not None:
                changed = True
                email = txt
                facebook["email"] = email
                print("email: ", email)

            if txt.find("Reviews") >= 0:
                "Rating \u00b7 4.9 (328 Reviews)\ufeff"
                changed = True
                reviews = urllib.parse.unquote(txt).replace("\u00b7 ", "").replace("\ufeff", "")
                facebook["reviews"] = reviews
                print("reviews: ", reviews)

        a_tags = soup.find_all('a')
        hrefs = [a.get('href') for a in a_tags if a.get('href') is not None]
        for href in hrefs:
            decoded_string = urllib.parse.unquote(href)[10:]
            # print("href: ", decoded_string)
            offset = decoded_string.find("https://")
            if offset > 0:
                offset = offset + 8
                url = decoded_string[offset:]
                offset = url.find("&h=")
                if offset > 0:
                    changed = True
                    url = url[:offset]

                    print("************* url: ", url)
                    if url.find("instagram") >= 0:
                        facebook["instagramUrl"] = url
                        print("instagramUrl: ", url)
                    elif url.find("youtube") >= 0:
                        facebook["youtubeUrl"] = url
                        print("youtubeUrl: ", url)
                    else:
                        facebook["websiteUrl"] = url
                        print("websiteUrl: ", url)

        for a_tag in a_tags:
            txt = a_tag.get_text()
            if txt.find("likes") >= 0:
                facebook["likes"] = txt
                print('likes: ', txt)
            if txt.find("followers") >= 0:
                facebook["followers"] = txt
                print('followers: ', txt)

        if changed:
            print("facebook updated: ", facebook)
            social["facebook"] = facebook

    '''

    def processFacebook(self, url, response, social):


        # Wait for the page to load completely
        time.sleep(1)  # Increase this if necessary for your connection

        facebook = {}
        if "facebook" in social:
            facebook = social["facebook"]

        print("scan text")
        changed = False
        spans = response.xpath('//span').extract()
        for span in spans:

            txt = span

            if txt.find("Page") >= 0:

                changed = True
                type = txt.replace("Page \u00b7", "").strip()
                facebook["type"] = type
                print("type: ", type)

            if txt.find("Colorado") >= 0 and txt.find("United States") >= 0:
                changed = True
                address = txt
                facebook["address"] = address
                print("address: ", address)

            if txt.find("(") < txt.find(")") and txt.find(")") < txt.find("-"):
                changed = True
                phoneNumber = txt
                facebook["phoneNumber"] = phoneNumber
                print("phoneNumber: ", phoneNumber)

            pattern = re.compile(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$')
            if pattern.match(txt) is not None:
                changed = True
                email = txt
                facebook["email"] = email
                print("email: ", email)


            if txt.find("Reviews") >= 0:
                "Rating \u00b7 4.9 (328 Reviews)\ufeff"
                changed = True
                reviews = urllib.parse.unquote(txt).replace("\u00b7 ", "").replace("\ufeff", "")
                facebook["reviews"] = reviews
                print("reviews: ", reviews)

        hrefs = response.xpath('//a/@href').extract()
        for href in hrefs:
            decoded_string = urllib.parse.unquote(href)[10:]
            #print("href: ", decoded_string)
            offset = decoded_string.find("https://")
            if offset > 0:
                offset = offset + 8
                url = decoded_string[offset:]
                offset = url.find("&h=")
                if offset > 0:
                    changed = True
                    url = url[:offset]

                    print("************* url: ", url)
                    if url.find("instagram") >= 0:
                        facebook["instagramUrl"] = url
                        print("instagramUrl: ", url)
                    elif url.find("youtube") >= 0:
                        facebook["youtubeUrl"] = url
                        print("youtubeUrl: ", url)
                    else:
                        facebook["websiteUrl"] = url
                        print("websiteUrl: ", url)

        aTags = response.xpath('//a').extract()
        for a_tag in aTags:
            txt = a_tag.get_text()
            if txt.find("likes") >= 0:
                facebook["likes"] = txt
                print('likes: ', txt)
            if txt.find("followers") >= 0:
                facebook["followers"] = txt
                print('followers: ', txt)

        if changed:
            print("facebook updated: ", facebook)
            social["facebook"] = facebook
    '''

    def updateChurchWithSocialData(self, church, response):

        changed = False

        # extract contacts from staff web pages

        print("process church: ", church["name"])

        processor = "extract-social-data-from-webpage"
        needsToBeProcessed = self.helpers.checkIfNeedsProcessing(church, processor, response.url)

        if needsToBeProcessed == True:

            changed = True

            social = {}
            if "social" in church:
                social = church["social"]

            if "websiteUrl" not in social:
                social["websiteUrl"] = response.url

            hrefs = response.xpath('//a/@href').extract()
            for href in hrefs:
                print("href: ", href)

                if href.find("facebook.com") >= 0 and "facebookUrl" not in social:
                    social["facebookUrl"] = href.rstrip("/")
                    print("facebook: ", href)
                if href.find("instagram.com") >= 0 and "instagramUrl" not in social:
                    social["instagramUrl"] = href.rstrip("/")
                    print("instagram: ", href)
                if href.find("twitter.com") >= 0 and "twitterUrl" not in social:
                    social["twitterUrl"] = href.rstrip("/")
                    print("twitter: ", href)
                if href.find("youtube.com") >= 0 and "youtubeUrl" not in social:
                    youtubeUrl = href.rstrip("/about").rstrip("/featured").rstrip("/streams").rstrip("/liv").rstrip("/video").rstrip("/")
                    if youtubeUrl.find("?") == -1:
                        social["youtubeUrl"] = youtubeUrl
                        self.processYoutubeAbout(youtubeUrl, social)
                        print("youtube: ", href)
                if href.find("instagram.com") >= 0 and "instagramUrl" not in social:
                    social["instagramUrl"] = href.rstrip("/")
                    print("instagram: ", href)
                if href.find("tiktok.com") >= 0 and "tiktokUrl" not in social:
                    social["tiktokUrl"] = href.rstrip("/")
                    print("tiktok: ", href)
                if href.find("vimeo.com") >= 0 and "vimeoUrl" not in social:
                    social["vimeoUrl"] = href.rstrip("/")
                    print("vimeo: ", href)
                if href.find("mailto:") >= 0 and "email" not in social:
                    social["email"] = href.replace("mailto:", "")
                    print("email: ", href.replace("mailto:", ""))

            church["social"] = social

            self.helpers.markAsProcessed(church, processor, response.url)


        # get data from social pages
        if "social" in church:
            social = church["social"]

            if "youtubeUrl" in social and "youtube" not in social:
                youtubeUrl = social["youtubeUrl"]
                changed = True
                self.processYoutubeAbout(youtubeUrl, social)

            if "facebookUrl" in social and "facebook" not in social:
                facebookUrl = social["facebookUrl"]
                changed = True
                self.processFacebook(facebookUrl, social)


        return changed