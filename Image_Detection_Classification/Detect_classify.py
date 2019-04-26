# import the necessary packages
import numpy as np,pandas as pd
import argparse
import cv2
import glob
import os
import shutil
import warnings
warnings.filterwarnings("ignore")
import os,sys
import numpy as np
import pandas as pd

from keras.preprocessing import image
from keras.layers import Dense, GlobalAveragePooling2D
from keras.models import Model
from keras.preprocessing.image import ImageDataGenerator
from keras import optimizers
from keras.optimizers import SGD
from keras.callbacks import ModelCheckpoint
from keras.layers import Dropout
# from PIL import ImageFile
from keras.applications.resnet50 import ResNet50
import shutil
from keras.models import model_from_json
import random
from keras.applications.resnet50 import preprocess_input
#ImagePath: list of path to images
# Max batch size=300
#Detection
root='Images'
ImagePaths=os.listdir(root)
Num_Images=len(ImagePaths)

Classes=['Bulbul', 'Collared_dove', 'Common_sparrow', 'Coppersmith', 'Crow',
       'Crow_pheasant', 'Drongo', 'Golden_backed_woodpecker',
       'Green Barbet', 'Hoopoe', 'Indian_hornbill', 'Indian_robin',
       'Jungle_babbler', 'Koel', 'Little_green_beeeater', 'Magpie_robin',
       'Myna', 'Owlet', 'Parakeet', 'Pariah_kite', 'Partridge', 'Peacock',
       'Pied_wagtail', 'Pigeon', 'Pond_heron', 'Red_wattled_lapwing',
       'Rufous_backed_shrike', 'Shikra', 'Sunbird', 'Tailor_bird',
       'Tree_pie', 'White_breasted_kingfisher',
       'White_breasted_water_hen']

print("[INFO] loading model...")
net = cv2.dnn.readNetFromCaffe("Detection/MobileNetSSD_deploy.prototxt.txt" , "Detection/MobileNetSSD_deploy.caffemodel" )
DetectionStats=pd.DataFrame(columns=['path to original','startX', 'startY', 'endX', 'endY','confidence','width','height','predicted_class'])
Images = [cv2.imread(os.path.join(root,Path)) for Path in ImagePaths]
Sizes=[image.shape for image in Images]
images=[cv2.resize(image,(300,300)) for image in Images]
images=np.stack(images,axis=0)
blob=cv2.dnn.blobFromImages(images, 0.007843, (300, 300), 127.5)
blob_shape=blob.shape

print("Number Of Images:{}".format(Num_Images))
# pass the blob through the network and obtain the detections and
# predictions
net.setInput(blob)
print(blob.shape)
detections = net.forward()

detections=detections.reshape(detections.shape[2],detections.shape[3])[[detections[0,0,:,1]==3]]
Cropped=[]

for i in np.arange(0, detections.shape[0]):
    confidence = detections[i, 2]
    if(confidence>0.5):
        ImageIndex=  int(detections[i, 0])
        w=Sizes[ImageIndex][1]
        h=Sizes[ImageIndex][0]
        path_to_original=ImagePaths[ImageIndex]
        box = detections[i, 3:7] * np.array([w, h, w, h])
        (startX, startY, endX, endY) = box.astype("int")
        DetectionStats.loc[i]=[path_to_original,startX, startY, endX, endY,confidence,w,h,None]
        crop_img = Images[ImageIndex][startY:endY, startX:endX,:]
        Cropped+=[crop_img]
print("Detected {} birds".format(len(Cropped)))

#Classification
def loadModel(Path):
    # load json and create model
    json_file = open(Path+'/model_architecture.json', 'r')
    loaded_model_json = json_file.read()
    json_file.close()
    loaded_model = model_from_json(loaded_model_json)
    # load weights into new model
    loaded_model.load_weights(Path+"/model_weights.h5")
    print("Loaded model from disk",Path)
    return loaded_model


ModelPath="Classification/Resnet50"
model=loadModel(ModelPath)
x=[cv2.resize(image,(224,224)) for image in Cropped]
x=np.stack(x,axis=0)

# compile the model
model.compile(optimizer=SGD(lr=0.0001, momentum=0.9), loss='categorical_crossentropy', metrics=['categorical_accuracy'])
x = preprocess_input(x)

Predictions=model.predict(x)
print(Predictions.shape)
Prediction1=np.argmax(Predictions,axis=1)
print(Prediction1)
COLORS=[0.2,0.3,0.4]
i=0
for index, row in DetectionStats.iterrows():
         image=Images[index]
         cv2.rectangle(image, (row['startX'], row['startY']), (row['endX'], row['endY']),
			COLORS, 2)
         y = row['startY'] - 15 if row['startY'] - 15 > 15 else row['startY'] + 15
         cv2.putText(image,Classes[Prediction1[i]]+":"+str(row['confidence']), (row['startX'], y),
			cv2.FONT_HERSHEY_SIMPLEX, 0.5, COLORS, 2)
         cv2.imwrite("something{}.jpg".format(i), image)
         i+=1
