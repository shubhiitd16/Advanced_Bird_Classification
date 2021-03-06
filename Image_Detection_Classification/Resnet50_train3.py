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
import random
from keras.applications.resnet50 import preprocess_input

# In[28]:


Birds=pd.read_csv('AllData2.csv')

Classes=pd.read_csv('DataStats2.csv')
ImagePath=Birds['Image Path'].values
Sizes=Birds['Image Size'].str.replace('(','').str.replace(')','').str.split(',').values
Sizes=[[int(float(j)) for j in i] for i in Sizes]
Class=Birds['Bird Class'].values
print('InputForTrain:{}'.format(Birds.shape))
print('OutputForTrain:{}'.format(Class.shape))


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
try:
    model_name=sys.argv[4]
    model=loadModel('Resnet50/pretrained2')
    model.load_weights(model_name)
except:
    model=loadModel('Resnet50/pretrained2')
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
model.compile(optimizer=SGD(lr=0.0001, momentum=0.9), loss='categorical_crossentropy', metrics=['categorical_accuracy'])

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

x_train = preprocess_input(x_train)
x_valid = preprocess_input(x_valid)
x_test = preprocess_input(x_test)



# In[113]:


# trainning process
nb_epoch = int(sys.argv[1])
batch_size = int(sys.argv[2])
print("Epochs: {}".format(nb_epoch),"Batch Size: {}".format(batch_size))
checkpointer = ModelCheckpoint(filepath=sys.argv[3], verbose=1, monitor='val_categorical_accuracy',save_best_only=True)
model.fit_generator(datagen.flow(x_train, y_train, batch_size=batch_size),
                    steps_per_epoch = (x_train.shape[0]/batch_size)+1,
                    epochs=nb_epoch,
                    validation_data = (x_valid, y_valid),
                    callbacks=[checkpointer])

Predictions=model.predict(x_train)
print(Predictions.shape)
Prediction1=np.argmax(Predictions,axis=1)
print(Prediction1.shape)
print(np.sum(Prediction1==encoder.transform(y_train1)))

Predictions=model.predict(x_valid)
print(Predictions.shape)
Prediction2=np.argmax(Predictions,axis=1)
print(Prediction2.shape)
print(np.sum(Prediction2==encoder.transform(y_valid1)))

Predictions=model.predict(x_test)
print(Predictions.shape)
Prediction3=np.argmax(Predictions,axis=1)
print(Prediction3.shape)
print(np.sum(Prediction3==encoder.transform(y_test1)))

np.savez('resnet50_pred2.npz', name1=Prediction1, name2=Prediction2,name3=Prediction3,name4=y_train1,name5=y_valid1,name6=y_test1,name7=encoder.classes_)
