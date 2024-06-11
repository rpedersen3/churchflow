import json
import re

from quotesbot.utilities.helpers import Helpers

from quotesbot.utilities.profileextractor import ProfileExtractor

class UpdateChurchWithStaffFromWebPages:

    # get churches
    churches_file_path = "churches.json"
    with open(churches_file_path, "r") as file:
        churchesData = json.load(file)

    churches = churchesData["churches"]
    if churches == None:
        churches = []


    def UpdateChurchWithStaffFromWebPages(self, response):

        # extract contacts from staff web pages
        currentChurch, isHomePage = Helpers.findCurrentChurch(self.churches, response.url)
        if currentChurch is not None and "name" in currentChurch:

            print("process church: ", currentChurch["name"])

            processor = "extract-profile-contacts-from-webpage"
            needsToBeProcessed = Helpers.checkIfNeedsProcessing(currentChurch, processor, response.url)

            if needsToBeProcessed == True:

                # crawl page and get schema
                schema = ProfileExtractor.extractProfilesFromWebPage(currentChurch, response, None, None, None, None)
                ProfileExtractor.extractProfilesUsingSchema(currentChurch, response, schema)

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

                    '''
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