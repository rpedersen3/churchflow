# -*- coding: utf-8 -*-
#import os
#os.environ['TF_CPP_MIN_LOG_LEVEL'] = '1'

#from deepface import DeepFace
import cv2
import dlib
import numpy as np
import matplotlib.pyplot as plt
import urllib.request

print("----------------------------------------------------")
print("represent")

url = "https://www.missionhills.org/wp-content/uploads/2018/04/craig_smith_2018.jpg"
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
response = urllib.request.urlopen(req)
arr = np.asarray(bytearray(response.read()), dtype=np.uint8)
img = cv2.imdecode(arr, -1)  # 'Load it as it is'

#img = cv2.imread("mark.jpg")
print ("shape: ", str(img.shape))

gray_image = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
print ("gray: ", str(gray_image.shape))

detector = dlib.get_frontal_face_detector()
faces = detector(gray_image)

for face in faces:
    x, y, w, h = (face.left(), face.top(), face.width(), face.height())
    cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)

plt.imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
plt.axis('off')
plt.show()

print('faces: ', str(faces))

print("done ---------")
#    face_objs = DeepFace.extract_faces(img_path="tom.jpg", target_size = (224, 224), detector_backend = 'opencv')

print("----------------------------------------------------")
print("detect faces")

