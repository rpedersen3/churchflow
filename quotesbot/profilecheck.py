# -*- coding: utf-8 -*-
import re
import cv2
import dlib
import numpy as np
import matplotlib.pyplot as plt
import urllib.request
from ethnicolr import  pred_census_ln, census_ln, pred_wiki_ln
import spacy
import scrapy
from scrapy_splash import SplashRequest
import os
from PIL import Image, ImageEnhance

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




class ProfileCheck:
    name = "profilecheck"

    # ------------ Model for Age detection --------#
    #age_weights = "age_deploy.prototxt"
    #age_config = "age_net.caffemodel"
    #age_Net = cv2.dnn.readNet(age_config, age_weights)

    #gender_weights = "gender_deploy.prototxt"
    #gender_config = "gender_net.caffemodel"
    #gender_Net = cv2.dnn.readNet(gender_config, gender_weights)

    # Model requirements for image
    #ageList = ['(0-2)', '(4-6)', '(8-12)', '(15-20)',
    #           '(25-32)', '(38-43)', '(48-53)', '(60-100)']
    #genderList = ['Male', 'Female']
    #model_mean = (78.4263377603, 87.7689143744, 114.895847746)

    nlp = spacy.load("en_core_web_sm")
    pd.set_option("display.max_rows", 200)

    def get_human_names(self, text):
        tokens = nltk.tokenize.word_tokenize(text)
        pos = nltk.pos_tag(tokens)
        sentt = nltk.ne_chunk(pos, binary=False)
        print('sentt: ', sentt)
        person_list = []
        person = []
        name = ""
        for subtree in sentt.subtrees(filter=lambda t: t.node == 'PERSON'):
            print('subtree: ', subtree)
            for leaf in subtree.leaves():
                person.append(leaf[0])
            if len(person) > 1:  # avoid grabbing lone surnames
                for part in person:
                    name += part + ' '
                if name[:-1] not in person_list:
                    person_list.append(name[:-1])
                name = ''
            person = []

        return (person_list)

    def get_job_titles(self, text):

        text = text[:60]


        if "minister" in text.lower():
            if "worship" in text.lower():
                return "Worship Minister"
            return "Minister"

        if "bishop" in text.lower():
            if "suffragan" in text.lower():
                return "Suffragan Bishop"
            return "Bishop"

        if "pastor" in text.lower():
            if "lead" in text.lower():
                if "worship" in text.lower():
                    return "Lead Worship Pastor"
                if "student" in text.lower():
                    return "Lead Student Pastor"
                if "children's" in text.lower():
                    return "Lead Children's Pastor"
                return "Lead Pastor"
            if "executive" in text.lower():
                return "Executive Pastor"
            if "senior" in text.lower():
                return "Senior Pastor"
            if "associate" in text.lower():
                return "Associate Pastor"
            if "worship" in text.lower():
                return "Worship Pastor"
            if "care" in text.lower():
                return "Care Pastor"
            if "next gen" in text.lower():
                return "Kids Pastor"
            if "groups" in text.lower():
                return "Groups Pastor"
            if "residency" in text.lower():
                return "Residency Pastor"
            return "Pastor"

        if "worship " in text.lower():
            if "leader" in text.lower():
                return "Worship Leader"

        if "executive" in text.lower():
            if "assistant" in text.lower():
                return "Executive Assistant"
            return "Executive"


        if "elder" in text.lower():
            return "Elder"

        if "deacon" in text.lower():
            return "Deacon"

        if "chairman" in text.lower():
            return "Chairman"

        if "treasurer" in text.lower():
            if "assistant" in text.lower():
                return "Assistant Treasurer"
            return "Treasurer"


        if "director" in text.lower():
            if "executive" in text.lower():
                return "Executive Director"
            if "associate" in text.lower():
                if "groups" in text.lower():
                    return "Groups Associate Director"
                if "kids" in text.lower():
                    return "Kids Associate Director"
                return "Associate Director"
            if "facilities" in text.lower():
                return "Facilities Director"
            if "connections" in text.lower():
                return "Connections Director"
            if "communications" in text.lower():
                return "Communications Director"
            if "kids" in text.lower():
                return "Kids Director"
            if "high school" in text.lower():
                return "High School Director"
            return "Director"

        if "rector" in text.lower():
            return "Rector"

        if "associate" in text.lower():
            return "Associate"

        if "manager" in text.lower():
            if "financial" in text.lower():
                return "Financial Manager"
            return "Manager"

        if "coordinator" in text.lower():
            if "facilities" in text.lower():
                return "Facilities Coordinator"
            if "care" in text.lower():
                return "Care Coordinator"
            if "groups" in text.lower():
                return "Groups Coordinator"
            if "next steps" in text.lower():
                return "Next Steps Coordinator"
            if "kids" in text.lower():
                return "Kids Coordinator"
            if "video" in text.lower():
                return "Video Coordinator"
            if "women's ministry" in text.lower():
                return "Women's Ministry Coordinator"
            if "men's ministry" in text.lower():
                return "Men's Ministry Coordinator"
            return "Coordinator"

        if "staff" in text.lower():
            if "facilities" in text.lower():
                return "Facilities Staff"
            return "Staff"

        if "receptionist" in text.lower():
            return "Receptionist"

        if "counselor" in text.lower():
            if "care" in text.lower():
                return "Care Counselor"
            if "biblical" in text.lower():
                return "Biblical Counselor"
            return "Counselor"

        if "administrative" in text.lower():
            if "assistant" in text.lower():
                return "Administrative Assistant"
            if "front desk" in text.lower():
                return "Front Desk Administrator"
            return "Administrative"

        if "administrator" in text.lower():
            if "database" in text.lower():
                return "Database Administrator"
            return "Administrator"

        if "lead" in text.lower():
            return "Lead"

        if "specialist" in text.lower():
            return "Specialist"

        if "resident" in text.lower():
            return "Resident"

        return None


    def get_departments(self, text):

        text = text[:120]
        if "ministry" in text.lower():
            if "services" in text.lower():
                return "Ministry Services"
            if "environments" in text.lower():
                return "Ministry Environments"
            return "Ministry"

        if "life center" in text.lower():
            return "Life Center"

        if "global outreach" in text.lower():
            return "Global Outreach"

        if "global mobilization" in text.lower():
            return "Global Mobilization"

        if "preschool" in text.lower():
            return "Preschool"

        if "high school" in text.lower():
            return "High School"

        if "young adult" in text.lower():
            return "Young Adult"

        if "elementary" in text.lower():
            return "Elementary"

        if "creative arts" in text.lower():
            return "Creative Arts"

        if "weekend experience" in text.lower():
            return "Weekend Experience"

        if "weekend experience" in text.lower():
            return "Weekend Experience"

        return None

    def isPersonName(self, name):

        #print("check name: ", name)
        fullname = None

        #  replace the name beginning with
        name = name.lower()
        if name.startswith("the "):
            name = name.replace("the ", "")

        name = name.replace("&", "and")

        # remove some common titles in front of name
        name = name.replace("fr.", "")
        name = name.replace("dr.", "")
        name = name.replace("rev.", "")
        name = name.replace("deacon", "")
        name = name.replace("associate", "")
        name = name.replace("board", "")
        name = name.replace("reverend", "")
        name = name.replace("staff", "")
        name = name.replace("africa", "")
        name = name.replace("asia", "")
        name = name.replace("takes", "")
        name = name.replace("father", "")
        name = name.replace("teach", "")
        name = name.replace("agenda", "")
        name = name.replace("weekend", "")
        name = name.replace("council", "")
        name = name.replace("members", "")
        name = name.replace("creed", "")
        name = name.replace("nicene", "")
        name = name.replace("evangelist", "")
        name = name.replace("ministerial", "")
        name = name.replace("minister", "")
        name = name.replace("read more", "")
        name = name.replace("suffragan", "")
        name = name.replace("zion", "")
        name = name.replace("lady", "")
        name = name.replace("sister", "")
        name = name.replace("brother", "")
        name = name.replace("worship", "")
        name = name.replace("arts", "")
        name = name.replace("women", "")
        name = name.replace("bible", "")
        name = name.replace("adult", "")
        name = name.replace("music", "")
        name = name.replace("player", "")
        name = name.replace("welcome", "")
        name = name.replace("about", "")
        name = name.replace("home", "")
        name = name.replace("clergy", "")
        name = name.replace("student", "")
        name = name.replace("elder", "")
        name = name.replace("community", "")
        name = name.replace("care ", "")
        name = name.replace("ministries ", "")
        name = name.replace("center", "")
        name = name.replace("select", "")
        name = name.replace("pastoral", "")
        name = name.replace("pastor", "")
        name = name.replace("founder", "")
        name = name.replace("standard", "")
        name = name.replace("celebration", "")
        name = name.replace("administrator", "")
        name = name.replace("senior", "")
        name = name.replace("peace", "")
        name = name.replace("building", "")
        name = name.replace("bookkeeper", "")
        name = name.replace("trusting", "")
        name = name.replace("benefited", "")
        name = name.replace("raised", "")
        name = name.replace("business", "")
        name = name.replace("personally", "")
        name = name.replace("event", "")
        name = name.replace("registration", "")
        name = name.replace("social", "")
        name = name.replace("scheduler", "")
        name = name.replace("sermons", "")
        name = name.replace("feature", "")
        name = name.replace("programs", "")
        name = name.replace("prayer", "")
        name = name.replace("reuests", "")
        name = name.replace("groups", "")
        name = name.replace("ministry", "")
        name = name.replace("early", "")
        name = name.replace("learning", "")
        name = name.replace("pathways", "")
        name = name.replace("connected", "")
        name = name.replace("apostle", "")
        name = name.replace("church", "")
        name = name.replace("emeritus", "")
        name = name.replace("school", "")
        name = name.replace("volunteers", "")
        name = name.replace("growth", "")
        name = name.replace("director", "")
        name = name.replace("coordinator", "")
        name = name.replace("office", "")
        name = name.replace("campus", "")
        name = name.replace("lead", "")
        name = name.replace("strategic", "")
        name = name.replace("associate", "")
        name = name.replace("contact", "")
        name = name.replace("team", "")
        name = name.replace("lay ", "")

        #print("****** name: ", name)


        nlpFoundAName = True
        '''
        doc = self.nlp(name)
        for ent in doc.ents:
            #print("check name: ", name)
            #print("label: ", ent.label_, ", text: ", ent.text)
            if ent.label_ == "PERSON":
                nlpFoundAName = True
                parts = ent.text.split()
                if len(parts) == 2:
                    fullname = ent.text
                    print("nlp fullname person: ", fullname)
        '''
        # lets try and parse name in pieces
        if nlpFoundAName:
            #print("************  check full name parts: ", name)
            fullname = self.isPersonNameUsingParts(name)
            #if fullname is not None:
            #    print("fullname parts: ", fullname)




        #print('fullname: ', fullname)
        return fullname

    def isPhoneNumber(self, string):
        r = re.compile(r'(\d{3}[-\.\s]??\d{3}[-\.\s]??\d{4}|\(\d{3}\)\s*\d{3}[-\.\s]??\d{4}|\d{3}[-\.\s]??\d{4})')
        phone_numbers = r.findall(string)

        phoneNumber = None
        if len(phone_numbers) > 0:
            phoneNumber = phone_numbers[0]

        return phoneNumber

    def isEmailAddresses(self, string):
        r = re.compile(r'[\w\.-]+@[\w\.-]+')
        email = r.findall(string)

        if len(email) == 0:
            return None

        return email

    def isPersonNameUsingParts(self, name):

        # grab first two words that sound like real names
        parts = name.split()

        fullname = None
        foundProfileLastname = False
        skipNextPart = False
        for part in parts:

            part = part.replace(".", "")
            part = part.replace(",", "")
            part = part.strip()
            if (len(part) < 2):
                continue

            if      part == "is" or \
                    part == "his" or \
                    part == "wife" or \
                    part == "with" or \
                    part == "stay" or \
                    part == "site" or \
                    part == "from" or \
                    part == "po" or \
                    part == "box" or \
                    part == "left" or \
                    part == "one" or \
                    part == "for" or \
                    part == "our" or \
                    part == "small" or \
                    part == "sing" or \
                    part == "god" or \
                    part == "live" or \
                    part == "she" or \
                    part == "he" or \
                    part == "while" or \
                    part == "first" or \
                    part == "time" or \
                    part == "check" or \
                    part == "out" or \
                    part == "at" or \
                    part == "came" or \
                    part == "plan" or \
                    part == "your" or \
                    part == "who" or \
                    part == "the" or \
                    part == "st" or \
                    part == "was" or \
                    part == "my" or \
                    part == "if" or \
                    part == "us" or \
                    part == "next" or \
                    part == "of" or \
                    part == "as" or \
                    part == "at" or \
                    part == "ask" or \
                    part == "you" or \
                    part == "we" or \
                    part == "in" or \
                    part == "all" or \
                    part == "mass" or \
                    part == "new" or \
                    part == "has" or \
                    part == "email" or \
                    part == "food" or \
                    part == "bank" or \
                    part == "member" or \
                    part == "portal" or \
                    part == "life" or \
                    part == "back" or \
                    part == "to" or \
                    part == "her":

                #print("break on part: ", part)
                break

            pattern = re.compile(r'[^a-zA-Z\s]')  # Matches any character that is not a letter or whitespace

            # Use the search method to check if the string contains any non-character characters
            match = pattern.search(part)
            if match:
                #print("break on non visible character: ", part)
                break



            #print("part: ", part)
            if part.lower() != "and" and skipNextPart == False:
                #print("part: ", part)
                names = [{'name': part}]

                df = pd.DataFrame(names)
                predictions = census_ln(df, 'name')
                #print("name: ", part)
                #print("predictions: ", predictions)

                pctwhite = predictions['pctwhite'].iloc[0]
                pctblack = predictions['pctblack'].iloc[0]
                pctapi = predictions['pctapi'].iloc[0]
                pctaian = predictions['pctaian'].iloc[0]
                pct2prace = predictions['pct2prace'].iloc[0]
                pcthispanic = predictions['pcthispanic'].iloc[0]


                if fullname is None:
                    fullname = part
                else:

                    # firstname is repeated, sometimes happends then just ignor it
                    if part == fullname:
                        continue

                    # lastname check
                    lastnamePred = pred_census_ln(df, 'name')
                    white = lastnamePred['white'].iloc[0]

                    fullname = fullname + " " + part
                    #print("fullname: ", fullname)

                    # check that lastname is a valid name
                    if str(white) != 'nan':
                        #print("found lastname: ", fullname)
                        foundProfileLastname = True

                    break


            # adjust for two people like Jane and Joe Smith => Jane Smith
            if skipNextPart:
                skipNextPart = False

            if part.lower() == "and":
                skipNextPart = True

        #print("fullname: ", fullname)
        if foundProfileLastname:
            #print("return fullname: ", fullname)
            return fullname

        return None


    def isProfileJobTitle(self, title):
        foundProfileTitle = False

        jobTitle = self.get_job_titles(title)

        return jobTitle


    def isProfileDepartment(self, department):

        department = self.get_departments(department)
        return department



    def isProfilePhoto(self, response, url):

        foundPhoto = False
        foundProfilePhoto = False

        #print("url: ", url)

        detector = dlib.get_frontal_face_detector()

        originalUrl = url

        urlLower = url.lower()
        if urlLower.find(".jpg") != -1 or urlLower.find(".jpeg") != -1 or urlLower.find(".png") != -1 or urlLower.find(".ashx") != -1:

            if urlLower.find(".jpg") != -1:
                offset = urlLower.find(".jpg")
                url = url[:offset] + ".jpg"

            if urlLower.find(".jpeg") != -1:
                offset = urlLower.find(".jpeg")
                url = url[:offset] + ".jpeg"

            if urlLower.find(".png") != -1:
                offset = urlLower.find(".png")
                url = url[:offset] + ".png"

            if urlLower.find(".ashx") != -1:
                offset = urlLower.find(".ashx")
                url = url[:offset] + ".ashx"


            # sometimes they come in sets so need to split them
            url = url.split(", ")[0]
            url = url.split(" ")[0]
            #print("process image: >>", url, "<<")

            foundPhoto = True

            hdrs = {
                "User-Agent": "XY"
            }


            gray_image = None

            try:

                #print("get photo arr")
                req = urllib.request.Request(url, headers=hdrs)
                response = urllib.request.urlopen(req)
                arr = np.asarray(bytearray(response.read()), dtype=np.uint8)

                #print("encode and detect: ", url)
                if url.find(".jpg") != -1 or url.find(".jpeg") != -1 or url.find(".jpeg") != -1 or url.find(".ashx") != -1:
                    frame = cv2.imdecode(arr, -1)
                    #print("found image 1 ")
                    gray_image = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

                if url.find(".png") != -1:
                    frame = cv2.imdecode(arr, cv2.IMREAD_COLOR)
                    #print("found image 2 ")
                    gray_image = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)


            except Exception as e:

                # problem getting image so lets see if we already have this file
                # read response from file if it exists
                print("---------------  Problem connecting to source: ", url)
                print("e: ", e)

                image_name = url.split('/')[-1]
                destination_folder = ".scrapy/imagefiles"
                os.makedirs(destination_folder, exist_ok=True)
                destination_file_path = os.path.join(destination_folder, os.path.basename(image_name)) + ".png"

                #print("-------- check if file exists: ", destination_file_path)
                if os.path.exists(destination_file_path):
                    img = Image.open(destination_file_path)
                    contrast_enhancer = ImageEnhance.Contrast(img)
                    enh = contrast_enhancer.enhance(2)
                    enhanced_image = np.asarray(enh)
                    gray_image = cv2.cvtColor(enhanced_image, cv2.COLOR_BGR2GRAY)

                    #print("print done open")
                    #print(img.format)
                    #print(img.size)
                    #print(img.mode)




            if gray_image is not None:

                try:
                    #print("try to get faces .............")
                    height, width = gray_image.shape[:2]

                    #plt.imshow(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
                    #plt.axis('off')
                    #plt.show()

                    rects = detector(gray_image)
                    #print('rects: ', str(rects))


                    # allow 2 faces
                    numberOfFaces = len(rects)
                    #print("********* number of faces: ", numberOfFaces)
                    if numberOfFaces < 3:
                        for rect in rects:
                            x, y, x2, y2, w, h = (rect.left(), rect.top(), rect.right(), rect.bottom(), rect.width(), rect.height())
                            #cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                            #print('***************************')
                            #print('image width: ', width, ',  image height: ', height)
                            #print('face width: ', w, ',  face height: ', h)
                            #print('x: ', x, ', ', 'y: ', y)

                            percentOfHeight = (h / height) * 100
                            percentFromTop = (y / height) * 100
                            percentFromBottom = ((height-y2) / height) * 100

                            #print("percentOfHeight: ", percentOfHeight)
                            #print("percentFromTop: ", percentFromTop)
                            #print("percentFromBottom: ", percentFromBottom)



                            # check if face is in middle of picture and is percent of total size
                            #if numberOfFaces == 1 and percentOfHeight > 20 and percentFromTop < 40 and percentFromBottom < 65:
                            #    foundProfilePhoto = True
                            #    print("found photo")
                            if percentOfHeight > 15:
                                foundProfilePhoto = True




                            #if foundProfilePhoto:

                                #print("found photo")


                                #face_img = frame[y:y+h, x:x+w].copy()
                                #blob = cv2.dnn.blobFromImage(face_img, 1, (227, 227), model_mean, swapRB=False)


                                #age_Net.setInput(blob)
                                #age_preds = age_Net.forward()
                                #age = ageList[age_preds[0].argmax()]
                                #i = age_preds[0].argmax()
                                #ageConfidence = age_preds[0][i]

                                #print('age: ', age, ", confidence: ", ageConfidence)

                                #gender_Net.setInput(blob)
                                #gender_preds = gender_Net.forward()
                                #gender = genderList[gender_preds[0].argmax()]
                                #j = gender_preds[0].argmax()
                                #genderConfidence = gender_preds[0][j]
                                ##print('gender: ', gender, ', confidence: ', genderConfidence)


                except Exception as e:
                    print("---------------  Problem reading photo: ", e)



        return foundPhoto, foundProfilePhoto

