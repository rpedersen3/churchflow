import re

import nltk
import pandas as pd
from ethnicolr import census_ln, pred_census_ln, census_ln, pred_wiki_ln

from deepface import DeepFace
import matplotlib.pyplot as plt

nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')
nltk.download('maxent_ne_chunker')
nltk.download('words')
nltk.download('stopwords')


from quotesbot.profilecheck import ProfileCheck


from clarifai.client.model import Model






class UpdatePersonInfo:

    key = ""

    firstnames_file_path = 'firstnames.csv'
    df = pd.read_csv(firstnames_file_path, sep=';')
    df['name_lower'] = df['name'].str.lower()

    def getNameParts(self, name):

        parts = name.split()

        if len(parts) > 1:

            firstName = parts[0]
            lastName = parts[1]

        return firstName, lastName



    def checkInvalidPartsFromNameText(self, txt):

        valid = True

        # grab first two words that sound like real names
        parts = txt.split()

        skipNextPart = False
        for part in parts:

            part = part.replace(".", "")
            part = part.replace(",", "")
            part = part.strip()
            if (len(part) < 2):
                continue

            if part == "is" or \
                part == "his" or \
                part == "wife" or \
                part == "on" or \
                part == "with" or \
                part == "mountain" or \
                part == "states" or \
                part == "forward" or \
                part == "world" or \
                part == "which" or \
                part == "not" or \
                part == "what" or \
                part == "do" or \
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
                part == "info" or \
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
                part == "learn" or \
                part == "more" or \
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

                # print("break on part: ", part)
                valid = False

            # check for bad characters
            pattern = re.compile(r'[^a-zA-Z\s]')  # Matches any character that is not a letter or whitespace

            # Use the search method to check if the string contains any non-character characters
            match = pattern.search(part)
            if match:
                # print("break on non visible character: ", part)
                valid = False

        return valid



    def removeNonNamePartsFromText(self, txt):

        #  replace the name beginning with
        txt = txt.lower()
        if txt.startswith("the "):
            txt = txt.replace("the ", "")

        txt = txt.replace("&", "and")

        # remove some common titles in front of name
        stopwords = ["fr.",
                    "dr.",
                    "rev.",
                    "deacon",
                    "associate",
                    "board",
                    "reverend",
                    "staff",
                    "africa",
                    "asia",
                    "takes",
                    "father",
                    "teach",
                    "agenda",
                    "weekend",
                    "council",
                    "members",
                    "creed",
                    "nicene",
                    "evangelist",
                    "ministerial",
                    "minister",
                    "read more",
                    "suffragan",
                    "zion",
                    "lady",
                    "sister",
                    "brother",
                    "worship",
                    "arts",
                    "women",
                    "bible",
                    "adult",
                    "music",
                    "player",
                    "welcome",
                    "about",
                    "home",
                    "clergy",
                    "student",
                    "elder",
                    "community",
                    "care ",
                    "ministries ",
                    "center",
                    "select",
                    "pastoral",
                    "pastor",
                    "founder",
                    "standard",
                    "celebration",
                    "administrator",
                    "senior",
                    "peace",
                    "street",
                    "together",
                    "gathering",
                    "building",
                    "bookkeeper",
                    "trusting",
                    "benefited",
                    "raised",
                    "business",
                    "personally",
                    "event",
                    "registration",
                    "social",
                    "scheduler",
                    "sermons",
                    "feature",
                    "programs",
                    "prayer",
                    "reuests",
                    "groups",
                    "ministry",
                    "early",
                    "learning",
                    "pathways",
                    "connected",
                    "apostle",
                    "church",
                    "emeritus",
                    "school",
                    "volunteers",
                    "growth",
                    "director",
                    "coordinator",
                    "office",
                    "campus",
                    "lead",
                    "strategic",
                    "associate",
                    "contact",
                    "team",
                    "evangelist",
                    "first",
                    "lady",
                    "lay "]


        querywords = txt.split()

        resultwords = [word for word in querywords if word.lower() not in stopwords]
        txt = ' '.join(resultwords)

        return txt

    def extractRaceFromPhoto(self, url):

        age = None
        gender = None
        race = None
        racePercent = None

        # first check to verify just one face in photo and good size photo
        profileCheck = ProfileCheck()
        foundPhoto, foundProfilePhoto = profileCheck.isProfilePhoto(url, 1, 20)

        if foundProfilePhoto == True:

            try:

                objs = DeepFace.analyze(
                    img_path=url,
                    actions=['age', 'gender', 'race'],
                )

                if len(objs) > 0:

                    firstFace = objs[0]

                    confidence = firstFace["face_confidence"]
                    age = firstFace["age"]
                    gender = firstFace["dominant_gender"]
                    race = firstFace["dominant_race"]
                    racePercent = firstFace["race"][race] / 100.0

                    print("done: ", age, ", ", gender, ", ", race)



                '''
                # now determine race of person in picture
                model_url = (
                    "https://clarifai.com/clarifai/main/models/ethnicity-demographics-recognition"
                )
                image_url = url

                model_prediction = Model(url=model_url, pat=self.key).predict_by_url(
                    image_url, input_type="image"
                )

                if len(model_prediction.outputs[0].data.concepts):
                    first = model_prediction.outputs[0].data.concepts[0]
                    racePercent = first.value
                    if racePercent > 0.5:

                        race = first.name.lower()

                        if race == 'latino_hispanic':
                            race = 'hispanic'
                        if race == 'api':
                            race = 'asian'

                        racePercent = first.value
                '''


            except Exception as e:
                print("get race err: ", e)

        # Get the output
        return race, racePercent, age, gender

    def extractNameFromText(self, text):



        firstname = None
        lastname = None

        race = None
        racePercent = None

        text = self.removeNonNamePartsFromText(text)
        checkValidity = self.checkInvalidPartsFromNameText(text)



        if checkValidity == True:

            print("check name: ", text)

            parts = text.split()

            # if find two first names like "joe and sue jones" then skip second first name
            skipNextPart = False

            for part in parts:

                # print("part: ", part)
                if part.lower() != "and" and skipNextPart == False:

                    print("part: ", part)

                    if firstname is None:

                        # see if firstname is valid name
                        # print("part: ", part)

                        # check firstname against known names
                        names = [{'name': part}]
                        df = pd.DataFrame(names)
                        predictions = census_ln(df, 'name')

                        #print("firstname predictions: ", predictions)

                        # check that firstname is a valid name by checking if any return value is not 'nan'
                        pctwhite = predictions['pctwhite'].iloc[0]
                        pctblack = predictions['pctblack'].iloc[0]
                        pctapi = predictions['pctapi'].iloc[0]
                        pctaian = predictions['pctaian'].iloc[0]
                        pct2prace = predictions['pct2prace'].iloc[0]
                        pcthispanic = predictions['pcthispanic'].iloc[0]



                        # check that lastname is a valid name
                        if str(pctwhite) != 'nan':
                            #print("valid firstname: ", part)
                            firstname = part
                        else:
                            # check in first names file for name
                            result = self.df[self.df['name_lower'] == part]
                            if not result.empty:
                                firstname = part
                            else:
                                print(">>>>>>> bad firstname: ", part)


                    else:  # looking for lastname

                        # firstname is repeated, sometimes happens then just ignor it
                        if part == firstname:
                            continue

                        # check lastname against known names
                        names = [{'name': part}]
                        df = pd.DataFrame(names)
                        predictions = census_ln(df, 'name')

                        #print("lastname: ", part)
                        #print("lastname predictions: ", predictions)

                        pctwhite = predictions['pctwhite'].iloc[0]
                        pctblack = predictions['pctblack'].iloc[0]
                        pctapi = predictions['pctapi'].iloc[0]
                        pctaian = predictions['pctaian'].iloc[0]
                        pct2prace = predictions['pct2prace'].iloc[0]
                        pcthispanic = predictions['pcthispanic'].iloc[0]

                        # check that lastname is a valid name by checking if any return value is not 'nan'
                        if str(pctwhite) != 'nan':
                            print("valid lastname: ", part)
                            lastname = part
                        else:
                            print("=========== bad lastname: ", part)


                    # adjust for two people like Jane and Joe Smith => Jane Smith
                    if skipNextPart:
                        skipNextPart = False

                    if part.lower() == "and":
                        skipNextPart = True

                    if firstname != None and lastname != None:

                        fullname = firstname + " " + lastname

                        names = [{'name': lastname}]
                        df = pd.DataFrame(names)
                        lastnamePred = pred_census_ln(df, 'name')
                        race = lastnamePred['race'].iloc[0]
                        racePercent = lastnamePred[race].iloc[0]

                        print("return found name")
                        return fullname, firstname, lastname, race, racePercent



        return None, None, None, None, None

    def updateContactInfo(self, church):

        updated = False

        photoCount = 0
        if "contacts" in church:

            for contact in church["contacts"]:

                # if not processed contact and valid name
                if "name" in contact:

                    name = contact["name"]
                    fullname, firstname, lastname, nameRace, nameRacePercent = self.extractNameFromText(name)
                    print("*********** name", fullname, ", ", nameRace, ", ", nameRacePercent)

                    if fullname != None:

                        updated = True

                        if "valid" not in contact:
                            contact["valid"] = "yes"


                        # set race based on name if high confidence
                        if "race" not in contact and nameRacePercent > .90:
                            print("*********** name race", nameRace, ", ", str(nameRacePercent))
                            contact["race"] = nameRace

                        # set race to unknown if not defined
                        if "race" not in contact:
                            contact["race"] = "unknown"


                        # set age, gender, race based on image if moderate confidence
                        if photoCount < 5 and "photo" in contact:

                            photoCount = photoCount + 1

                            if "probRace" not in "contact":

                                url = contact["photo"]
                                photoRace, photoRacePercent, photoAge, photoGender = self.extractRaceFromPhoto(url)

                                if photoRace != None and photoRacePercent > 0.5:
                                    print("*********** photo race: ", photoRace, ", ", str(photoRacePercent))
                                    contact["probRace"] = photoRace
                                    contact["probAge"] = str(photoAge)
                                    contact["probGender"] = photoGender

                                else:
                                    contact["probRace"] = "unknown"
                                    contact["probAge"] = "unknown"
                                    contact["probGender"] = "unknown"
                        '''

                    else:
                        updated = True
                        contact["valid"] = "no"

        return updated