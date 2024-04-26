import cv2
import dlib
import urllib.request
import numpy as np
import matplotlib.pyplot as plt

from clarifai_grpc.channel.clarifai_channel import ClarifaiChannel
from clarifai_grpc.grpc.api import resources_pb2, service_pb2, service_pb2_grpc
from clarifai_grpc.grpc.api.status import status_code_pb2
from clarifai.client.model import Model

# Convert width height to a point in a rectangle
def getRectangle(faceDictionary):
    rect = faceDictionary.face_rectangle
    left = rect.left
    top = rect.top
    bottom = left + rect.height
    right = top + rect.width
    return ((left, top), (bottom, right))

class Photo:
    name = "photo"

    def text(self):

        model_url = (
            "https://clarifai.com/clarifai/main/models/ethnicity-demographics-recognition"
        )
        image_url = "https://www.missionhills.org/wp-content/uploads/2018/04/keith_carson_2018.jpg"

        # The Predict API also accepts data through URL, Filepath & Bytes.
        # Example for predict by filepath:
        # model_prediction = Model(model_url).predict_by_filepath(filepath, input_type="text")

        # Example for predict by bytes:
        # model_prediction = Model(model_url).predict_by_bytes(image_bytes, input_type="text")

        model_prediction = Model(url=model_url, pat="").predict_by_url(
            image_url, input_type="image"
        )

        # Get the output
        print("---------- print output model")
        print(model_prediction.outputs[0].data.text.raw)
        print(model_prediction.outputs)
        print("-------------------------------")

        # Uncomment this line to print the full Response JSON
        # print(output)

        '''
            ageProto="age_deploy.prototxt"
            ageModel="age_net.caffemodel"
            genderProto="gender_deploy.prototxt"
            genderModel="gender_net.caffemodel"
            emoProto ="deploy.prototxt"
            emoModel="EmotiW_VGG_S.caffemodel"
        '''
        '''

        # ------------ Model for Age detection --------#
        age_weights = "age_deploy.prototxt"
        age_config = "age_net.caffemodel"
        age_Net = cv2.dnn.readNet(age_config, age_weights)

        gender_weights = "gender_deploy.prototxt"
        gender_config = "gender_net.caffemodel"
        gender_Net = cv2.dnn.readNet(gender_config, gender_weights)

        emoProto = "deploy.prototxt"
        emoModel = "EmotiW_VGG_S.caffemodel"
        emoNet = cv2.dnn.readNet(emoModel, emoProto)



        # Model requirements for image
        ageList = ['(0-2)', '(4-6)', '(8-12)', '(15-20)',
                   '(25-32)', '(38-43)', '(48-53)', '(60-100)']
        genderList = ['Male', 'Female']
        model_mean = (78.4263377603, 87.7689143744, 114.895847746)


        detector = dlib.get_frontal_face_detector()
        url = "https://www.missionhills.org/wp-content/uploads/2018/04/craig_smith_2018.jpg"

        hdrs = {
            "User-Agent": "XY"
        }


        req = urllib.request.Request(url, headers=hdrs)
        response = urllib.request.urlopen(req)
        arr = np.asarray(bytearray(response.read()), dtype=np.uint8)


        frame = None
        if url.find(".jpg") != -1 or url.find(".jpeg") != -1 or url.find(".jpeg") != -1 or url.find(
                ".ashx") != -1:
            frame = cv2.imdecode(arr, -1)
        if url.find(".png") != -1:
            frame = cv2.imdecode(arr, cv2.IMREAD_COLOR)

        if frame is not None:



            gray_image = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            height, width = gray_image.shape[:2]



            rects = detector(gray_image)

            numberOfFaces = len(rects)
            # print("********* number of faces: ", numberOfFaces)
            if numberOfFaces < 3:
                for rect in rects:

                    x, y, x2, y2, w, h = (
                    rect.left(), rect.top(), rect.right(), rect.bottom(), rect.width(), rect.height())
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

                    print('***************************')
                    print('image width: ', width, ',  image height: ', height)
                    print('face width: ', w, ',  face height: ', h)
                    print('x: ', x, ', ', 'y: ', y)

                    percentOfHeight = (h / height) * 100
                    percentFromTop = (y / height) * 100
                    percentFromBottom = ((height - y2) / height) * 100

                    # print("percentOfHeight: ", percentOfHeight)
                    # print("percentFromTop: ", percentFromTop)
                    # print("percentFromBottom: ", percentFromBottom)

                    # check if face is in middle of picture and is percent of total size
                    # if numberOfFaces == 1 and percentOfHeight > 20 and percentFromTop < 40 and percentFromBottom < 65:
                    #    foundProfilePhoto = True
                    #    print("found photo")
                    if percentOfHeight > 20:

                        plt.imshow(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
                        plt.axis('off')
                        plt.show()

                        face_img = frame[y:y+h, x:x+w].copy()
                        blob = cv2.dnn.blobFromImage(face_img, 1, (227, 227), model_mean, swapRB=False)

                        age_Net.setInput(blob)
                        age_preds = age_Net.forward()
                        age = ageList[age_preds[0].argmax()]
                        i = age_preds[0].argmax()
                        ageConfidence = age_preds[0][i]

                        print('age: ', age, ", confidence: ", ageConfidence)

                        gender_Net.setInput(blob)
                        gender_preds = gender_Net.forward()
                        gender = genderList[gender_preds[0].argmax()]
                        j = gender_preds[0].argmax()
                        genderConfidence = gender_preds[0][j]
                        print('gender: ', gender, ', confidence: ', genderConfidence)
        '''