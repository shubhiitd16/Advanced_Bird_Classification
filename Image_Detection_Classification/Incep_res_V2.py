
# coding: utf-8

# In[1]:


import pandas as pd
import os,cv2
import math


# In[2]:


Labels=pd.read_csv('Output.csv')


# In[3]:


TrainX=[cv2.imread(os.path.join('Cropped','crop{}.jpeg'.format(x))) for x in Labels['index'] if x%5<3 ]
ValidX=[cv2.imread(os.path.join('Cropped','crop{}.jpeg'.format(x))) for x in Labels['index'] if x%5==4 ]
TestX=[cv2.imread(os.path.join('Cropped','crop{}.jpeg'.format(x))) for x in Labels['index'] if x%5==3 ]


# In[4]:


Labels=Labels.set_index('index')




# In[5]:


import numpy
TrainX=[cv2.resize(image,(350,350)) for image in TrainX]
TrainX=numpy.stack(TrainX,axis=0)
ValidX=[cv2.resize(image,(350,350)) for image in ValidX]
ValidX=numpy.stack(ValidX,axis=0)
TestX=[cv2.resize(image,(350,350)) for image in TestX]
TestX=numpy.stack(TestX,axis=0)


# In[6]:


TrainY=Labels[Labels.index%5<3]['labels'].values
ValidY=Labels[Labels.index%5==4]['labels'].values
TestY=Labels[Labels.index%5==3]['labels'].values


# In[7]:


print(len(TrainY))
print(len(ValidY))
print(len(TestY))


# In[8]:


import numpy as np
from keras.layers import Conv2D, MaxPooling2D, Dense, Activation, Dropout, Flatten, Input, AveragePooling2D
from keras.optimizers import Adam
from keras.models import Model
from keras.utils import plot_model, np_utils
from keras.callbacks import LearningRateScheduler
from keras.applications.inception_resnet_v2 import InceptionResNetV2
from keras import backend as K
from keras.utils.generic_utils import get_custom_objects


BATCH_SIZE = 32
VALIDATION_SPLIT = 0.1
N_CLASSES = 16
EPOCHS = 7


# Swish Activation Function
def swish(x):
    return (K.sigmoid(x) * x)

get_custom_objects().update({'swish': Activation(swish)})


# Learning Step Decay by 10e-1 after every 4 epochs
def step_decay(epoch):
    initial_lrate = 0.001
    drop = 0.1
    epochs_drop = 4.0
    lrate = initial_lrate * math.pow(drop, math.floor((epoch)/epochs_drop))
    return lrate


# Calculates Precision Accuracy
def precision(y_true, y_pred):
    """Precision metric.
    Computes the precision, a metric for multi-label classification of
    how many selected items are relevant.
    """
    true_positives = K.sum(K.round(K.clip(y_true * y_pred, 0, 1)))
    predicted_positives = K.sum(K.round(K.clip(y_pred, 0, 1)))
    precision = true_positives / (predicted_positives + K.epsilon())
    return precision


# Calculates Recall Accuracy
def recall(y_true, y_pred):
    """Recall metric.
    Computes the recall, a metric for multi-label classification of
    how many relevant items are selected.
    """
    true_positives = K.sum(K.round(K.clip(y_true * y_pred, 0, 1)))
    possible_positives = K.sum(K.round(K.clip(y_true, 0, 1)))
    recall = true_positives / (possible_positives + K.epsilon())
    return recall


# Calculates F1 score
def f1(y_true, y_pred):

    def precision(y_true, y_pred):
        true_positives = K.sum(K.round(K.clip(y_true * y_pred, 0, 1)))
        predicted_positives = K.sum(K.round(K.clip(y_pred, 0, 1)))
        precision = true_positives / (predicted_positives + K.epsilon())
        return precision


    def recall(y_true, y_pred):
        true_positives = K.sum(K.round(K.clip(y_true * y_pred, 0, 1)))
        possible_positives = K.sum(K.round(K.clip(y_true, 0, 1)))
        recall = true_positives / (possible_positives + K.epsilon())
        return recall
    precision = precision(y_true, y_pred)
    recall = recall(y_true, y_pred)
    return (2*((precision*recall)/(precision+recall+K.epsilon())))



# Inception_ResNet_V2 model define
def build_inception_resnet_V2(img_shape=(350, 350, 3), n_classes=4, l2_reg=0.,
                load_pretrained=True, freeze_layers_from='base_model'):
    
    # Decide if load pretrained weights from imagenet
    if load_pretrained:
        weights = 'imagenet'
    else:
        weights = None

    # Get base model
    base_model = InceptionResNetV2(include_top=False, weights=weights,
                             input_tensor=None, input_shape=img_shape)

    # Add final layers
    x = base_model.output
    x = AveragePooling2D((4,4), strides=(4, 4), name='avg_pool')(x)
    x = Flatten(name='flatten')(x)
    x = Dense(512, activation='swish', name='dense_1', kernel_initializer='he_uniform')(x)
    x = Dropout(0.25)(x)
    predictions = Dense(n_classes, activation='softmax', name='predictions', kernel_initializer='he_uniform')(x)

    # This is the model that will  be trained
    model = Model(inputs=base_model.input, outputs=predictions)

    # Freeze some layers
    if freeze_layers_from is not None:
        if freeze_layers_from == 'base_model':
            print ('   Freezing base model layers')
            for layer in base_model.layers:
                layer.trainable = False
        else:
            for i, layer in enumerate(model.layers):
                print(i, layer.name)
            print ('   Freezing from layer 0 to ' + str(freeze_layers_from))
            for layer in model.layers[:freeze_layers_from]:
               layer.trainable = False
            for layer in model.layers[freeze_layers_from:]:
               layer.trainable = True


    # Compiling Model with Adam Optimizer
    adam = Adam(0.0001) 
    model.compile(loss='categorical_crossentropy', optimizer=adam, metrics=[precision, recall, f1])  
    return model 


# In[ ]:


# Learning Rate Schedule
lrate = LearningRateScheduler(step_decay)

# Loading Model
model = build_inception_resnet_V2(load_pretrained=False)

model.load_weights('inception_resnet_V2_original.h5')


# In[ ]:

from sklearn import preprocessing
cat_features = numpy.unique(TrainY)
enc = preprocessing.LabelEncoder()
enc.fit(cat_features)
TrainY=enc.transform(TrainY).reshape(-1,1)
ValidY=enc.transform(ValidY).reshape(-1,1)

from sklearn.preprocessing import OneHotEncoder
enc = OneHotEncoder(handle_unknown='ignore')
enc.fit(TrainY)
TrainY=enc.transform(TrainY)
ValidY=enc.transform(ValidY)

TrainY=TrainY.todense()
ValidY=ValidY.todense()



# In[ ]:


print(model.summary())
print(TrainY.shape)
print(TrainX.shape)


# In[ ]:


history = model.fit(TrainX, TrainY,  epochs=EPOCHS, verbose= 2, 
         steps_per_epoch=TrainX.shape[0]//BATCH_SIZE,
         callbacks = [lrate],
         validation_data=[ValidX,ValidY],
         validation_steps = ValidX.shape[0] // BATCH_SIZE
         )


# In[ ]:


model.save_weights('inception_resnet_V2_final1.h5')

