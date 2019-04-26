#Usage: python app.py
import os
from flask import Flask, render_template, request,jsonify
from werkzeug import secure_filename
from keras.preprocessing.image import load_img, img_to_array
from keras.models import load_model
import numpy as np
import uuid
from keras.models import model_from_json
import base64
import requests,json,tensorflow as tf
from geopy.geocoders import Nominatim
geolocator = Nominatim(user_agent="specify_your_app_name_here")
img_width, img_height = 224, 224
import mysql.connector
mysql = mysql.connector.connect(host = 'localhost', user = 'root', passwd = "advbird123")
mycursor = mysql.cursor()
mycursor.execute("select * from image_database.info")
Data=np.array(mycursor.fetchall())
Coordinates=["{},{}".format(Data[i][2],Data[i][3]) for i in range(Data.shape[0])]
Paths=["/var/www/html/{}".format(Data[i][-2]) for i in range(Data.shape[0])]
Label=[Data[i][-1] for i in range(Data.shape[0])]


UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = set(['jpg', 'jpeg','JPG'])

#Paths=['uploads/det_C199633808570966_aaaf1879a5_z.jpg','uploads/det_6167A4copper.jpeg','uploads/det_C43EECpeacock.jpg','uploads/det_B68E48sample2.jpeg']
#Label=['Parakeet','Coppersmith','Peacock','Pigeon']
#Coordinates=["28.542067,77.194323","28.541934,77.192345","28.542023,77.216743","28.541245,77.217843"]

Data=[[x,y,z] for x,y,z in zip(Paths,Label,Coordinates)]
print(Data)

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

import cv2
model=loadModel('Resnet50/pretrained2')
model.load_weights('v2_105.hdf5')
graph = tf.get_default_graph()


# load our serialized model from disk
print("[INFO] loading model...")
net = cv2.dnn.readNetFromCaffe("Resnet50/Detection/MobileNetSSD_deploy.prototxt.txt" , "Resnet50/Detection/MobileNetSSD_deploy.caffemodel" )

def detect(path,label):
    image=cv2.imread(path)
    (h, w) = image.shape[:2]
    blob = cv2.dnn.blobFromImage(cv2.resize(image, (300, 300)), 0.007843,
	(300, 300), 127.5)
    print("[INFO] computing object detections...")
    net.setInput(blob)
    detections = net.forward()
    for i in np.arange(0, detections.shape[2]):
        	# extract the confidence (i.e., probability) associated with the
        	# prediction
        	confidence = detections[0, 0, i, 2];idx = int(detections[0, 0, i, 1])
        	# filter out weak detections by ensuring the `confidence` is
        	# greater than the minimum confidence
        	if confidence > 0.5 and idx==3:
        		# extract the index of the class label from the `detections`,
        		# then compute the (x, y)-coordinates of the bounding box for
        		# the object
        		
        		box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
        		(startX, startY, endX, endY) = box.astype("int")
         
        		# display the prediction
        		print("[INFO] {}".format(label))
        		cv2.rectangle(image, (startX, startY), (endX, endY),
        			[255,255,0], 2)
        		y = startY - 15 if startY - 15 > 15 else startY + 15
    return image
    
    
def predict(path):
    im=cv2.imread(path)
    im1=cv2.resize(im,(224,224))
    im1=im1.reshape((1,224,224,3))
    print(im1.shape)
    global graph
    with graph.as_default():
        pred=model.predict(im1)
    return Classes[np.argmax(pred,axis=1)][0]

def get_address(coordinates):
    #location = geolocator.reverse("52.509669, 13.376294")
    location = geolocator.reverse(coordinates)
    return location.address

Classes=np.array(['Brahminy_maina', 'Bulbul', 'Collared_dove', 'Common_myna',
       'Common_sparrow', 'Coppersmith', 'Crow_pheasant', 'Drongo',
       'Golden_backed_woodpecker', 'Green Barbet', 'Hoopoe', 'House_Crow',
       'Indian_hornbill', 'Indian_robin', 'Jungle_Crow', 'Jungle_babbler',
       'Koel', 'Little_green_beeeater', 'Magpie_robin', 'Owlet',
       'Parakeet', 'Pariah_kite', 'Partridge', 'Peacock', 'Pied_myna',
       'Pied_wagtail', 'Pigeon', 'Pond_heron', 'Red_wattled_lapwing',
       'Rufous_backed_shrike', 'Shikra', 'Sunbird', 'Tailor_bird',
       'White_breasted_kingfisher', 'White_breasted_water_hen'])

# Load the model


def get_as_base64(url):
    return base64.b64encode(requests.get(url).content)



def my_random_string(string_length=10):
    """Returns a random string of length string_length."""
    random = str(uuid.uuid4()) # Convert UUID format to a Python string.
    random = random.upper() # Make all characters uppercase.
    random = random.replace("-","") # Remove the UUID '-'.
    return random[0:string_length] # Return the random string.

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

app = Flask(__name__)
#simple_geoip = SimpleGeoIP(app)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route("/")
def template_test():
    return render_template('template.html', label='Please Upload the image first', imagesource='../uploads/default.jpeg')

@app.route("/map")
def map1():
    lattitude=28.54209513
    longitude=77.19202354
    margin=0.01
    print("Map working")
    try:
        address=get_address("{},{}".format(lattitude,longitude))
    except:
        address="{},{}".format(lattitude,longitude)
    print("Map Not Working")
    source='uploads/det_7D6875sample2.jpeg'
    Label='Pigeon'
    return render_template('map.html',address=address,source=source,Label=Label,Lat=str(lattitude),Long=str(longitude),Lat1=str(lattitude-margin),Long1=str(longitude-margin),Lat2=str(lattitude+margin),Long2=str(longitude+margin))

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        import time
        start_time = time.time()
        file = request.files['file']
        print("file")
        #lat = request.files['latitude']
        #long = request.files['longitude']
        #print(lat,long)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)

            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            
            
            label = predict(file_path)
            image=detect(file_path,label)
            filename = my_random_string(6) + filename
            cv2.imwrite("uploads/det_"+filename,image)
            os.rename(file_path, os.path.join(app.config['UPLOAD_FOLDER'], filename))
            print("--- %s seconds ---" % str (time.time() - start_time))
            return render_template('template.html', label=label, imagesource='../uploads/det_' + filename)

from flask import send_from_directory

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename)
    
@app.route('/detected')
def detected_file():
    for i in range(len(Data)):
        try:
            Data[i][2]=get_address(Data[i][2])
        except:
            pass
    return render_template('detected.html',rows=Data)

from werkzeug import SharedDataMiddleware
app.add_url_rule('/uploads/<filename>', 'uploaded_file',
                 build_only=True)
app.wsgi_app = SharedDataMiddleware(app.wsgi_app, {
    '/uploads':  app.config['UPLOAD_FOLDER']
})

if __name__ == "__main__":
    app.debug=False
    app.run(host='0.0.0.0', port=3000)
    