from rdflib import Graph, URIRef, Literal, Namespace, RDF, RDFS
from urllib.parse import urlparse
import json
import re
import string
import random
import requests
import time

from collections.abc import Sequence
from google.cloud import enterpriseknowledgegraph as ekg

class UpdateChurchDenomination:

    api_key = ''

    def updateChurchDenominationWithOpenAi(self, church):

        changed = False

        if "denomination" not in church and "name" in church:

            name = church["name"].lower()

            if name.find("baptist") >= 0:
                church["denomination"] = "baptist"

            elif name.find("catholic") >= 0:
                church["denomination"] = "catholic"
            elif name.find("sacred heart") >= 0:
                church["denomination"] = "catholic"
            elif name.find("our lady") >= 0:
                church["denomination"] = "catholic"

            elif name.find("united methodist") >= 0:
                church["denomination"] = "united methodist church"

            elif name.find("presbyterian") >= 0:
                church["denomination"] = "presbyterian"

            elif name.find("united church of christ") >= 0:
                church["denomination"] = "united church of christ"

            elif name.find("apostolic") >= 0:
                church["denomination"] = "apostolic"

            elif name.find("lutheran") >= 0:
                church["denomination"] = "lutheran"

            elif name.find("episcopal") >= 0:
                church["denomination"] = "episcopal"


            elif name.find("church of christ") >= 0:
                church["denomination"] = "church of christ"

            elif name.find("nazarene") >= 0:
                church["denomination"] = "church of the nazarene"

            elif name.find("evangelical") >= 0:
                church["denomination"] = "evangelical"

            elif name.find("adventist") >= 0:
                church["denomination"] = "seventh-day adventist"

            elif name.find("mennonite") >= 0:
                church["denomination"] = "mennonite"

            else:
                church["denomination"] = "unknown"

            changed = True


        if self.api_key != '' and "is-primary" in church and "name" in church and "addressInfo" in church and "city" in church["addressInfo"]:

            if church["is-primary"] == "yes":

                changed = True

                time.sleep(0.5)



                # Define the endpoint URL
                url = 'https://api.openai.com/v1/chat/completions'

                # Set up the headers including the API key
                headers = {
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {self.api_key}',
                }

                name = church["name"]
                street = church["addressInfo"]["street"]
                city = church["addressInfo"]["city"]
                website = church["link"]

                query = 'What is the denomination, lead pastor, facebook url, twitter url, instagram url, youtube url and website URL of ' + name + " in " + city + ', CO? Provide response in JSON format.'
                print("Query: ", query)

                # Define the payload with your query
                payload = {
                    'model': 'gpt-4o',
                    'messages': [
                        {
                            'role': 'system',
                            'content': 'You are a helpful assistant.'
                        },
                        {
                            'role': 'user',
                            'content': query
                        }
                    ],
                    'max_tokens': 400
                }

                # Make the API call
                response = requests.post(url, headers=headers, json=payload)
                print("openai response: ", response)

                # Parse the response
                if response.status_code == 200:
                    data = response.json()
                    answer = data['choices'][0]['message']['content']
                    print("the answer: " + answer)

                    json_pattern = re.compile(r'\{.*\}', re.DOTALL)
                    json_match = json_pattern.search(answer)

                    if json_match:
                        json_str = json_match.group()
                        try:
                            jsonObject = json.loads(json_str)
                            print(json.dumps(jsonObject, indent=2))

                            church["openai"] = {}

                            if "denomination" in jsonObject:
                                church["openai"]["denomination"] = jsonObject["denomination"]
                                print("denomination: ", jsonObject["denomination"])
                            if "lead_pastor" in jsonObject:
                                church["openai"]["leadPastor"] = jsonObject["lead_pastor"]
                                print("lead_pastor: ", jsonObject["lead_pastor"])

                            if "facebook_url" in jsonObject:
                                church["openai"]["facebookUrl"] = jsonObject["facebook_url"]
                                print("facebook_url: ", jsonObject["facebook_url"])
                            if "twitter_url" in jsonObject:
                                church["openai"]["twitterUrl"] = jsonObject["twitter_url"]
                                print("twitter_url: ", jsonObject["twitter_url"])
                            if "instagram_url" in jsonObject:
                                church["openai"]["instagramUrl"] = jsonObject["instagram_url"]
                                print("instagram_url: ", jsonObject["instagram_url"])
                            if "tiktok_url" in jsonObject:
                                church["openai"]["tiktokUrl"] = jsonObject["tiktok_url"]
                                print("tiktok_url: ", jsonObject["tiktok_url"])
                            if "youtube_url" in jsonObject:
                                church["openai"]["youtubeUrl"] = jsonObject["youtube_url"]
                                print("youtube_url: ", jsonObject["youtube_url"])
                            if "website_url" in jsonObject:
                                church["openai"]["websiteUrl"] = jsonObject["website_url"]
                                print("website_url: ", jsonObject["website_url"])


                            if "facebook" in jsonObject:
                                church["openai"]["facebookUrl"] = jsonObject["facebook"]
                                print("facebook_url: ", jsonObject["facebook"])
                            if "twitter" in jsonObject:
                                church["openai"]["twitterUrl"] = jsonObject["twitter"]
                                print("twitter_url: ", jsonObject["twitter"])
                            if "instagram" in jsonObject:
                                church["openai"]["instagramUrl"] = jsonObject["instagram"]
                                print("instagram_url: ", jsonObject["instagram"])
                            if "tiktok" in jsonObject:
                                church["openai"]["tiktokUrl"] = jsonObject["tiktok"]
                                print("tiktok_url: ", jsonObject["tiktok"])
                            if "youtube" in jsonObject:
                                church["openai"]["youtubeUrl"] = jsonObject["youtube"]
                                print("youtube_url: ", jsonObject["youtube"])
                            if "website" in jsonObject:
                                church["openai"]["websiteUrl"] = jsonObject["website"]
                                print("website_url: ", jsonObject["website"])

                            if "social_media" in jsonObject:

                                if "facebook_url" in jsonObject["social_media"]:
                                    church["openai"]["facebookUrl"] = jsonObject["social_media"]["facebook_url"]
                                    print("facebook_url: ", jsonObject["social_media"]["facebook_url"])
                                if "twitter_url" in jsonObject["social_media"]:
                                    church["openai"]["twitterUrl"] = jsonObject["social_media"]["twitter_url"]
                                    print("twitter_url: ", jsonObject["social_media"]["twitter_url"])
                                if "instagram_url" in jsonObject["social_media"]:
                                    church["openai"]["instagramUrl"] = jsonObject["social_media"]["instagram_url"]
                                    print("instagram_url: ", jsonObject["social_media"]["instagram_url"])
                                if "tiktok_url" in jsonObject["social_media"]:
                                    church["openai"]["tiktokUrl"] = jsonObject["social_media"]["tiktok_url"]
                                    print("tiktok_url: ", jsonObject["social_media"]["tiktok_url"])
                                if "youtube_url" in jsonObject["social_media"]:
                                    church["openai"]["youtubeUrl"] = jsonObject["social_media"]["youtube_url"]
                                    print("youtube_url: ", jsonObject["social_media"]["youtube_url"])
                                if "website_url" in jsonObject["social_media"]:
                                    church["openai"]["websiteUrl"] = jsonObject["social_media"]["website_url"]
                                    print("website_url: ", jsonObject["social_media"]["website_url"])

                                if "facebook" in jsonObject["social_media"]:
                                    church["openai"]["facebookUrl"] = jsonObject["social_media"]["facebook"]
                                    print("facebook_url: ", jsonObject["social_media"]["facebook"])
                                if "twitter" in jsonObject["social_media"]:
                                    church["openai"]["twitterUrl"] = jsonObject["social_media"]["twitter"]
                                    print("twitter_url: ", jsonObject["social_media"]["twitter"])
                                if "instagram" in jsonObject["social_media"]:
                                    church["openai"]["instagramUrl"] = jsonObject["social_media"]["instagram"]
                                    print("instagram_url: ", jsonObject["social_media"]["instagram"])
                                if "tiktok" in jsonObject["social_media"]:
                                    church["openai"]["tiktokUrl"] = jsonObject["social_media"]["tiktok"]
                                    print("tiktok_url: ", jsonObject["social_media"]["tiktok"])
                                if "youtube" in jsonObject["social_media"]:
                                    church["openai"]["youtubeUrl"] = jsonObject["social_media"]["youtube"]
                                    print("youtube_url: ", jsonObject["social_media"]["youtube"])
                                if "website" in jsonObject["social_media"]:
                                    church["openai"]["websiteUrl"] = jsonObject["social_media"]["website"]
                                    print("website_url: ", jsonObject["social_media"]["website"])




                        except json.JSONDecodeError as e:
                            print(f"JSON Decode Error: {e}")
                    else:
                        print("No JSON object found in the string")



                else:
                    print(f'Error: {response.status_code}')
                    print(response.text)


        return changed



    def updateChurchDenominationWithGoogleGraph(self, church):

        if self.api_key != '' and "is-primary" in church and "name" in church and "addressInfo" in church and "street" in church["addressInfo"] and "city" in church["addressInfo"]:

            if church["is-primary"] == "yes":
                changed = True

                time.sleep(0.5)

                name = church["name"]
                street = church["addressInfo"]["street"]
                city = church["addressInfo"]["city"]

                # query = 'What is the denomination, lead pastor information, facebook url, twitter url, instagram url, youtube url and website URL of ' + name + " at " + city + ', CO? Provide response in JSON format.'
                search_query = 'place ' + name + ' at ' + street + ', ' + city + ', Colorado'
                search_query = "denver broncos stadium"
                #search_query = "taylor swift"
                search_query = "ChIJx8kD9Ar2a4cRx3UGuZ04I4g"
                '''
                def search_sample(
                        project_id: str,
                        location: str,
                        search_query: str,
                        languages: Sequence[str] = None,
                        types: Sequence[str] = None,
                        limit: int = 20,
                ):
                
                
                - Cloud MID: c-07xw4yymn
                    - googleKgMID: /m/02hxv8
                    - googlePlaceID: ChIJVbc8qLp4bIcRhaypxkMxvLE
                    - wikidataQID: Q1046135
        
        
                '''
                ids = ["ChIJVbc8qLp4bIcRhaypxkMxvLE"]

                api_key = ""
                place_id = "ChIJx8kD9Ar2a4cRx3UGuZ04I4g"
                fields = "*"
                url = f"https://maps.googleapis.com/maps/api/place/details/json?place_id={place_id}&key={api_key}"
                response = requests.get(url)
                data = response.json()
                print("place data: ", data)


                '''
                #ids = ["c-07xw4yymn"]

                project_id = "my-project-1712412027646"
                location = "global"


                # Create a client
                client = ekg.EnterpriseKnowledgeGraphServiceClient()

                # The full resource name of the location
                # e.g. projects/{project_id}/locations/{location}
                parent = client.common_location_path(project=project_id, location=location)

                # Initialize request argument(s)
                request = ekg.LookupRequest(
                    parent=parent,
                    ids=ids
                )

                # Make the request
                response = client.lookup(request=request)


                print(f"Lookup IDs: {ids}\n")

                print(response)

                # Extract and print date from response
                for item in response.item_list_element:
                    result = item.get("result")

                    print(f"Name: {result.get('name')}")
                    print(f"- Description: {result.get('description')}")
                    print(f"- Types: {result.get('@type')}\n")

                    detailed_description = result.get("detailedDescription")

                    if detailed_description:
                        print("- Detailed Description:")
                        print(f"\t- Article Body: {detailed_description.get('articleBody')}")
                        print(f"\t- URL: {detailed_description.get('url')}")
                        print(f"\t- License: {detailed_description.get('license')}\n")

                    print(f"- Cloud MID: {result.get('@id')}")
                    for identifier in result.get("identifier"):
                        print(f"\t- {identifier.get('name')}: {identifier.get('value')}")

                    print("\n")


                '''








                '''
                
                
                
                

                # Initialize request argument(s)
                request = ekg.SearchRequest(parent=parent,
                                            query=search_query,
                                            types=["Place"])

                # Make the request
                response = client.search(request=request)

                print(f"Search Query: {search_query}\n")

                # Extract and print date from response
                for item in response.item_list_element:
                    result = item.get("result")

                    print(f"Name: {result.get('name')}")
                    print(f"- Description: {result.get('description')}")
                    print(f"- Types: {result.get('@type')}\n")

                    detailed_description = result.get("detailedDescription")

                    if detailed_description:
                        print("- Detailed Description:")
                        print(f"\t- Article Body: {detailed_description.get('articleBody')}")
                        print(f"\t- URL: {detailed_description.get('url')}")
                        print(f"\t- License: {detailed_description.get('license')}\n")

                    print(f"- Cloud MID: {result.get('@id')}")
                    for identifier in result.get("identifier"):
                        print(f"\t- {identifier.get('name')}: {identifier.get('value')}")

                    print("\n")
                '''

    def updateChurchDenominationWithGoogleGemini(self, church):

        changed = False

        if self.api_key != '' and "is-primary" in church and "name" in church and "addressInfo" in church and "street" in church["addressInfo"] and "city" in church["addressInfo"]:

            if church["is-primary"] == "yes":

                changed = True

                time.sleep(0.5)

                name = church["name"]
                street = church["addressInfo"]["street"]
                city = church["addressInfo"]["city"]

                #query = 'What is the denomination, lead pastor information, facebook url, twitter url, instagram url, youtube url and website URL of ' + name + " at " + city + ', CO? Provide response in JSON format.'
                query = 'What is the denomination, lead pastor, facebook url, twitter url, instagram url, youtube url and website URL of ' + name + ' at ' + street + ', ' + city + ', CO? Provide response in JSON format.'

                #innerQuery = "Pikes Peak Christian Church information including pastors"
                # innerQuery = "from church " + currentChurch["name"] + " in city " + currentChurch["addressInfo"]["city"] + " Colorado and website " + currentChurch["link"]
                #query = innerQuery  # + " using this JSON schema: \{ \"type\": \"object\", \"properties\": \{ \"fullname\": \{ \"type\": \"string\" \}, \"title\": \{ \"type\": \"string\" \}, \"email\": \{ \"type\": \"string\" \}, \"phone-number\": \{ \"type\": \"string\" \}\}\}"

                print("query: ", query)
                # query = "Lead Pastor from " + currentChurch["name"] + ", " + currentChurch["addressInfo"]["city"] + " using this JSON schema: \{ \"type\": \"object\", \"properties\": \{ \"fullname\": \{ \"type\": \"string\" \}, \"title\": \{ \"type\": \"string\" \}, \"email\": \{ \"type\": \"string\" \}, \"phone-number\": \{ \"type\": \"string\" \}\}\}"
                endpoint = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro-latest:generateContent?key=" + self.api_key
                # endpoint = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.0-ultra:generateContent?key=" + api_key

                payload = {"contents": [{
                    "parts": [{"text": query}]}],
                    "generationConfig": {
                        "response_mime_type": "application/json",
                    }}
                if self.api_key == '':
                    print("api key is not set for getAddressInfoUsingGooglePlaces")
                    return

                time.sleep(1)

                response = requests.post(url=endpoint, json=payload)
                data = response.json()

                print("************* json returned: ", data)

                if "candidates" in data:
                    for candidate in data["candidates"]:
                        if "content" in candidate:
                            if "parts" in candidate["content"]:
                                for part in candidate["content"]["parts"]:
                                    if "text" in part:
                                        text = part["text"]
                                        print('text: ', text)

                                        church["gemini"] = {}

                                        jsonObject = json.loads(text)

                                        if "denomination" in jsonObject:
                                            church["gemini"]["denomination"] = jsonObject["denomination"]
                                            print("denomination: ", jsonObject["denomination"])
                                        if "lead pastor" in jsonObject:
                                            if len(jsonObject["lead pastor"]) > 0:
                                                church["gemini"]["leadPastor"] = jsonObject["lead pastor"][0]
                                                print("lead_pastor: ", jsonObject["lead pastor"][0])

                                        if "facebook url" in jsonObject:
                                            church["openai"]["facebookUrl"] = jsonObject["facebook url"]
                                            print("facebook_url: ", jsonObject["facebook url"])

                                        if "twitter url" in jsonObject:
                                            church["openai"]["twitterUrl"] = jsonObject["twitter url"]
                                            print("twitter_url: ", jsonObject["twitter url"])

                                        if "instagram url" in jsonObject:
                                            church["openai"]["instagramUrl"] = jsonObject["instagram url"]
                                            print("instagram_url: ", jsonObject["instagram url"])

                                        if "youtube url" in jsonObject:
                                            church["openai"]["youtubeUrl"] = jsonObject["youtube url"]
                                            print("youtube_url: ", jsonObject["youtube url"])

                                        if "website url" in jsonObject:
                                            church["openai"]["websiteUrl"] = jsonObject["website url"]
                                            print("website_url: ", jsonObject["website url"])

                                        break
                        break

                '''
                # Define the endpoint URL
                url = 'https://api.openai.com/v1/chat/completions'

                # Set up the headers including the API key
                headers = {
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {self.api_key}',
                }

                name = church["name"]
                street = church["addressInfo"]["street"]
                city = church["addressInfo"]["city"]
                website = church["link"]

                query = 'What is the denomination, lead pastor, facebook url, twitter url, instagram url, youtube url and website URL of ' + name + " in " + city + ', CO? Provide response in JSON format.'
                print("Query: ", query)

                # Define the payload with your query
                payload = {
                    'model': 'gpt-4o',
                    'messages': [
                        {
                            'role': 'system',
                            'content': 'You are a helpful assistant.'
                        },
                        {
                            'role': 'user',
                            'content': query
                        }
                    ],
                    'max_tokens': 400
                }

                # Make the API call
                response = requests.post(url, headers=headers, json=payload)
                print("openai response: ", response)

                # Parse the response
                if response.status_code == 200:
                    data = response.json()
                    answer = data['choices'][0]['message']['content']
                    print("the answer: " + answer)

                    json_pattern = re.compile(r'\{.*\}', re.DOTALL)
                    json_match = json_pattern.search(answer)

                    if json_match:
                        json_str = json_match.group()
                        try:
                            jsonObject = json.loads(json_str)
                            print(json.dumps(jsonObject, indent=2))

                            church["openai"] = {}

                            if "denomination" in jsonObject:
                                church["openai"]["denomination"] = jsonObject["denomination"]
                                print("denomination: ", jsonObject["denomination"])
                            if "lead_pastor" in jsonObject:
                                church["openai"]["leadPastor"] = jsonObject["lead_pastor"]
                                print("lead_pastor: ", jsonObject["lead_pastor"])

                            if "facebook_url" in jsonObject:
                                church["openai"]["facebookUrl"] = jsonObject["facebook_url"]
                                print("facebook_url: ", jsonObject["facebook_url"])
                            if "twitter_url" in jsonObject:
                                church["openai"]["twitterUrl"] = jsonObject["twitter_url"]
                                print("twitter_url: ", jsonObject["twitter_url"])
                            if "instagram_url" in jsonObject:
                                church["openai"]["instagramUrl"] = jsonObject["instagram_url"]
                                print("instagram_url: ", jsonObject["instagram_url"])
                            if "tiktok_url" in jsonObject:
                                church["openai"]["tiktokUrl"] = jsonObject["tiktok_url"]
                                print("tiktok_url: ", jsonObject["tiktok_url"])
                            if "youtube_url" in jsonObject:
                                church["openai"]["youtubeUrl"] = jsonObject["youtube_url"]
                                print("youtube_url: ", jsonObject["youtube_url"])
                            if "website_url" in jsonObject:
                                church["openai"]["websiteUrl"] = jsonObject["website_url"]
                                print("website_url: ", jsonObject["website_url"])


                            if "facebook" in jsonObject:
                                church["openai"]["facebookUrl"] = jsonObject["facebook"]
                                print("facebook_url: ", jsonObject["facebook"])
                            if "twitter" in jsonObject:
                                church["openai"]["twitterUrl"] = jsonObject["twitter"]
                                print("twitter_url: ", jsonObject["twitter"])
                            if "instagram" in jsonObject:
                                church["openai"]["instagramUrl"] = jsonObject["instagram"]
                                print("instagram_url: ", jsonObject["instagram"])
                            if "tiktok" in jsonObject:
                                church["openai"]["tiktokUrl"] = jsonObject["tiktok"]
                                print("tiktok_url: ", jsonObject["tiktok"])
                            if "youtube" in jsonObject:
                                church["openai"]["youtubeUrl"] = jsonObject["youtube"]
                                print("youtube_url: ", jsonObject["youtube"])
                            if "website" in jsonObject:
                                church["openai"]["websiteUrl"] = jsonObject["website"]
                                print("website_url: ", jsonObject["website"])

                            if "social_media" in jsonObject:

                                if "facebook_url" in jsonObject["social_media"]:
                                    church["openai"]["facebookUrl"] = jsonObject["social_media"]["facebook_url"]
                                    print("facebook_url: ", jsonObject["social_media"]["facebook_url"])
                                if "twitter_url" in jsonObject["social_media"]:
                                    church["openai"]["twitterUrl"] = jsonObject["social_media"]["twitter_url"]
                                    print("twitter_url: ", jsonObject["social_media"]["twitter_url"])
                                if "instagram_url" in jsonObject["social_media"]:
                                    church["openai"]["instagramUrl"] = jsonObject["social_media"]["instagram_url"]
                                    print("instagram_url: ", jsonObject["social_media"]["instagram_url"])
                                if "tiktok_url" in jsonObject["social_media"]:
                                    church["openai"]["tiktokUrl"] = jsonObject["social_media"]["tiktok_url"]
                                    print("tiktok_url: ", jsonObject["social_media"]["tiktok_url"])
                                if "youtube_url" in jsonObject["social_media"]:
                                    church["openai"]["youtubeUrl"] = jsonObject["social_media"]["youtube_url"]
                                    print("youtube_url: ", jsonObject["social_media"]["youtube_url"])
                                if "website_url" in jsonObject["social_media"]:
                                    church["openai"]["websiteUrl"] = jsonObject["social_media"]["website_url"]
                                    print("website_url: ", jsonObject["social_media"]["website_url"])

                                if "facebook" in jsonObject["social_media"]:
                                    church["openai"]["facebookUrl"] = jsonObject["social_media"]["facebook"]
                                    print("facebook_url: ", jsonObject["social_media"]["facebook"])
                                if "twitter" in jsonObject["social_media"]:
                                    church["openai"]["twitterUrl"] = jsonObject["social_media"]["twitter"]
                                    print("twitter_url: ", jsonObject["social_media"]["twitter"])
                                if "instagram" in jsonObject["social_media"]:
                                    church["openai"]["instagramUrl"] = jsonObject["social_media"]["instagram"]
                                    print("instagram_url: ", jsonObject["social_media"]["instagram"])
                                if "tiktok" in jsonObject["social_media"]:
                                    church["openai"]["tiktokUrl"] = jsonObject["social_media"]["tiktok"]
                                    print("tiktok_url: ", jsonObject["social_media"]["tiktok"])
                                if "youtube" in jsonObject["social_media"]:
                                    church["openai"]["youtubeUrl"] = jsonObject["social_media"]["youtube"]
                                    print("youtube_url: ", jsonObject["social_media"]["youtube"])
                                if "website" in jsonObject["social_media"]:
                                    church["openai"]["websiteUrl"] = jsonObject["social_media"]["website"]
                                    print("website_url: ", jsonObject["social_media"]["website"])




                        except json.JSONDecodeError as e:
                            print(f"JSON Decode Error: {e}")
                    else:
                        print("No JSON object found in the string")



                else:
                    print(f'Error: {response.status_code}')
                    print(response.text)
                '''

        return changed
