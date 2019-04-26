
# coding: utf-8

# Bird Detection with Open CV

# Source:https://www.pyimagesearch.com/2017/09/11/object-detection-with-deep-learning-and-opencv/

# In[1]:


# import the necessary packages
import numpy as np,pandas as pd
import argparse
import cv2
import glob
import os
import shutil
import warnings
warnings.filterwarnings("ignore")


# In[2]:


print("[INFO] loading datasets...")
Birds=pd.read_csv('AllData.csv')
ImagePaths=Birds['Image Path'].values
Sizes=Birds['Image Size'].str.replace('(','').str.replace(')','').str.split(',').values
Sizes=[[int(float(j)) for j in i] for i in Sizes]
Labels=Birds['Bird Class'].values
Num_Images=ImagePaths.shape[0]
print("[INFO] loading model...")
net = cv2.dnn.readNetFromCaffe("MobileNetSSD_deploy.prototxt.txt" , "MobileNetSSD_deploy.caffemodel" )


# In[13]:


for image_indices in np.array_split(range(Num_Images),(Num_Images/300)+1):
    DetectionStats=pd.DataFrame(columns=['path to original','path to crop','startX', 'startY', 'endX', 'endY','confidence','width','height'])
    Images = [cv2.imread(Path) for Path in ImagePaths[image_indices]]
    images=[cv2.resize(image,(300,300)) for image in Images]
    images=np.stack(images,axis=0)
    blob=cv2.dnn.blobFromImages(images, 0.007843, (300, 300), 127.5)
    blob_shape=blob.shape
    print("{}:{}  Dealing with {} images of sizes {}".format(image_indices[0],image_indices[-1],blob_shape[0],blob.shape[1:]))
    # pass the blob through the network and obtain the detections and
    # predictions
    net.setInput(blob)
    detections = net.forward()
    detections=detections.reshape(detections.shape[2],detections.shape[3])[[detections[0,0,:,1]==3]]
    print("Detected {} birds".format(detections.shape[0]))
    for i in np.arange(0, detections.shape[0]):
        confidence = detections[i, 2]
        ImageIndex=  int(detections[i, 0])
        w=Sizes[ImageIndex][1]    
        h=Sizes[ImageIndex][0] 
        path_to_crop="Cropped/Bird{}_{}.jpg".format(ImageIndex,i)
        path_to_original=ImagePaths[ImageIndex]
        box = detections[i, 3:7] * np.array([w, h, w, h])
        (startX, startY, endX, endY) = box.astype("int")
        DetectionStats.loc[i]=[path_to_original,path_to_crop,startX, startY, endX, endY,confidence,w,h]
        crop_img = Images[ImageIndex][startY:endY, startX:endX,:]
        cv2.imwrite(path_to_crop, crop_img)


# In[14]:


DetectionStats.to_csv("DetectionStats.csv")

