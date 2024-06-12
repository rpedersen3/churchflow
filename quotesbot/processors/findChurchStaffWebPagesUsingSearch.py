import time
from urllib.parse import urlparse

from googleapiclient.discovery import build

from quotesbot.utilities.helpers import Helpers

class FindChurchStaffWebPagesUsingSearch:

    helpers = Helpers()

    def findStaffWebPages(self, church, googleKey):

        changed = False

        if "link" in church:

            link = church["link"]

            processor = "extract-staff-pages-from-webpage"
            needsToBeProcessed = self.helpers.checkIfNeedsProcessing(church, processor, link)

            print("link: ", link, ", needs: ", needsToBeProcessed)

            if needsToBeProcessed:

                print("process: ", link)
                if link != "" and link.find("facebook") == -1:

                    changed = True

                    pages = []
                    if "pages" in church:
                        pages = church["pages"]

                    if len(pages) == 0:

                        time.sleep(1)
                        api_key = googleKey
                        service = build(
                            "customsearch", "v1", developerKey=api_key
                        )

                        parsed_url = urlparse(link)
                        domain = parsed_url.netloc.replace("www.", "")

                        names = "pastor", "elder";  # , "deacon", "minister"

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

                            # print("--------------------------------------")
                            # print(res)
                            # print("--------------------------------------")

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

                                            page = self.helpers.getPage(pages, "staff", link)
                                            if page is None:
                                                page = {
                                                    "type": "staff",
                                                    "url": link
                                                }
                                                pages.append(page)

                            if len(pages) > 0:
                                print("found pages: ", pages)
                                church["pages"] = pages

                                break

                    needsToBeProcessed = self.helpers.markAsProcessed(church, processor, church["link"])


        return changed