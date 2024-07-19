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

class FindChurchOrganizations:


    churches_file_path = "churches.json"
    with open(churches_file_path, "r") as file:
        churchesData = json.load(file)
    churches = churchesData["churches"]



    def findChurchOrganizationStructure(self, church, orgChartUrl):

        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service)


        driver.get(orgChartUrl)

        # Wait for the page to load completely
        time.sleep(10)  # Increase this if necessary for your connection

        # Get the page source and parse it with BeautifulSoup
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        driver.quit()

        print("soup: ", soup)
        '''
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

        for tr in soup.find_all('tr', class_="description-item"):
            for td in tr.find_all('td', class_="style-scope"):

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

        '''
