
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
from keras.optimizers import SGD,adam
from keras.callbacks import ModelCheckpoint
from keras.layers import Dropout
# from PIL import ImageFile
from keras.applications.resnet50 import ResNet50
import shutil
from keras.models import model_from_json
import random
from keras.applications.resnet50 import preprocess_input

# In[28]:


Images=pd.read_csv("DetectionStats.csv")

Classes=pd.read_csv('DataStats.csv')
ImagePath=Images['path to crop']
Sizes=Images[['width','height']]
Class=Images['class']


# In[14]:


from keras.models import Sequential
from keras.layers import Dense, Conv2D, Flatten
#create model
model = Sequential()
#add model layers
model.add(Conv2D(64, kernel_size=3, activation=’relu’, input_shape=(224,224,3)))
model.add(Conv2D(64, kernel_size=3, activation=’relu’))
model.add(Conv2D(32, kernel_size=3, activation=’relu’))
model.add(Conv2D(32, kernel_size=3, activation=’relu’))
model.add(Flatten())
model.add(Dense(33, activation=’softmax’))


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

def shuffle(x,y):
    n=x.shape[0]
    x_s=x.shape
    y_s=y.shape
    order= random.shuffle(list(range(n)))
    x=x[order]
    y=y[order]
    return x.reshape(x_s),y.reshape(y_s)


# In[16]:


# get model
img_rows, img_cols, img_channel = 224, 224, 3
input_tensor_shape=(img_rows, img_cols, img_channel)
output_shape=Classes.shape[0]



# In[17]:


print("No of layers:",len(model.layers))


# In[18]:



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
shape_t=x_train.shape
shape_v=x_valid.shape
shape_te=x_test.shape
print("TrainX: ",x_train.shape,"ValidX: ",x_valid.shape,"TestX: ",x_test.shape)
y_test1=[j for i,j in enumerate(Class) if i%10==0]
y_valid1=[j for i,j in enumerate(Class) if i%10==1 or i%10==2]
y_train1=[j for i,j in enumerate(Class) if i%10>2]
print(len(y_train1),len(y_valid1),len(y_test1))




# In[92]:


# compile the model
model.compile(optimizer=adam(lr=0.0001), loss='categorical_crossentropy', metrics=['categorical_accuracy'])

# set train Generator
datagen =ImageDataGenerator(
                            rotation_range=10,
                            width_shift_range=.05,
                            height_shift_range=.05,
                            shear_range=0.05,
                            zoom_range=0.05,
                            horizontal_flip=True,
                            vertical_flip=False,
                            )

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
y_test=onehot(encoder.transform(y_test1))

print(np.sum(np.argmax(y_train,axis=1)==encoder.transform(y_train1)))
print(np.sum(np.argmax(y_valid,axis=1)==encoder.transform(y_valid1)))
print(np.sum(np.argmax(y_test,axis=1)==encoder.transform(y_test1)))


x_train,y_train=shuffle(x_train,y_train)
x_valid,y_valid=shuffle(x_valid,y_valid)
x_test,y_test=shuffle(x_test,y_test)



# In[113]:


# trainning process
nb_epoch = int(sys.argv[1])
batch_size = int(sys.argv[2])
print("Epochs: {}".format(nb_epoch),"Batch Size: {}".format(batch_size))
checkpointer = ModelCheckpoint(filepath= './ResNet50_weights1.hdf5', verbose=1, monitor='val_acc',save_best_only=True)
model.fit_generator(datagen.flow(x_train, y_train, batch_size=batch_size),
                    steps_per_epoch = (x_train.shape[0]/batch_size)+1,
                    epochs=nb_epoch,
                    validation_data = (x_valid, y_valid),
                    callbacks=[checkpointer])

Predictions=model.predict(x_train)
print(Predictions.shape)
Prediction=np.argmax(Predictions,axis=1)
print(Prediction.shape)
print(np.sum(Prediction==encoder.transform(y_train1)))

Predictions=model.predict(x_valid)
print(Predictions.shape)
Prediction=np.argmax(Predictions,axis=1)
print(Prediction.shape)
print(np.sum(Prediction==encoder.transform(y_valid1)))

Predictions=model.predict(x_test)
print(Predictions.shape)
Prediction=np.argmax(Predictions,axis=1)
print(Prediction.shape)
print(np.sum(Prediction==encoder.transform(y_test1)))
