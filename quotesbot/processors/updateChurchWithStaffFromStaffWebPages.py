import json
import re
import base64
from io import BytesIO
from PIL import Image
import os

from quotesbot.utilities.helpers import Helpers

from quotesbot.utilities.profileextractor import ProfileExtractor
from quotesbot.utilities.profileextractorbeautifulsoup import ProfileExtractorBeautifulSoup
from scrapy_splash import SplashRequest

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

import time
import requests

class UpdateChurchWithStaffFromWebPages:

    print("setup class")

    helpers = Helpers()

    # get churches
    churches_file_path = "churches.json"
    with open(churches_file_path, "r") as file:
        churchesData = json.load(file)

    churches = churchesData["churches"]
    if churches == None:
        churches = []

    print("churches resolved")

    def appendWebPagesBasedOnStaff(self, church, startURLs):

        if "pages" in church and "name" in church and church["name"] == "Mission Hills Church Littleton Campus":
            for page in church["pages"][:3]:

                if "url" in page and "type" in page:
                    url = page["url"]
                    typ = page["type"]

                    if typ == "staff" and url.find(".pdf") == -1:

                        processor = "extract-profile-contacts-from-webpage"
                        needsToBeProcessed = self.helpers.checkIfNeedsProcessing(church, processor, url)

                        if needsToBeProcessed:

                            if url.find('staff') >= 0 or \
                                    url.find('about') >= 0 or \
                                    url.find('leader') >= 0 or \
                                    url.find('contact') >= 0 or \
                                    url.find('team') >= 0 or \
                                    url.find('leader') >= 0 or \
                                    url.find('who-we-are') >= 0 or \
                                    url.find('pastor') >= 0:

                                print('**************** process page: ', url)
                                startURLs.append(url)

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


    def updateWithStaffFromStaffWebPagesUsingChromeDriver(self, church):

        changed = False

        # extract contacts from staff web pages
        print("process church: ", church["name"])

        if "pages" in church:
            for page in church["pages"]:
                if "url" in page and "type" in page and page["type"] == "staff":

                    changed = True

                    url = page["url"]

                    processor = "extract-profile-contacts-from-webpage-chromedriver"
                    needsToBeProcessed = self.helpers.checkIfNeedsProcessing(church, processor, url)

                    if needsToBeProcessed == True:

                        print("process staff page: ", url)

                        changed = True

                        print("process facebook .....................")
                        service = Service(ChromeDriverManager().install())
                        driver = webdriver.Chrome(service=service)

                        driver.get(url)

                        # Wait for the page to load completely
                        time.sleep(10)  # Increase this if necessary for your connection

                        # Get the page source and parse it with BeautifulSoup
                        soup = BeautifulSoup(driver.page_source, 'html.parser')
                        driver.quit()

                        # crawl page and get schema
                        extractor = ProfileExtractorBeautifulSoup()
                        schema = extractor.constructSchema(church, url, soup)
                        extractor.extractProfilesUsingSchema(church, url, soup, schema)

                        self.helpers.markAsProcessed(church, processor, url)

                    break

        return changed
