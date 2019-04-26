
# coding: utf-8

# In[1]:


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
from pandas_ml import ConfusionMatrix
import matplotlib.pyplot as plt

# In[28]:


Images=pd.read_csv("DetectionStats.csv")

Classes=pd.read_csv('DataStats.csv')
ImagePath=Images['path to crop']
Sizes=Images[['width','height']]
Class=Images['class']


# In[14]:


def build_ResNet50(input_tensor_shape,output_shape):
    '''
    # reference 
        https://keras.io/applications/#vgg16
        https://www.tensorflow.org/api_docs/python/tf/contrib/keras/applications/ResNet50
    # model defination
        https://github.com/tensorflow/tensorflow/blob/r1.2/tensorflow/contrib/keras/python/keras/applications/resnet50.py
        
    # Arguments
        include_top: whether to include the fully-connected layer at the top of the network.
     
    '''
    base_model = ResNet50(weights='imagenet', include_top=False, input_shape= input_tensor_shape)
    
    x_model = base_model.output
    
    x_model = GlobalAveragePooling2D(name='globalaveragepooling2d')(x_model)
    
    x_model = Dense(1024, activation='relu',name='fc1_Dense')(x_model)
    x_model = Dropout(0.5, name='dropout_1')(x_model)
    
    x_model = Dense(256, activation='relu',name='fc2_Dense')(x_model)
    x_model = Dropout(0.5, name='dropout_2')(x_model)
    predictions = Dense(output_shape, activation='sigmoid',name='output_layer')(x_model)
    
    model = Model(inputs=base_model.input, outputs=predictions)
    
    return model


# In[15]:


def SaveModel(model,Path):
    # serialize model to JSON
    model_json = model.to_json()
    if os.path.isdir(Path):
        shutil.rmtree(Path)
    os.mkdir(Path)
    with open(Path+"/model_architecture.json", "w") as json_file:
        json_file.write(model_json)
    # serialize weights to HDF5
    model.save_weights(Path+"/model_weights.h5")
    print("Saved model to ",Path)

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


# In[16]:


# get model
img_rows, img_cols, img_channel = 224, 224, 3
input_tensor_shape=(img_rows, img_cols, img_channel)
output_shape=Classes.shape[0]
model=loadModel('Resnet50/pretrained')
model.load_weights('ResNet50_weights1.hdf5')

# In[17]:


print("No of layers:",len(model.layers))


# In[18]:


#FreezeLayers
for layer in model.layers[:175]:
        layer.trainable = False
for layer in model.layers[175:]:
    layer.trainable = True


# In[109]:


import cv2
Images = [cv2.imread(Path) for Path in ImagePath]
Images=[image for image in Images if image is not None]
Class=[x for x,y in zip(Class,Images) if y is not None]

print("No of Images: {}".format(len(Images)))

x_test=[cv2.resize(image,(224,224)) for i,image in enumerate(Images) if i%10==0]
x_valid=[cv2.resize(image,(224,224)) for i,image in enumerate(Images) if i%10==1 or i%10==2]
x_train=[cv2.resize(image,(224,224)) for i,image in enumerate(Images) if i%10>2]
x_train=np.stack(x_train,axis=0)
x_valid=np.stack(x_valid,axis=0)
x_test=np.stack(x_test,axis=0)
print("TrainX: ",x_train.shape,"ValidX: ",x_valid.shape,"TestX: ",x_test.shape)
y_test1=[j for i,j in enumerate(Class) if i%10==0]
y_valid1=[j for i,j in enumerate(Class) if i%10==1 or i%10==2]
y_train1=[j for i,j in enumerate(Class) if i%10>2]
print(len(y_train1),len(y_valid1),len(y_test1))


# In[92]:


# compile the model
model.compile(optimizer=SGD(lr=0.0001, momentum=0.9), loss='binary_crossentropy', metrics=['accuracy'])

# set train Generator
datagen = ImageDataGenerator(rotation_range=30,width_shift_range=0.2,height_shift_range=0.2,horizontal_flip=True)
datagen.fit(x_train)


# In[110]:


def onehot(encoded_Y):
    TrainY=np.zeros((encoded_Y.shape[0],encoder.classes_.shape[0]))
    for i in range(encoded_Y.shape[0]):
        TrainY[i,encoded_Y[i]]=1
    return TrainY


# In[111]:


from sklearn import preprocessing
from keras.utils import to_categorical, np_utils
encoder = preprocessing.LabelEncoder()
encoder.fit(Classes['Bird Class'].values)
print(encoder.classes_)
y_train=onehot(encoder.transform(y_train1))
y_valid=onehot(encoder.transform(y_valid1))



# In[113]:


# trainning process
print("Evaluation on Training Dataset")
Predictions=model.predict(x_train)
print(Predictions.shape)
Prediction=np.argmax(Predictions,axis=1)
print(Prediction.shape)
print(np.sum(Prediction==encoder.transform(y_train1)))


cm = ConfusionMatrix(Prediction,encoder.transform(y_train1))
ConfusionMatrix=cm.stats()['cm']
ClassStatistics=cm.stats()['class']
OverallStatistics=cm.stats()['overall']
ClassStatistics.to_csv("trainStatsResnet.csv")
print(OverallStatistics)
print(ConfusionMatrix)


print("Evaluation on Test Dataset")
Predictions=model.predict(x_test)
print(Predictions.shape)
Prediction=np.argmax(Predictions,axis=1)
print(Prediction.shape)
print(np.sum(Prediction==encoder.transform(y_test1)))

cm = ConfusionMatrix(Prediction,encoder.transform(y_test1))
ConfusionMatrix=cm.stats()['cm']
ClassStatistics=cm.stats()['class']
OverallStatistics=cm.stats()['overall']
ClassStatistics.to_csv("testStatsResnet.csv")
print(OverallStatistics)
print(ConfusionMatrix)
