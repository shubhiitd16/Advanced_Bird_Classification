from bs4 import BeautifulSoup
import requests
import re
import os,sys
def createFolder(directory):
    try:
        if not os.path.exists(directory):
            os.makedirs(directory)
    except OSError:
        print ('Error: Creating directory. ' +  directory)
def downloadFile(url,name):
    r = requests.get(url)
    file = name+'.jpeg';
    with open(file,'wb') as f:
        f.write(r.content)
def urlReader(url):
    reader = 0
    pointer = 2
    for char in url:
        if char == '=' and reader == 1:
            break
        elif char == '=' and reader == 0:
            reader = 1
        else:
            pointer = pointer + 1
    return url[:pointer]

bird = input("Name of Bird: ")
createFolder(bird.capitalize())
host = "http://orientalbirdimages.org"
url = "http://orientalbirdimages.org/search.php?keyword="

req = requests.get(url + bird)
soup = BeautifulSoup(req.text, "lxml")
page_numbers = soup.findAll('td', {"width": "190"})
bird_url = url + bird + ",&query=&page="

result = int(int(re.search(r'\d+', page_numbers[0].text).group())/20) + 2

folder= input("Destination Folder: ")
path = os.getcwd() + '/Data/' + folder
os.chdir(path)

for i in range(1,result):
	nurl = bird_url + str(i)
	req = requests.get(nurl + bird)
	soup = BeautifulSoup(req.text, "lxml")
	pages = soup.findAll('a', href=re.compile('.*Bird_ID*'))
	i = 0
	while (i < len(pages)):
		page = pages[i]
        #createFolder(page.text.replace('/','_'))
        #os.chdir(os.getcwd() + '/' + page.text.replace('/','_'))
		i = i+2
		url = host + "/" + (page.get('href'))[2:]
		req = requests.get(url)
		soup = BeautifulSoup(req.text,"lxml")
		subpages = soup.findAll('option')
		url = urlReader(url)
		count = 1
		for subpage in subpages:
			nurl = url + subpage.get('value')
			req = requests.get(nurl)
			soup = BeautifulSoup(req.text,"lxml")
			ssubpages = soup.findAll('img')
			for ssubpage in ssubpages:
				if(ssubpage.get('src') != "images/top.png"):
					print(ssubpage.get('alt') + "(" + str(count) + ")")
					downloadFile(ssubpage.get('src'),(ssubpage.get('alt').replace('/','_') + "(" + str(count) + ")"))
					count = count + 1
    #os.chdir(path)
