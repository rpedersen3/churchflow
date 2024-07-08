from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time
import requests
import json
from urllib.parse import urlparse

class IfaProcessor:

    # get churches
    churchesData = None
    churches_file_path = "churches.json"
    with open(churches_file_path, "r") as file:
        churchesData = json.load(file)

    churches = churchesData["churches"]
    if churches == None:
        churches = []

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


        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service)

        # URL of the ELCA World Map page
        url = "https://interfaithallianceco.org/partners/"
        driver.get(url)

        # Wait for the page to load completely
        time.sleep(10)  # Increase this if necessary for your connection

        # Get the page source and parse it with BeautifulSoup
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        driver.quit()

        i = 1
        #print("soup: ", soup)
        for church in soup.find_all('p'):

            if church.find('a') != None:

                a = church.find('a')
                name = a.get_text(strip=True).strip()
                website = a.get('href')

                parsed_url = urlparse(website)
                domain = parsed_url.netloc.replace("www.", "")
                domain = domain.replace("/", "")


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

                            partner = ""
                            if "partner" in church:
                                partner = church["partner"]

                            partnerName = "Interfaith Alliance"
                            if partner.find(partnerName) == -1:
                                if partner == "":
                                    partner = partnerName
                                else:
                                    partner = partner + ", " + partnerName

                            church["partner"] = partner

                            foundChurch = True

                            self.saveChurches()

                if foundChurch == False:
                    print(f"********* not found church: {name}, domain: {domain}")


