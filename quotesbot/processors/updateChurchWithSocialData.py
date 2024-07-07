import json
import re
import base64
from io import BytesIO
from PIL import Image
import os

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

        #print("soup: ", soup)
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
                print("ticktok: ", linkValue)





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
                    youtubeUrl = href.rstrip("/about").rstrip("/featured").rstrip("/streams").rstrip("/")
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

        return changed