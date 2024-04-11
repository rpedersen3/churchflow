# -*- coding: utf-8 -*-
import re
import cv2
import dlib
import numpy as np
import matplotlib.pyplot as plt
import urllib.request
from ethnicolr import census_ln
import spacy
from names_dataset import NameDataset, NameWrapper
import math
import requests
import nltk
from nltk.corpus import stopwords
nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')
nltk.download('maxent_ne_chunker')
nltk.download('words')
nltk.download('stopwords')

import pandas as pd


class ChurchCheck:
    name = "churchcheck"