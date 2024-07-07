from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

from urllib.parse import urlparse
from bs4 import BeautifulSoup
import time
import requests
import json
import re


class VineyardProcessor:

    # get churches
    churchesData = None
    churches_file_path = "churches.json"
    with open(churches_file_path, "r") as file:
        churchesData = json.load(file)

    churches = churchesData["churches"]
    if churches == None:
        churches = []



    def strip_non_visible_characters(self, s: str) -> str:
        # Define a regular expression pattern to match non-visible characters
        pattern = re.compile(r'[^\x20-\x7E]+')
        # Substitute non-visible characters with an empty string
        return re.sub(pattern, '', s)

    def geocodeAddress(self, address):

        url = 'https://nominatim.openstreetmap.org/search?format=json&email=richardpedersen3@gmail.com&q=' + address
        '''
            params = {
            'q': address,
            'format': 'json'
        }
        response = requests.get(url, params=params)
        '''
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            if data:
                return data[0]['lat'], data[0]['lon']
            else:
                print('Address not found')
                return None, None
        else:
            print('Error:', response.status_code)
            return None, None

    def saveChurches(self):

        # save to churches file
        self.churchesData["churches"] = self.churches
        with open(self.churches_file_path, "w") as json_file:
            json.dump(self.churchesData, json_file, indent=4)

    def findChurches(self):

        for i in range(1, 6):

            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service)

            # URL of the ELCA World Map page
            url = "https://vineyardusa.org/find/?_region=mountain-region"
            if i > 1:
                url = "https://vineyardusa.org/find/?_region=mountain-region&_page=" + str(i)

            driver.get(url)

            # Wait for the page to load completely
            time.sleep(10)  # Increase this if necessary for your connection


            # Get the page source and parse it with BeautifulSoup
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            driver.quit()

            #print("soup: ", soup)
            for church in soup.find_all('article', class_ ="wpgb-card-12"):

                print(" process article")
                if church.find('a'):

                    name = church.find('a').get_text(strip=True).strip()
                    cityStr = church.find('div', class_ ="wpgb-block-3").get_text(strip=True).replace(",", "").strip()
                    stateStr = church.find('div', class_="wpgb-block-4").get_text(strip=True).strip()


                    hrefs = [a['href'] for a in church.find_all('a', href=True)]
                    if len(hrefs) > 0:
                        website = hrefs[0]

                        parsed_url = urlparse(website)
                        domain = parsed_url.netloc.replace("www.", "")
                        domain = domain.replace("/", "")


                        if (stateStr == "CO"):

                            print(" church: ", name, ", domain: ", domain)

                            foundChurch = False
                            for church in self.churches:

                                if "link" in church:

                                    domain = domain.replace("/", "")

                                    link = church["link"]
                                    parsed_url = urlparse(link)
                                    churchDomain = parsed_url.netloc.replace("www.", "")
                                    churchDomain = churchDomain.replace("/", "")

                                    if domain.lower() == churchDomain.lower():

                                        print(f"****** found Name: {name}, domain: {domain}")

                                        print("found church: ", name)

                                        network = ""
                                        if "network" in church:
                                            network = church["network"]

                                        networkName = "Vineyard Church"
                                        if network.find(networkName) == -1:
                                            if network == "":
                                                network = networkName
                                            else:
                                                network = network + ", " + networkName


                                        church["network"] = network

                                        foundChurch = True

                                        self.saveChurches()

                            if foundChurch == False:

                                print(f"********* not found church: {name}, domain: {domain}")
