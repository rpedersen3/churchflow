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

        if "elder" in text.lower():
            return "Elder"

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

        # remove some common titles in front of name
        name = name.lower()
        name = name.replace("fr.", "")
        name = name.replace("rev.", "")
        name = name.replace("deacon", "")
        name = name.replace("staff", "")
        name = name.replace("clergy", "")
        name = name.replace("elder", "")
        name = name.replace("care ", "")
        name = name.replace("center", "")
        name = name.replace("pastoral", "")
        name = name.replace("pastor", "")
        name = name.replace("director", "")
        name = name.replace("coordinator", "")
        name = name.replace("office", "")
        name = name.replace("campus", "")
        name = name.replace("lead", "")
        name = name.replace("associate", "")

        #print("****** name: ", name)

        doc = self.nlp(name)
        for ent in doc.ents:
            #print("check name: ", name)
            #print("label: ", ent.label_, ", text: ", ent.text)
            if ent.label_ == "PERSON":
                parts = ent.text.split()
                if len(parts) == 2:
                    fullname = ent.text
                    #print("fullname person: ", fullname)

        # lets try and parse name in pieces
        if fullname is None:
            #print("check full name parts: ", name)
            fullname = self.isPersonNameUsingParts(name)
            #print("fullname parts: ", fullname)




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

            if part.lower() != "and" and skipNextPart == False:

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
                if str(pctwhite) != 'nan':
                    if fullname is None:
                        fullname = part
                    else:
                        fullname = fullname + " " + part
                        foundProfileLastname = True

                if foundProfileLastname:
                    break

            # adjust for two people like Jane and Joe Smith => Jane Smith
            if skipNextPart:
                skipNextPart = False

            if part.lower() == "and":
                skipNextPart = True

        #print("fullname: ", fullname)
        return fullname


    def isProfileJobTitle(self, title):
        foundProfileTitle = False

        jobTitle = self.get_job_titles(title)

        return jobTitle


    def isProfileDepartment(self, department):

        department = self.get_departments(department)
        return department


    def isProfilePhoto(self, url):

        foundProfilePhoto = False
        #print("url: ", url)

        detector = dlib.get_frontal_face_detector()

        if url.find(".jpg") != -1 or url.find(".jpeg") != -1 or url.find(".png") != -1 or url.find(".ashx") != -1:

            # sometimes they come in sets so need to split them
            url = url.split(", ")[0]
            #print("process image: >>", url, "<<")

            req = urllib.request.Request(url, headers={'User-Agent': 'XY'})
            response = urllib.request.urlopen(req)
            arr = np.asarray(bytearray(response.read()), dtype=np.uint8)

            frame = None
            if url.find(".jpg") != -1 or url.find(".jpeg") != -1 or url.find(".jpeg") != -1 or url.find(".ashx") != -1:
                frame = cv2.imdecode(arr, -1)
            if url.find(".png") != -1:
                frame = cv2.imdecode(arr, cv2.IMREAD_COLOR)

            if frame is not None:
                try:
                    gray_image = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

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
                            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
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
                            if percentOfHeight > 20:
                                foundProfilePhoto = True
                                #print("found photo")

                            #plt.imshow(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
                            #plt.axis('off')
                            #plt.show()

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
                        print("e")



            return foundProfilePhoto

