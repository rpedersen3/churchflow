
import os
import json
from googleapiclient.discovery import build



class ChurchFinder:
    name = "churchfinder"


    def findChurches(self):

        api_key = ""
        service = build("customsearch", "v1", developerKey=api_key)

        search_engine_id = "YOUR_SEARCH_ENGINE_ID"
        api_version = "v1"
        search_engine = service.cse().list(cx=search_engine_id, version=api_version)

        query = "zenserp API tutorials"
        search_engine.q = query
        response = search_engine.execute()
        results = response["items"]

        print("results: ", results)