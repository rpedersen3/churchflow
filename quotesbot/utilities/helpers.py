from urllib.parse import urlparse
from datetime import datetime

class Helpers:

    def checkIfNeedsProcessing(self, currentChurch, processor, url):

        if "processed" not in currentChurch:
            currentChurch["processed"] = {}

        if processor not in currentChurch["processed"]:
            currentChurch["processed"][processor] = []

        needsToBeProcessed = True
        for processed in currentChurch["processed"][processor]:
            if processed["page"].lower().startswith(url.lower()):

                needsToBeProcessed = False

                if "datetime" in processed:

                    datetimeStr = processed["datetime"]
                    dt = datetime.strptime(datetimeStr, "%Y-%m-%d %H:%M:%S.%f")
                    if dt.date() >= datetime.today().date():
                        needsToBeProcessed = False

        return needsToBeProcessed

    def markAsProcessed(self, currentChurch, processor, url):

        processed = {
                    "page": url,
                    "datetime": str(datetime.now())
                }
        currentChurch["processed"][processor].append(processed)

    def findCurrentChurch(self, churches, url):

        isHomePage = False
        currentChurch = None
        for church in churches:

            if "link" in church:
                churchParse = urlparse(church["link"])
                churchDomain = churchParse.netloc.replace("www.", "")

                urlParse = urlparse(url)
                urlDomain = urlParse.netloc.replace("www.", "")

                if churchDomain == urlDomain:
                    currentChurch = church

                    # print("path: ", urlParse.path)
                    if urlParse.path == '' or urlParse.path == '/':
                        isHomePage = True

                    break

        return currentChurch, isHomePage





    def getPage(self, pages, type, url):

        for page in pages:
            if page["type"] == type and page["url"] == url:
                return page

        return None