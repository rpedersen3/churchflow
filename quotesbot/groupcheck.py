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
from collections import Counter
import re
import nltk
from nltk.corpus import stopwords
nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')
nltk.download('maxent_ne_chunker')
nltk.download('words')
nltk.download('stopwords')

import pandas as pd


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
                "young",
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