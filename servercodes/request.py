import requests
import sys
API_ENDPOINT = "http://10.17.10.77:3000/predict/"
file = sys.argv[1]
path = API_ENDPOINT + file
r = requests.get(url  = path)

prediction = r.text

print(prediction)
