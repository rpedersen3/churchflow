# -*- coding: utf-8 -*-

import cv2
import dlib
import numpy as np
import matplotlib.pyplot as plt
import urllib.request
from ethnicolr import census_ln
from names_dataset import NameDataset, NameWrapper
import math
import requests
import re
from collections import Counter

from openai import OpenAI
from bs4 import BeautifulSoup

from langchain_core.callbacks.base import BaseCallbackHandler
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain.chains import LLMChain
from langchain_community.llms import GPT4All
from langchain_core.prompts import PromptTemplate



import nltk
from nltk.corpus import stopwords
nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')
nltk.download('maxent_ne_chunker')
nltk.download('words')
nltk.download('stopwords')

client = OpenAI(
  organization='',
  api_key=''
)

import gpt4all
class GroupCheck:
    name = "groupcheck"

    nltk.download('stopwords')


    def remove_possessive(self, text):
        # Define a regular expression pattern to match "'s" at the end of words
        pattern = r"'s\b"
        # Use re.sub to replace matches of the pattern with an empty string
        text_without_possessive = re.sub(pattern, "", text)
        return text_without_possessive

    def count_words_in_list(self, word_list1, word_list2):
        # Count the occurrences of words in word_list1
        word_counts = Counter(word_list1)

        # Filter the counts to only include words from word_list2
        word_counts_filtered = {word: count for word, count in word_counts.items() if word in word_list2}

        return len(word_counts_filtered)

    def split_on_multiple_chars(self, text, delimiters):
        #print("********** split_on_multiple_chars: ", text, ", del: ", delimiters)
        # Create a regular expression pattern that matches any of the specified delimiters
        pattern = '|'.join(map(re.escape, delimiters))
        # Use re.split() with the pattern to split the text
        parts = re.split(pattern, text)
        return parts

    def isGroupName(self, name):

        foundGroupName = False


        stop_words = set(stopwords.words('english'))

        # remove extra name stuff after "|", "-"
        delimiters = ['|', ',', '-']
        name = self.split_on_multiple_chars(name, delimiters)[0]
        name = name.lower()


        name = self.remove_possessive(name)
        words = name.split()
        total_original_words = len(words)

        if total_original_words < 10:
            total_stop_words = len([word for word in words if word.lower() in stop_words])
            filtered_words = [word for word in words if word.lower() not in stop_words]
            filtered_words = filtered_words[:4]

            # remove extra stuff
            # 's, at, or,
            primaryNames = [
                "group",
                "groups",
                "life",
                "bible",
                "studies",
                "ministry",
                "mission",
                "team",
                "study",
                "school",
                "gathering",
                "prayer",
                "outreach",
                "classes",
                "class",
                "support",
                "interest",
                "mentoring",
                "community",
                "connecting"
            ]

            typeNames = [
                "mom",
                "moms",
                "singles",
                "wives",
                "coed",
                "adult",
                "adults",
                "child",
                "children",
                "teen",
                "teenager",
                "teenagers",
                "kid",
                "kids",
                "men",
                "mens",
                "women",
                "womens",
                "parents",
                "parent",
                "student",
                "students",
                "fathers",
                "mothers",
                "middle",
                "infant",
                "infants",
                "preschooler",
                "preschoolers",
                "ladies",
                "lady",
                "military",
                "veterans",
                "55+",
                "college"
            ]

            dateNames = [
                "weekly",
                "monday",
                "tuesday",
                "wednesday",
                "thursday",
                "friday",
                "saturday",
                "sunday",
                "hour"
            ]

            activityNames = [
                "hiking",
                "biking",
                "karate",
                "pickleball",
                "frisbee",
                "volleyball",
                "league",
                "crochet",
                "quilter",
                "quilters",
                "basketball",
                "football",
                "softball",
                "beach",
                "wilderness"
            ]

            caringNames = [
                "divorce",
                "grief"
                "infertility",
                "finance",
                "marriage"
            ]

            primaryWordCount = self.count_words_in_list(filtered_words, primaryNames)
            if (primaryWordCount > 2):
                primaryWordCount = 2

            typeWordCount = self.count_words_in_list(filtered_words, typeNames)
            if (typeWordCount > 2):
                typeWordCount = 2

            activityWordCount = self.count_words_in_list(filtered_words, activityNames)
            if (activityWordCount > 1):
                activityWordCount = 1

            dateWordCount = self.count_words_in_list(filtered_words, dateNames)
            if (dateWordCount > 1):
                dateWordCount = 1

            caringWordCount = self.count_words_in_list(filtered_words, caringNames)
            if (caringWordCount > 1):
                caringWordCount = 1

            totalWordCount = len(filtered_words)

            #print("words: ", filtered_words)
            #print("total: ", totalWordCount, ", primary: ", primaryWordCount, ", activity: ", activityWordCount, ", caring: ", caringWordCount)
            missingWords = totalWordCount - primaryWordCount - typeWordCount - activityWordCount - caringWordCount - dateWordCount

            if (total_original_words == 1 and totalWordCount == 1 and missingWords == 0 and activityWordCount == 0 and dateWordCount == 0 and total_stop_words == 0) or \
                    (total_original_words < 5 and totalWordCount == 2 and missingWords == 0 and total_stop_words <= 1) or \
                    (totalWordCount == 3 and missingWords <= 1 and total_stop_words <= 1) or \
                    (totalWordCount == 4 and missingWords <= 1 and total_stop_words <= 2):
                foundGroupName = True







        return foundGroupName


    def getJsonFromHtmlUsingLocalLLM(self, html):

        s1 = BeautifulSoup(html, 'html.parser')

        # Remove class attributes from all elements
        for tag in s1.find_all(True):
            tag.attrs = {}
        html = s1.prettify()

        #print('div: ', html)


        local_path = (
            "C:/Users/Richard Pedersen/AppData\Local/nomic.ai/GPT4All/Nous-Hermes-2-Mistral-7B-DPO.Q4_0.gguf"
        )

        model = gpt4all.GPT4All("C:/Users/Richard Pedersen/AppData\Local/nomic.ai/GPT4All/Nous-Hermes-2-Mistral-7B-DPO.Q4_0.gguf"
                            )
        with model.chat_session():
            questions = [
                "Can you explain what is a large language model?",
                "Can you give some examples applications?",
                "Are there any limitations?",
                "Summarize the above in two sentences.",
            ]
            for question in questions:
                answer = model.generate(question)
                print("Q:", question)
                print("A:", answer)


    def getJsonFromHtmlUsingOpenAI(self, html):

        s1 = BeautifulSoup(html, 'html.parser')

        # Remove class attributes from all elements
        for tag in s1.find_all(True):
            tag.attrs = {}
        html = s1.prettify()

        print('div: ', html)

        model = 'gpt-3.5-turbo'
        print("call chat with html")
        completion = client.chat.completions.create(
            model=model,  # Feel free to change the model to gpt-3.5-turbo-1106
            messages=[
                {"role": "system", "content": "You are a master at scraping and parsing raw HTML."},
                {"role": "user", "content": html}
            ],
            tools=[
                {
                    "type": "function",
                    "function": {
                        "name": "parse_data",
                        "description": "Parse raw HTML data nicely",
                        "parameters": {
                            'type': 'object',
                            'properties': {
                                'data': {
                                    'type': 'array',
                                    'items': {
                                        'type': 'object',
                                        'properties': {
                                            'title': {'type': 'string'},
                                            'time': {'type': 'string'},
                                            'day': {'type': 'string'}
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            ],
            tool_choice={
                "type": "function",
                "function": {"name": "parse_data"}
            }
        )

        # Calling the data results
        print('done with getting openai stuff')
        argument_str = completion.choices[0].message.tool_calls[0].function.arguments

        print("json: ", argument_str)
    def lookForGroupNames(self, htmlText, className):

        soup = BeautifulSoup(htmlText, 'html.parser')

        count = 0
        if className != "":
            select = 'div[class*="' + className + '"]'
            child_div_elements = soup.select(select)

            for div in child_div_elements:

                count = count + 1
                if count > 120:
                    break

                self.getJsonFromHtmlUsingLocalLLM(str(div))



