import json
import re
import base64
from io import BytesIO
from PIL import Image
import os

from quotesbot.utilities.helpers import Helpers

from quotesbot.utilities.profileextractor import ProfileExtractor

from scrapy_splash import SplashRequest

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

        if "pages" in church:
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


    def updateChurchWithStaffFromWebPages(self, church, response):

        print(".........................")

        changed = False

        # extract contacts from staff web pages

        print("process church: ", church["name"])
        print("process staff page: ", response.url)

        processor = "extract-profile-contacts-from-webpage"
        needsToBeProcessed = self.helpers.checkIfNeedsProcessing(church, processor, response.url)

        if needsToBeProcessed == True:
            print("process staff page: ", response.url)

            changed = True

            # crawl page and get schema
            extractor = ProfileExtractor()
            schema = extractor.extractProfilesFromWebPage(church, response, None, None, None, None)
            extractor.extractProfilesUsingSchema(church, response, schema)

            self.helpers.markAsProcessed(church, processor, response.url)


            '''
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

            '''
        else:
            print("processing not needed")

        # self.getLeadPastorInfoUsingAzureAI(currentChurch)
        # self.searchForContacts(currentChurch, response)




        return changed