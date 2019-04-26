
# coding: utf-8

# In[1]:


from keras.preprocessing.image import ImageDataGenerator, array_to_img, img_to_array, load_img
from tqdm import tqdm_notebook, tnrange
import numpy as np
import numpy as np
import cv2
#school's mac is hard to install cv2, you may think abput using PIL
import matplotlib.pyplot as plt
import pickle
import h5py
import glob
import time
from random import shuffle
from collections import Counter

from keras.applications.resnet50 import ResNet50
from keras.preprocessing import image
from keras.applications.resnet50 import preprocess_input, decode_predictions
import numpy as np

from sklearn.model_selection import train_test_split

import keras
from keras.preprocessing.image import ImageDataGenerator
from keras.callbacks import LearningRateScheduler, ModelCheckpoint
from keras.models import Sequential
from keras.layers import Dense, Dropout, Activation, Flatten
from keras.layers import Conv2D, MaxPooling2D
from keras.optimizers import SGD, Adam
from keras.applications.vgg16 import VGG16
from keras.applications.vgg19 import VGG19
from keras.applications.resnet50 import ResNet50
from keras.models import model_from_json
from keras.models import load_model


# In[2]:


# In[3]:


#model = ResNet50(weights='imagenet')
model=load_model("Resnet50ImageNet.h5")

model.layers.pop()


# In[8]:


Train= [np.array(load_img("Frames/Train/image{}.jpg".format(idx),target_size=(224, 224))) / 255 for idx in tqdm_notebook(range(4))]
Valid= [np.array(load_img("Frames/Valid/image{}.jpg".format(idx),target_size=(224, 224))) / 255 for idx in tqdm_notebook(range(2))]
Test= [np.array(load_img("Frames/Test/image{}.jpg".format(idx),target_size=(224, 224))) / 255 for idx in tqdm_notebook(range(7))]

                 


# In[9]:


Train=np.stack(Train,axis=0)
Valid=np.stack(Valid,axis=0)
Test=np.stack(Test,axis=0)


# In[11]:


Train=preprocess_input(Train)
Valid=preprocess_input(Valid)
Test=preprocess_input(Test)


# In[12]:


Trainf=model.predict(Train)
Validf=model.predict(Valid)
Testf=model.predict(Test)


# In[14]:


np.savetxt("Trainf.csv", Trainf, delimiter=",")
np.savetxt("Validf.csv", Validf, delimiter=",")
np.savetxt("Testf.csv", Testf, delimiter=",")

