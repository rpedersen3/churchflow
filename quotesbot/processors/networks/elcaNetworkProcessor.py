from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time
import requests
import json

class ElcaProcessor:

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
        url = "https://search.elca.org/Pages/WorldMap.aspx?Type=CityState&City=&State=Colorado&Language=&Congregation=&Accessibility="
        driver.get(url)

        # Wait for the page to load completely
        time.sleep(10)  # Increase this if necessary for your connection

        # Get the page source and parse it with BeautifulSoup
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        driver.quit()

        i = 1
        #print("soup: ", soup)
        sectionDiv = soup.find('div', id="map-search-locations")
        for church in sectionDiv.find_all('li'):

            #print("ch: ", church)
            name = church.find('a').get_text(strip=True)
            addressParts = church.find('p').get_text().split(',')
            address = addressParts[0]

            foundChurch = None

            lat, lon = self.geocodeAddress(address)
            if lat != None and lon != None:

                latValue = float(lat)
                lonValue = float(lon)

                if latValue > 38.0 and latValue < 41.0 and lonValue < -104.0 and lonValue > -106.0:


                    for ch in self.churches:
                        if "addressInfo" in ch and "street" in ch["addressInfo"] and "latitude" in ch and "longitude" in ch:
                            chLat = float(ch["latitude"])
                            chLon = float(ch["longitude"])

                            if (abs(chLat - latValue) < 0.01 and abs(chLon - lonValue) < 0.01):

                                firstPart = address.split(' ')[0]
                                chFirstPart = ch["addressInfo"]["street"].split(' ')[0]

                                if firstPart.lower() == chFirstPart.lower():

                                    foundChurch = ch
                                    break

                    if foundChurch == None:

                        # cycle through and see if address just matches
                        for ch in self.churches:
                            if "addressInfo" in ch and "street" in ch["addressInfo"]:
                                if address.lower().find(ch["addressInfo"]["street"].lower()) >= 0:
                                    foundChurch = ch
                                    break

                    if foundChurch == None:

                        print(f"****** not found Name: {name}, Address: {address}, loc: {lat} - {lon}")

                        i = i + 1
                        if i > 10000000:
                            break

            else:

                # cycle through and see if address just matches
                if foundChurch == None:
                    for ch in self.churches:
                        if "addressInfo" in ch and "street" in ch["addressInfo"]:
                            if address.lower().find(ch["addressInfo"]["street"].lower()) >= 0:
                                foundChurch = ch
                                break

                if foundChurch == None:
                    print(f"****** bad address: {name}, Address: {address}")


            if foundChurch != None:

                network = ""
                if "network" in foundChurch:
                    network = foundChurch["network"]

                if network.find("Evangelical Lutheran Church in America") == -1:
                    if network == "":
                        network = "Evangelical Lutheran Church in America"
                        print(f"found Name: {name}, Address: {address}, loc: {lat} - {lon}")
                    else:
                        network = network + ", " + "Evangelical Lutheran Church in America"


                foundChurch["network"] = network

                self.saveChurches()


