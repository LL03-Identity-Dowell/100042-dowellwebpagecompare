
# A very simple Flask Hello World app for you to get started with...


from flask import Flask,make_response,request,render_template,Response,redirect
import base64
import glob
import os.path
import os,re
import cv2
import numpy as np
import imutils
import csv

import qrcode
from PIL import Image
import json
import requests
# from datetime import datetime
# import random
from datetime import datetime
from pymongo import MongoClient
import gridfs
import ssl
import certifi
from pexels_api import API
from mega import Mega



import pyqrcode

from django.views.decorators.clickjacking import xframe_options_exempt

dowellclock_url = "https://100009.pythonanywhere.com/dowellclock"


is_scheduled = False
schedule = ""
respid_main_count = 100000
dd=datetime.now()
time=dd.strftime("%d:%m:%Y,%H:%M:%S")
event_id_url="https://100003.pythonanywhere.com/event_creation"
data={"platformcode":"FB" ,"citycode":"101","daycode":"0",
                "dbcode":"pfm" ,"ip_address":"192.168.0.41",
                "login_id":"lav","session_id":"new",
                "processcode":"1","regional_time":time,
                "dowell_time":time,"location":"22446576",
                "objectcode":"1","instancecode":"100051","context":"afdafa ",
                "document_id":"3004","rules":"some rules","status":"work"
                }


event_id_resp=requests.post(event_id_url,json=data)
event_id = event_id_resp.text






#create instance of mega
mega = Mega()

email = "nitesh@dowellresearch.in"
password = "RstuKnA*u9"


m = mega.login(email,password)
#login using temporary anonymous account
#m = mega.login()
folder = m.find('social_media_images')


global PEXELS_API_KEY

PEXELS_API_KEY='563492ad6f91700001000001e4bcde2e91f84c9b91cffabb3cf20c65'

present_dir=os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__)

connection = MongoClient("mongodb+srv://qruser:qr_12345@cluster0.n2ih9.mongodb.net/DB_IMAGE?retryWrites=true&w=majority",ssl_cert_reqs=ssl.CERT_REQUIRED, ssl_ca_certs=certifi.where())

database = connection['client_data']

collection =database.socialmedia_form
#database = connection['web_image_write']
fs = gridfs.GridFS(database)
i=0
c=fs.find()
print("{}".format(c))
print(type(c))
for f in c:
    i=i+1
    print(f.filename)
print(i)
x=fs.find()
print(x)


class ColorDescriptor:
	def __init__(self, bins):
		# store the number of bins for the 3D histogram
		self.bins = bins
	def describe(self, image):
		# convert the image to the HSV color space and initialize
		# the features used to quantify the image
		#print("this is describe function")
		image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
		features = []
		# grab the dimensions and compute the center of the image
		(h, w) = image.shape[:2]
		(cX, cY) = (int(w * 0.5), int(h * 0.5))
				# divide the image into four rectangles/segments (top-left,
		# top-right, bottom-right, bottom-left)
		segments = [(0, cX, 0, cY), (cX, w, 0, cY), (cX, w, cY, h),(0, cX, cY, h)]
		# construct an elliptical mask representing the center of the
		# image
		(axesX, axesY) = (int(w * 0.75) // 2, int(h * 0.75) // 2)
		ellipMask = np.zeros(image.shape[:2], dtype = "uint8")
		cv2.ellipse(ellipMask, (cX, cY), (axesX, axesY), 0, 0, 360, 255, -1)
		# loop over the segments
		for (startX, endX, startY, endY) in segments:
			# construct a mask for each corner of the image, subtracting
			# the elliptical center from it
			cornerMask = np.zeros(image.shape[:2], dtype = "uint8")
			cv2.rectangle(cornerMask, (startX, startY), (endX, endY), 255, -1)
			cornerMask = cv2.subtract(cornerMask, ellipMask)
			# extract a color histogram from the image, then update the
			# feature vector
			hist = self.histogram(image, cornerMask)
			features.extend(hist)
		# extract a color histogram from the elliptical region and
		# update the feature vector
		hist = self.histogram(image, ellipMask)
		features.extend(hist)
		# return the feature vector
		return features

	def histogram(self, image, mask):
		# extract a 3D color histogram from the masked region of the
		# image, using the supplied number of bins per channel
 		#print("this is  histogrm class")
		hist = cv2.calcHist([image], [0, 1, 2], mask, self.bins,
			[0, 180, 0, 256, 0, 256])
		# normalize the histogram if we are using OpenCV 2.4
		if imutils.is_cv2():
			hist = cv2.normalize(hist).flatten()
		# otherwise handle for OpenCV 3+
		else:
			hist = cv2.normalize(hist, hist).flatten()
		# return the histogram
		return hist


# searcher algorithm


class Searcher:
	def __init__(self, indexPath):
		# store our index path
		self.indexPath = indexPath
	def search(self, queryFeatures, limit = 30):
		# initialize our dictionary of results
		results = {}
		print("this is searcher function")
				# open the index file for reading
		with open(self.indexPath) as f:
			# initialize the CSV reader
			reader = csv.reader(f)
			# loop over the rows in the index
			for row in reader:
				# parse out the image ID and features, then compute the
				# chi-squared distance between the features in our index
				# and our query features
				features = [float(x) for x in row[1:]]
				d = self.chi2_distance(features, queryFeatures)
				# now that we have the distance between the two feature
				# vectors, we can udpate the results dictionary -- the
				# key is the current image ID in the index and the
				# value is the distance we just computed, representing
				# how 'similar' the image in the index is to our query
				results[row[0]] = d
			# close the reader
			f.close()
		# sort our results, so that the smaller distances (i.e. the
		# more relevant images are at the front of the list)
		results = sorted([(v, k) for (k, v) in results.items()])
		# return our (limited) results
		return results
		#return results



	def chi2_distance(self, histA, histB, eps = 1e-10):
		# compute the chi-squared distance
		d = 0.5 * np.sum([((a - b) ** 2) / (a + b + eps)
			for (a, b) in zip(histA, histB)])
		# return the chi-squared distance
		return d



@app.route("/camera",methods=['POST','GET'])
def index():
    if request.method == "GET":

        return render_template("webcam.html")

    elif request.method == "POST":

        file = request.files['image']
        query_path=os.path.join(present_dir,'static/Capture')
        query_path1=os.path.join(present_dir,'static/dataset1')
        file_name="myimage.jpg"
        file_path_name=os.path.join(query_path,file.filename)
        file_path_name1=os.path.join(query_path1,file_name)
        #file.save(file_path_name)
        img=Image.open(file.stream)    #PIL Image
        uploaded_img_path =file_path_name +".png"
        img.save(uploaded_img_path)
        file1 = request.files['image']
        img1=Image.open(file1.stream)
        uploaded_img_path1 =file_path_name1
        #uploaded_img_path = query_path + datetime.now().isoformat.replace(":",".") + "_" +file1.filename +".png"
        img1.save(uploaded_img_path1)

        # with open('e2.txt', 'w') as f:
        #     f.write(x)

        return make_response(uploaded_img_path1)






@app.route('/seo',methods=['POST','GET'])
def seo():
    if request.method == 'POST':

        fs = gridfs.GridFS(database)
        cursor=fs.find()
        file = request.files['query_img']
        query_path=os.path.join(present_dir,'static/Query')
        file.save(os.path.join(query_path,file.filename))
        query_image=(os.path.join(query_path,file.filename))
        imagename=os.path.join('static/Query',file.filename)
        rcvdimg=file.filename



        cd = ColorDescriptor((8, 12, 3))
        temp_path=os.path.join(present_dir,"static/results")
        for root,dirs,files in os.walk(temp_path):
            for file in files:
                os.remove(os.path.join(root,file))
        output1 = open("index1.csv", "w")
        i=0
        for record in cursor:    #for jpg images
        # 	#print(imagePath)
          	image_bytes=record.read()
          	temp="tempot.jpg"
          	#databasedir=os.path.join(present_dir,'static/dataset1')
          	temp_path=os.path.join(present_dir,temp)
          	with open(temp_path,"wb") as binary_file:
          	    binary_file.write(image_bytes)
          	imageID=record.filename
          	file_size=os.path.getsize(temp_path)
          	#image = cv2.imread(temp_path)
          	if file_size!=0:
          	    #temp="tempot.jpg"
          	    image = cv2.imread(temp_path)
          	    features = cd.describe(image)
          	    features = [str(f) for f in features]
          	    output1.write("%s,%s\n" % (imageID, ",".join(features)))
        # # close the index file
        output1.close()
        cd = ColorDescriptor((8, 12, 3))

        query = cv2.imread(query_image)
        features = cd.describe(query)
        # perform the search
        searcher = Searcher("index1.csv")
        results = searcher.search(features)
        print("filtered image paths from data bases are")
        #print(scores)

        seo_filter=[]
        filter_image=[]
        cursor=fs.find()
        for (score, resultID) in results:
        # 	# load the result image and display it

              filter_image=filter_image+[resultID]
              result =os.path.join('static/results',resultID)
              seo_filter=seo_filter+[(score,result)]

        limit=15
        filter_image=filter_image[:limit]

        seo_filter=seo_filter[:limit]

        i=0
        for x in cursor:
            if x.filename in filter_image:

                image_bytes=x.read()
                temp=str(i)+".jpg"
                temp_path=os.path.join(present_dir,"static/results")
                temp_path=os.path.join(temp_path,x.filename)
                with open(temp_path,"wb") as binary_file:
                    binary_file.write(image_bytes)
                i=i+1
        x=datetime.now().isoformat().replace(":","-")

        input_image=rcvdimg+x
        # with open(query_image,'rb') as f:
        #     contents=f.read()
        # fs.put(contents,filename=input_image)
        if seo_filter[0][0] < 1 :
            message="already uploaded, please give different image"
            return render_template('index1.html',message=str(message),query_path=imagename,scores=seo_filter)
            #return make_response("already uploaded, please give different image")

        else :
            with open(query_image,'rb') as f:
                contents=f.read()
            fs.put(contents,filename=input_image)
            message1="Given image is not present in database , Sucessfully saved the image to database"
            return render_template('index1.html',message=str(message1),query_path=imagename,scores=seo_filter)

        #return render_template('index.html',query_path=imagename,scores=seo_filter)
        #return make_response('matching images are {}'.format(filter_image))
    else :
        return render_template('index.html')
        #b=os.path.join(present_dir,'index.html')



@app.route('/show')
def show():
        query_path=os.path.join(present_dir,'static/Capture')
        query_image=(os.path.join(query_path,'myimage.png'))
        imagename=os.path.join('static/Capture','myimage.png')


        cursor=fs.find()
        cd = ColorDescriptor((8, 12, 3))
        temp_path=os.path.join(present_dir,"static/results")
        for root,dirs,files in os.walk(temp_path):
            for file in files:
                os.remove(os.path.join(root,file))
        output1 = open("index1.csv", "w")
        i=0
        for record in cursor:    #for jpg images
        # 	#print(imagePath)
          	image_bytes=record.read()
          	temp="tempot.jpg"
          	#databasedir=os.path.join(present_dir,'static/dataset1')
          	temp_path=os.path.join(present_dir,temp)
          	with open(temp_path,"wb") as binary_file:
          	    binary_file.write(image_bytes)
          	imageID=record.filename
          	file_size=os.path.getsize(temp_path)
          	#image = cv2.imread(temp_path)
          	if file_size!=0:
          	    #temp="tempot.jpg"
          	    image = cv2.imread(temp_path)
          	    features = cd.describe(image)
          	    features = [str(f) for f in features]
          	    output1.write("%s,%s\n" % (imageID, ",".join(features)))
        # # close the index file
        output1.close()
        cd = ColorDescriptor((8, 12, 3))

        query = cv2.imread(query_image)
        features = cd.describe(query)
        # perform the search
        searcher = Searcher("index1.csv")
        results = searcher.search(features)
        print("filtered image paths from data bases are")
        #print(scores)

        seo_filter=[]
        filter_image=[]
        cursor=fs.find()
        for (score, resultID) in results:
        # 	# load the result image and display it

              filter_image=filter_image+[resultID]
              result =os.path.join('static/results',resultID)
              seo_filter=seo_filter+[(score,result)]

        limit=15
        filter_image=filter_image[:limit]

        seo_filter=seo_filter[:limit]

        i=0
        for x in cursor:
            if x.filename in filter_image:

                image_bytes=x.read()
                temp=str(i)+".jpg"
                temp_path=os.path.join(present_dir,"static/results")
                temp_path=os.path.join(temp_path,x.filename)
                with open(temp_path,"wb") as binary_file:
                    binary_file.write(image_bytes)
                i=i+1
        x=datetime.now().isoformat().replace(":","-")
        input_image="cameraimg"+x+".jpg"
        # with open(query_image,'rb') as f:
        #     contents=f.read()
        # fs.put(contents,filename=input_image)

        if seo_filter[0][0] < 1 :
            message="already uploaded, please give different image"
            return render_template('index1.html',message=str(message),query_path=imagename,scores=seo_filter)
            #return make_response("already uploaded, please give different image")

        else :
            with open(query_image,'rb') as f:
                contents=f.read()
            fs.put(contents,filename=input_image)
            message1="Given image is not present in database , Sucessfully saved the image to database"
            return render_template('index1.html',message=str(message1),query_path=imagename,scores=seo_filter)
            #return make_response("Given image is not present in database , Sucessfully saved the image to database")

        #return render_template('index.html',query_path=imagename,scores=seo_filter)

        #return render_template('index.html',query_path=imagename,scores = seo_filter)




@app.route('/similar_images_in_db',methods=['POST','GET'])
def similar_images_in_db():
    if request.method == 'POST':

        fs = gridfs.GridFS(database)
        cursor=fs.find()
        file = request.files['query_img']
        query_path=os.path.join(present_dir,'static/Query')
        file.save(os.path.join(query_path,file.filename))
        query_image=(os.path.join(query_path,file.filename))
        imagename=os.path.join('static/Query',file.filename)
        rcvdimg=file.filename



        cd = ColorDescriptor((8, 12, 3))
        temp_path=os.path.join(present_dir,"static/results")
        for root,dirs,files in os.walk(temp_path):
            for file in files:
                os.remove(os.path.join(root,file))
        # output1 = open("index1.csv", "w")
        i=0
        # for record in cursor:    #for jpg images
        # # 	#print(imagePath)
        #   	image_bytes=record.read()
        #   	temp="tempot.jpg"
        #   	#databasedir=os.path.join(present_dir,'static/dataset1')
        #   	temp_path=os.path.join(present_dir,temp)
        #   	with open(temp_path,"wb") as binary_file:
        #   	    binary_file.write(image_bytes)
        #   	imageID=record.filename
        #   	file_size=os.path.getsize(temp_path)
        #   	#image = cv2.imread(temp_path)
        #   	if file_size!=0:
        #   	    #temp="tempot.jpg"
        #   	    image = cv2.imread(temp_path)
        #   	    features = cd.describe(image)
        #   	    features = [str(f) for f in features]
        #   	    output1.write("%s,%s\n" % (imageID, ",".join(features)))
        # # # close the index file
        # output1.close()
        cd = ColorDescriptor((8, 12, 3))

        query = cv2.imread(query_image)
        features = cd.describe(query)
        # perform the search
        searcher = Searcher("index1.csv")
        results = searcher.search(features)
        print("filtered image paths from data bases are")
        #print(scores)

        seo_filter=[]
        filter_image=[]
        cursor=fs.find()
        for (score, resultID) in results:
        # 	# load the result image and display it

              filter_image=filter_image+[resultID]
              result =os.path.join('static/results',resultID)
              seo_filter=seo_filter+[(score,result)]

        limit=15
        filter_image=filter_image[:limit]

        seo_filter=seo_filter[:limit]

        i=0
        for x in cursor:
            if x.filename in filter_image:

                image_bytes=x.read()
                temp=str(i)+".jpg"
                temp_path=os.path.join(present_dir,"static/results")
                temp_path=os.path.join(temp_path,x.filename)
                with open(temp_path,"wb") as binary_file:
                    binary_file.write(image_bytes)
                i=i+1
        x=datetime.now().isoformat().replace(":","-")

        input_image=rcvdimg+x
        # with open(query_image,'rb') as f:
        #     contents=f.read()
        # fs.put(contents,filename=input_image)
        if seo_filter[0][0] < 1 :
            message="already uploaded, please give different image"
            #return render_template('index1.html',message=str(message),query_path=imagename,scores=seo_filter)
            return make_response("The similar image is already present in database")

        else :
            with open(query_image,'rb') as f:
                contents=f.read()
            fs.put(contents,filename=input_image)
            message1="Given image is not present in database , Sucessfully saved the image to database"
            #return render_template('index1.html',message=str(message1),query_path=imagename,scores=seo_filter)
            return make_response("Given image is not present in database ,sucessfully stored the image in database")

        #return render_template('index.html',query_path=imagename,scores=seo_filter)
        #return make_response('matching images are {}'.format(filter_image))
    else :
        return make_response("image not recieved")
        #return render_template('index.html')
        #b=os.path.join(present_dir,'index.html')


@app.route('/testt')
def hello_world1():
    x=fs.find()
    c=[(f.filename)for f in x]

    return make_response("hlo{}".format(c))



@xframe_options_exempt

@app.route('/final',methods=["POST","GET"])

def form():
    if request.method == "GET":
        return render_template("form1.html")

    elif request.method == "POST":
        email=request.values.get("email")
        brand=request.values.get("brand")
        channel=request.values.get("channel")
        channelbrand=request.values.get("channelbrand")
        Topico=request.values.get("Topico")
        Topic=request.values.get("Topic")
        Topic_description=request.values.get("Topic_description")
        content=request.values.get("content")
        camera=request.values.get("camera")
        contentform=request.values.get("contentform")
        selected_article=request.values.get("selected_article")
        group1=request.values.get("group1")
        group2=request.values.get("group2")
        group3=request.values.get("group3")
        group4=request.values.get("group4")
        group5=request.values.get("group5")
        imagelink=request.values.get("imagelink")
        imagelink_path=os.path.join(present_dir,'static/imagelink')
        try :
            if not os.path.isdir(imagelink_path):
                os.makedirs(imagelink_path)
            image_response=requests.get(imagelink,stream=True)
            image_content=image_response.content
            for root,dirs,files in os.walk(imagelink_path):
                for file in files:
                    os.remove(os.path.join(root,file))
            filename=os.path.join(imagelink_path,"pexels_image.jpg")
            with open(filename,"wb") as f:
                f.write(image_content)
        except Exception as e:
            imagelink=None

        try :
            file = request.files['query_img']
        except Exception as e:
            file = None

        if email == None :
            return render_template("form1.html")

        else :
            if brand == None or channel == None or Topico==None:
                return render_template("form2.html",email=email)
            else :
                if brand == None or channel == None or Topico==None or contentform == None :
                    article=[]
                    try:
                        for record in collection.find({'Topic' :Topico}):
                            article_buffer=record['Topic_description']
                            article=[article_buffer]+article
                        db_message=""
                        #return render_template("form_3.html",email=email,brand=brand,channel=channel,Topico=Topico,article=article,db_message=db_message)
                    except Exception as e:
                        article=None
                        db_message=" Exception not found the "+e
                        #return render_template("form_3.html",email=email,brand=brand,channel=channel,Topico=Topico,article=article,db_message=db_message)
                    if article ==[]:
                        db_message="not found the Topic in database click next to continue ,click Go back to select topic again"
                    return render_template("form_3.html",email=email,brand=brand,channel=channel,channelbrand=channelbrand,Topico=Topico,article=article,db_message=db_message)

                else :
                    if Topic == None or Topic_description == None or content == None:
                        return render_template("form3.html",email=email,brand=brand,channel=channel,channelbrand=channelbrand,Topico=Topico,selected_article=str(selected_article))
                    elif camera == "camera" :
                        attherate=Topic_description
                        combine_attherate=''
                        count=1
                        atherates=attherate.split(" @")
                        for x in atherates:
                            if count != 1:
                                combine_attherate=combine_attherate+x
                                count=count+1
                        Topic_description=Topic_description+group1+group2+group3+group4+group5
                        return render_template("form_webcam.html",email=email,brand=brand,channel=channel,channelbrand=channelbrand,Topic=Topic,Topic_description=Topic_description,content=content,combine_attherate=combine_attherate)

                        #return render_template("form3.html",email=email,brand=brand,channel=channel)

                    elif imagelink != None :

                        query_path=os.path.join(present_dir,'static/imagelink')
                        #query_image=(os.path.join(query_path,'myimage.png'))
                        query_image=(os.path.join(query_path,'pexels_image.jpg'))
                        #imagename=os.path.join('static/Capture','myimage.png')
                        imagename=os.path.join('static/imagelink','pexels_image.jpg')
                        fs = gridfs.GridFS(database)
                        cursor=fs.find()
                        cd = ColorDescriptor((8, 12, 3))
                        temp_path=os.path.join(present_dir,"static/results")
                        for root,dirs,files in os.walk(temp_path):
                            for file in files:
                                os.remove(os.path.join(root,file))
                        # output1 = open("index1.csv", "w")
                        i=0
                        # for record in cursor:    #for jpg images
                        # # 	#print(imagePath)
                        #   	image_bytes=record.read()
                        #   	temp="tempot.jpg"
                        #   	#databasedir=os.path.join(present_dir,'static/dataset1')
                        #   	temp_path=os.path.join(present_dir,temp)
                        #   	with open(temp_path,"wb") as binary_file:
                        #   	    binary_file.write(image_bytes)
                        #   	imageID=record.filename
                        #   	file_size=os.path.getsize(temp_path)
                        #   	#image = cv2.imread(temp_path)
                        #   	if file_size!=0:
                        #   	    #temp="tempot.jpg"
                        #   	    image = cv2.imread(temp_path)
                        #   	    features = cd.describe(image)
                        #   	    features = [str(f) for f in features]
                        #   	    output1.write("%s,%s\n" % (imageID, ",".join(features)))
                        # # # close the index file
                        # output1.close()
                        cd = ColorDescriptor((8, 12, 3))

                        query = cv2.imread(query_image)
                        features = cd.describe(query)
                        # perform the search
                        searcher = Searcher("index1.csv")
                        results = searcher.search(features)
                        print("filtered image paths from data bases are")
                        #print(scores)

                        seo_filter=[]
                        filter_image=[]
                        cursor=fs.find()
                        for (score, resultID) in results:
                        # 	# load the result image and display it

                              filter_image=filter_image+[resultID]
                              result =os.path.join('static/results',resultID)
                              seo_filter=seo_filter+[(score,result)]

                        limit=2
                        filter_image=filter_image[:limit]

                        seo_filter=seo_filter[:limit]

                        i=0
                        for x in cursor:
                            if x.filename in filter_image:

                                image_bytes=x.read()
                                temp=str(i)+".jpg"
                                temp_path=os.path.join(present_dir,"static/results")
                                temp_path=os.path.join(temp_path,x.filename)
                                with open(temp_path,"wb") as binary_file:
                                    binary_file.write(image_bytes)
                                i=i+1
                        x=datetime.now().isoformat().replace(":","-")
                        input_image="pexels_image"+x+".jpg"
                        # with open(query_image,'rb') as f:
                        #     contents=f.read()
                        # fs.put(contents,filename=input_image)

                        if seo_filter[0][0] < 3:
                            dowellclock = requests.get(dowellclock_url).json()['t1']
                            message1=f"dowellclock : {dowellclock} event_id :{event_id}, already uploaded, please give different image"
                            record="Given information is not stored into database"
                            return render_template('form4.html',record=record,email=email,brand=brand,channel=channel,channelbrand=channelbrand,Topic=Topic,Topic_description=Topic_description,content=content,message=str(message1),query_path=imagename,scores=seo_filter)
                            #return render_template('index1.html',message=str(message),query_path=imagename,scores=seo_filter)
                            #return make_response("already uploaded, please give different image")

                        else :
                            output1 = open("index1.csv", "a")
                            image = cv2.imread(query_image)
                            features = cd.describe(image)
                            features = [str(f) for f in features]
                            x=datetime.now().isoformat().replace(":","-")
                            input_image="pexels_image"+x+".jpg"
                            output1.write("%s,%s\n" % (input_image, ",".join(features)))
                            # # # close the index file
                            output1.close()

                            with open(query_image,'rb') as f:
                                contents=f.read()
                                b64_string = base64.b64encode(contents)
                            image_id=fs.put(contents,filename=input_image)
                            image_b64_str = b64_string.decode('utf-8')

                            file = m.upload(query_image,folder[0])

                            mega_drive_link =  m.get_upload_link(file)

                            attherate=Topic_description
                            combine_attherate=''
                            count=1
                            atherates=attherate.split(" @")
                            for x in atherates:
                                    if count != 1:
                                     combine_attherate=combine_attherate+x
                                    count=count+1

                            Topic_description=Topic_description+group1+group2+group3+group4+group5

                            dowellclock = requests.get(dowellclock_url).json()['t1']
                            form_data={
                                    "is_scheduled" :is_scheduled,
                                    "schedule" : schedule,
                                    "dowellclock" : dowellclock,
                                    "event_id"  : event_id,
                                    "email":email,
                                    "brand" :brand,
                                    "channel":channel,
                                    "channelbrand":channelbrand,
                                    "Topic":Topic,
                                    "Topic_description":Topic_description,
                                    "content":content,
                                    "Image_id":image_id,
                                    "image_b64_str" : "image_b64_str",
                                    "mega_drive_link" : mega_drive_link,
                                    "attherates":combine_attherate
                                    }
                            record=collection.insert_one(form_data)

                            message1=f"Given image is not present in database , Sucessfully saved the image to database and mega drive link :{mega_drive_link}"
                            #return render_template('form4.html',record=record,email=email,brand=brand,channel=channel,channelbrand=channelbrand,Topic=Topic,Topic_description=Topic_description,content=content,message=str(message1),query_path=imagename,scores=seo_filter,combine_attherate=combine_attherate)
                            return redirect('https://100007.pythonanywhere.com/')

                        #return make_response("input is nothing")



                    elif file != None :
                        try:
                            fs = gridfs.GridFS(database)
                            cursor=fs.find()

                            query_path=os.path.join(present_dir,'static/Query')
                            for root,dirs,files in os.walk(query_path):
                                for file in files:
                                    os.remove(os.path.join(root,file))
                            file = request.files['query_img']
                            file.save(os.path.join(query_path,file.filename))
                            query_image=(os.path.join(query_path,file.filename))
                            imagename=os.path.join('static/Query',file.filename)
                            rcvdimg=file.filename


                            cd = ColorDescriptor((8, 12, 3))
                            temp_path=os.path.join(present_dir,"static/results")
                            for root,dirs,files in os.walk(temp_path):
                                for file in files:
                                    os.remove(os.path.join(root,file))
                            # output1 = open("index1.csv", "w")
                            i=0
                            # for record in cursor:    #for jpg images
                            # # 	#print(imagePath)
                            #   	image_bytes=record.read()
                            #   	temp="tempot.jpg"
                            #   	#databasedir=os.path.join(present_dir,'static/dataset1')
                            #   	temp_path=os.path.join(present_dir,temp)
                            #   	with open(temp_path,"wb") as binary_file:
                            #   	    binary_file.write(image_bytes)
                            #   	imageID=record.filename
                            #   	file_size=os.path.getsize(temp_path)
                            #   	#image = cv2.imread(temp_path)
                            #   	if file_size!=0:
                            #   	    #temp="tempot.jpg"
                            #   	    image = cv2.imread(temp_path)
                            #   	    features = cd.describe(image)
                            #   	    features = [str(f) for f in features]
                            #   	    output1.write("%s,%s\n" % (imageID, ",".join(features)))
                            # # # close the index file
                            # output1.close()
                            cd = ColorDescriptor((8, 12, 3))

                            query = cv2.imread(query_image)
                            features = cd.describe(query)
                            # perform the search
                            searcher = Searcher("index1.csv")
                            results = searcher.search(features)
                            print("filtered image paths from data bases are")
                            #print(scores)

                            seo_filter=[]
                            filter_image=[]
                            cursor=fs.find()
                            for (score, resultID) in results:
                            # 	# load the result image and display it

                                  filter_image=filter_image+[resultID]
                                  result =os.path.join('static/results',resultID)
                                  seo_filter=seo_filter+[(score,result)]

                            limit=2
                            filter_image=filter_image[:limit]

                            seo_filter=seo_filter[:limit]

                            i=0
                            for x in cursor:
                                if x.filename in filter_image:

                                    image_bytes=x.read()
                                    temp=str(i)+".jpg"
                                    temp_path=os.path.join(present_dir,"static/results")
                                    temp_path=os.path.join(temp_path,x.filename)
                                    with open(temp_path,"wb") as binary_file:
                                        binary_file.write(image_bytes)
                                    i=i+1
                            x=datetime.now().isoformat().replace(":","-")

                            input_image=rcvdimg+x
                            # with open(query_image,'rb') as f:
                            #     contents=f.read()
                            # fs.put(contents,filename=input_image)
                            buffer_at=Topic_description
                            Topic_description=Topic_description+group1+group2+group3+group4+group5
                            if seo_filter[0][0] < 2 :
                                dowellclock = requests.get(dowellclock_url).json()['t1']
                                message=f"dowellclock : {dowellclock}  event_id : {event_id} already uploaded, please give different image"
                                record="Given information is not stored into database"
                                return render_template('form4.html',record=record,email=email,brand=brand,channel=channel,channelbrand=channelbrand,Topic=Topic,Topic_description=Topic_description,content=content,message=str(message),query_path=imagename,scores=seo_filter)
                                #return render_template('index1.html',message=str(message),query_path=imagename,scores=seo_filter)
                                #return make_response("already uploaded, please give different image")

                            else :
                                output1 = open("index1.csv", "a")
                                image = cv2.imread(query_image)
                                features = cd.describe(image)
                                features = [str(f) for f in features]
                                x=datetime.now().isoformat().replace(":","-")
                                input_image=rcvdimg+x
                                output1.write("%s,%s\n" % (input_image, ",".join(features)))
                                # # # close the index file
                                output1.close()


                                attherate=buffer_at
                                combine_attherate=''
                                count=1
                                atherates=attherate.split(" @")
                                for x in atherates:
                                    if count != 1:
                                     combine_attherate=combine_attherate+x
                                    count=count+1
                                with open(query_image,'rb') as f:
                                    contents=f.read()
                                    b64_string = base64.b64encode(contents)
                                image_id=fs.put(contents,filename=input_image)
                                image_b64_str = b64_string.decode('utf-8')

                                file = m.upload(query_image,folder[0])
                                mega_drive_link = m.get_upload_link(file)

                                dowellclock = requests.get(dowellclock_url).json()['t1']

                                form_data={
                                    "is_scheduled" :is_scheduled,
                                    "schedule" : schedule,
                                    "dowellclock" : dowellclock,
                                    "event_id"  : event_id,
                                    "email":email,
                                    "brand" :brand,
                                    "channel":channel,
                                    "channelbrand":channelbrand,
                                    "Topic":Topic,
                                    "Topic_description":Topic_description,
                                    "content":content,
                                    "Image_id":image_id,
                                    "image_b64_str" : "image_b64_str",
                                    "mega_drive_link" : mega_drive_link,
                                    "attherates":combine_attherate
                                    }
                                record=collection.insert_one(form_data)
                                message1=f"Given image is not present in database , Sucessfully saved the image to database and mega drive link : {mega_drive_link}"
                                #return render_template('form4.html',record=record,email=email,brand=brand,channel=channel,channelbrand=channelbrand,Topic=Topic,Topic_description=Topic_description,content=content,message=str(message1),query_path=imagename,scores=seo_filter,combine_attherate=combine_attherate)
                                return redirect('https://100007.pythonanywhere.com/')

                        except Exception as e:
                            dowellclock = requests.get(dowellclock_url).json()['t1']
                            message=f"dowellclock : {dowellclock} event_id :{event_id} submit again,inputs are not given properly try again  and exception is : {e} "
                            return render_template("form2.html",email=email,message=message)
                            #return render_template("form3.html",email=email,brand=brand,channel=channel,execptn=e)

                            #return render_template('index.html',query_path=imagename,scores=seo_filter)
                            #return make_response('execptio-> {}'.format(e))



                    else :
                        query_path=os.path.join(present_dir,'static/Capture')
                        query_image=(os.path.join(query_path,'myimage.png'))
                        imagename=os.path.join('static/Capture','myimage.png')
                        fs = gridfs.GridFS(database)
                        cursor=fs.find()
                        cd = ColorDescriptor((8, 12, 3))
                        temp_path=os.path.join(present_dir,"static/results")
                        for root,dirs,files in os.walk(temp_path):
                            for file in files:
                                os.remove(os.path.join(root,file))
                        # output1 = open("index1.csv", "w")
                        i=0
                        # for record in cursor:    #for jpg images
                        # # 	#print(imagePath)
                        #   	image_bytes=record.read()
                        #   	temp="tempot.jpg"
                        #   	#databasedir=os.path.join(present_dir,'static/dataset1')
                        #   	temp_path=os.path.join(present_dir,temp)
                        #   	with open(temp_path,"wb") as binary_file:
                        #   	    binary_file.write(image_bytes)
                        #   	imageID=record.filename
                        #   	file_size=os.path.getsize(temp_path)
                        #   	#image = cv2.imread(temp_path)
                        #   	if file_size!=0:
                        #   	    #temp="tempot.jpg"
                        #   	    image = cv2.imread(temp_path)
                        #   	    features = cd.describe(image)
                        #   	    features = [str(f) for f in features]
                        #   	    output1.write("%s,%s\n" % (imageID, ",".join(features)))
                        # # # close the index file
                        # output1.close()
                        cd = ColorDescriptor((8, 12, 3))

                        query = cv2.imread(query_image)
                        features = cd.describe(query)
                        # perform the search
                        searcher = Searcher("index1.csv")
                        results = searcher.search(features)
                        print("filtered image paths from data bases are")
                        #print(scores)

                        seo_filter=[]
                        filter_image=[]
                        cursor=fs.find()
                        for (score, resultID) in results:
                        # 	# load the result image and display it

                              filter_image=filter_image+[resultID]
                              result =os.path.join('static/results',resultID)
                              seo_filter=seo_filter+[(score,result)]

                        limit=3
                        filter_image=filter_image[:limit]

                        seo_filter=seo_filter[:limit]

                        i=0
                        for x in cursor:
                            if x.filename in filter_image:

                                image_bytes=x.read()
                                temp=str(i)+".jpg"
                                temp_path=os.path.join(present_dir,"static/results")
                                temp_path=os.path.join(temp_path,x.filename)
                                with open(temp_path,"wb") as binary_file:
                                    binary_file.write(image_bytes)
                                i=i+1
                        x=datetime.now().isoformat().replace(":","-")
                        input_image="cameraimg"+x+".jpg"
                        # with open(query_image,'rb') as f:
                        #     contents=f.read()
                        # fs.put(contents,filename=input_image)

                        if seo_filter[0][0] < 3:
                            dowellclock = requests.get(dowellclock_url).json()['t1']
                            message1=f"dowellclock : {dowellclock} event_id:{event_id} already uploaded, please give different image"
                            record="Given information is not stored into database"
                            return render_template('form4.html',record=record,email=email,brand=brand,channel=channel,channelbrand=channelbrand,Topic=Topic,Topic_description=Topic_description,content=content,message=str(message1),query_path=imagename,scores=seo_filter)
                            #return render_template('index1.html',message=str(message),query_path=imagename,scores=seo_filter)
                            #return make_response("already uploaded, please give different image")

                        else :
                            output1 = open("index1.csv", "a")
                            image = cv2.imread(query_image)
                            features = cd.describe(image)
                            features = [str(f) for f in features]
                            x=datetime.now().isoformat().replace(":","-")
                            input_image="cameraimg"+x+".jpg"
                            output1.write("%s,%s\n" % (input_image, ",".join(features)))
                            # # # close the index file
                            output1.close()

                            with open(query_image,'rb') as f:
                                contents=f.read()
                                b64_string = base64.b64encode(contents)

                            image_id=fs.put(contents,filename=input_image)
                            image_b64_str = b64_string.decode('utf-8')

                            file = m.upload(query_image,folder[0])
                            mega_drive_link = m.get_upload_link(file)

                            dowellclock = requests.get(dowellclock_url).json()['t1']

                            form_data={
                                "is_scheduled" :is_scheduled,
                                    "schedule" : schedule,
                                    "dowellclock" : dowellclock,
                                    "event_id" : event_id,
                                    "email":email,
                                    "brand" :brand,
                                    "channel":channel,
                                    "channelbrand":channelbrand,
                                    "Topic":Topic,
                                    "Topic_description":Topic_description,
                                    "content":content,
                                    "Image_id":image_id,
                                    "image_b64_str" : "image_b64_str",
                                    "mega_drive_link" : mega_drive_link
                                    }
                            record=collection.insert_one(form_data)

                            message1=f"dowellclock : {dowellclock} ,Given image is not present in database , Sucessfully saved the image to database and mega drive link{mega_drive_link} "
                            #return render_template('form4.html',record=record,email=email,brand=brand,channel=channel,channelbrand=channelbrand,Topic=Topic,Topic_description=Topic_description,content=content,message=str(message1),query_path=imagename,scores=seo_filter)
                            return redirect('https://100007.pythonanywhere.com/')

                        #return make_response("input is nothing")
                    #     return make_response("mail {} 1 {} 2 {}  topic {} topic desc{} content {} ".format(email,brand,channel,Topic,Topic_description,content))




@app.route('/topicApp/<name>', methods=['GET','POST'])
def topicApp(name):

    #payload = request.json

    #topic = payload['topic']
    topic = name
    cursor=collection.find()
    article =[]

    try:
        count = 0
        for record in collection.find({'Topic' :topic}):
            temp = {
                "id" : count,
                "article_buffer" : record['Topic_description'],
              "link":"pythonanywhere",
                "sub" : name,
                 "heading":name

                }
            article_buffer=record['Topic_description']
            article=[temp]+article
            count = count + 1
    except Exception as e:
            print(e)

    return Response(json.dumps(article),mimetype='application/json')

    #return make_response(f"data in database :{count}{article} ")














@app.route('/_autocomplete', methods=['GET','POST'])
def autocomplete():
    cursor=collection.find()
    combine=[]
    for record in cursor:
        try:
            buffer=record['email']
            combine=combine+['@'+buffer]
        except Exception as e:
            print(e)

    return Response(json.dumps(combine), mimetype='application/json')


@app.route('/_autocompleteTopic', methods=['GET','POST'])
def autocompleteTopic():
    cursor=collection.find()
    combine=[]
    for record in cursor:
        try:
            buffer=record['Topic']
            combine=combine+[buffer]
        except Exception as e:
            print(e)

    return Response(json.dumps(combine), mimetype='application/json')



@app.route('/auto_test', methods=['GET','POST'])
def autocomplete1():
    if request.method=="GET":
        return render_template('autocompleted.html')
    elif request.method == "POST":
        tags=request.values.get("tags")
        return make_response("recieved data {}".format(tags))


@app.route('/listdataindb')
def list_data_in_db():
    cursor=collection.find()
    combine=[]
    for record in cursor:
        try:
            buffer=record['name']
            combine=combine+['@'+buffer]
        except Exception as e:
            print(e)

    return make_response("data in database :{} ".format(combine))











@app.route('/image_sug', methods=['GET','POST'])
def image_sug():
    if request.method=="GET":
        return render_template('image_sug.html')
    elif request.method == "POST":
        tags=request.values.get("imagelink")
        return make_response("recieved data {}".format(tags))



@app.route('/_image_autocomplete', methods=['GET','POST'])
def image_autocomplete():
    x=request.values.get("term")
    output=[]
    api=API(PEXELS_API_KEY)
    api.search(x,page=1,results_per_page=10)
    photos=api.get_entries()
    for photo in photos:
        temp={}
        temp['value']=photo.description
        url=photo.small
        temp['imagelink']=photo.original
        temp['label']='<img src="' +url+ '" width="70" />&nbsp;&nbsp;&nbsp;' + temp['value'] + ''
        output.append(temp)

    return Response(json.dumps(output),mimetype='application/json')




@app.route('/')
def hello_world():
    x=fs.find()
    i=0
    for f in x:
        i=i+1

    return make_response("ok{}".format(i))





#FOR SOCIAL MEDIA APP
@app.route('/topicApptest1', methods=['GET','POST'])
def topicApptest1():

    payload = request.json

    topic = payload['topic']
    #topic = "global warming"
    name = topic

    cursor=collection.find()
    article =[]

    try:
        count = 0
        for record in collection.find({'Topic' :topic}):
            temp = {
                "id" : count,
                "article_buffer" : record['Topic_description'],
              "link":"pythonanywhere",
                "sub" : name,
                 "heading":name

                }
            article_buffer=record['Topic_description']
            article=[temp]+article
            count = count + 1
    except Exception as e:
            print(e)
    name = f"--{name}--pyt"
    article = {
        "title":name
        }
    return Response(json.dumps(article), mimetype='application/json')
    #return make_response(article.to_json(),200)
    #return "hi------------------------"



#FOR SOCIAL MEDIA APP AItopic sentence generator
@app.route('/topicgenerator', methods=['GET','POST'])
def AI_topic_generator():

    payload = request.json

    object1 = payload['object1']
    subject = payload['subject']
    subject_determinant = payload['subject_determinant']
    subject_number = payload['subject_number']
    object_deteminant = payload['object_deteminant']
    object_number = payload['object_number']
    adjective = payload['adjective']
    verb = payload['verb']
    count = 0

    print("index AI_topic_generator")
    url = "https://linguatools-sentence-generating.p.rapidapi.com/realise"
    LINGUA_KEY = '1ab6a8ab35msh454e13d4febb540p1f0fe3jsn5303c2162430'

    def api_call(grammar_arguments=None,count=None):
        if grammar_arguments is None:
            grammar_arguments = {}
        querystring = {
            "object": object1,
            "subject": subject,
            "verb": verb,
            "objmod": adjective,
            'subjdet': subject_determinant,
            'objdet': object_deteminant,
            'objnum': object_number,
            'subjnum': subject_number

        }
        iter_sentence_type = []
        if 'tense' in grammar_arguments:
            # print('Current tense is {}'.format(grammar_arguments['tense']))
            querystring['tense'] = grammar_arguments['tense'].capitalize()
            iter_sentence_type.append(
                grammar_arguments['tense'].capitalize())
        if 'progressive' in grammar_arguments:
            querystring['progressive'] = 'progressive'
            iter_sentence_type.append(grammar_arguments['progressive'])

        if 'perfect' in grammar_arguments:
            querystring['perfect'] = 'perfect'
            iter_sentence_type.append(grammar_arguments['perfect'])

        if 'negated' in grammar_arguments:
            querystring['negated'] = 'negated'
            iter_sentence_type.append(grammar_arguments['negated'])

        if 'passive' in grammar_arguments:
            querystring['passive'] = 'passive'
            iter_sentence_type.append(grammar_arguments['passive'])

        if 'modal_verb' in grammar_arguments:
            querystring['modal'] = grammar_arguments['modal_verb']

        if 'sentence_art' in grammar_arguments:
            querystring['sentencetype'] = grammar_arguments['sentence_art']
        iter_sentence_type.append("sentence.")
        type_of_sentence = ' '.join(iter_sentence_type)

        headers = {
            'x-rapidapi-host': "linguatools-sentence-generating.p.rapidapi.com",
            'x-rapidapi-key': LINGUA_KEY
        }
        resp = requests.request("GET", url, headers=headers, params=querystring).json()[
            'sentence']

        print(f"{resp} --- {type_of_sentence}")
        # return [requests.request("GET", url, headers=headers, params=querystring).json()['sentence'],
        #         type_of_sentence]

        dict1 = {
        "id" :count,
        "Heading":type_of_sentence,
        "Placeholder":resp,
        }


        return dict1

    tenses = ['past', 'present', 'future']
    other_grammar = ['passive', 'progressive', 'perfect', 'negated']
    results = []
    result_ids = []
    counter = 0
    for tense in tenses:
        for grammar in other_grammar:
            counter += 1
            count = count + 1
            #sentence_results = SentenceResults(sentence_grammar=sentence_grammar)
            arguments = {'tense': tense, grammar: grammar}
            results.append(api_call(arguments,str(count)))

    print(results)

    #results = f"{object1} and sub:{subject}"

    return Response(json.dumps(results), mimetype='application/json')
    #return Response(json.dumps(results), mimetype='application/json')





#FOR SOCIAL MEDIA APP AItopic sentence generator
@app.route('/topicgenerator1', methods=['GET','POST'])
def AI_topic_generator1():

    payload = request.json

    topic = []
    sentence_type = []

    object1 = payload['object1']
    subject = payload['subject']
    subject_determinant = payload['subject_determinant']
    subject_number = payload['subject_number']
    object_deteminant = payload['object_deteminant']
    object_number = payload['object_number']
    adjective = payload['adjective']
    verb = payload['verb']
    count = 0

    print("index AI_topic_generator")
    url = "https://linguatools-sentence-generating.p.rapidapi.com/realise"
    LINGUA_KEY = '1ab6a8ab35msh454e13d4febb540p1f0fe3jsn5303c2162430'

    def api_call(grammar_arguments=None,count=None):
        if grammar_arguments is None:
            grammar_arguments = {}
        querystring = {
            "object": object1,
            "subject": subject,
            "verb": verb,
            "objmod": adjective,
            'subjdet': subject_determinant,
            'objdet': object_deteminant,
            'objnum': object_number,
            'subjnum': subject_number

        }
        iter_sentence_type = []
        if 'tense' in grammar_arguments:
            # print('Current tense is {}'.format(grammar_arguments['tense']))
            querystring['tense'] = grammar_arguments['tense'].capitalize()
            iter_sentence_type.append(
                grammar_arguments['tense'].capitalize())
        if 'progressive' in grammar_arguments:
            querystring['progressive'] = 'progressive'
            iter_sentence_type.append(grammar_arguments['progressive'])

        if 'perfect' in grammar_arguments:
            querystring['perfect'] = 'perfect'
            iter_sentence_type.append(grammar_arguments['perfect'])

        if 'negated' in grammar_arguments:
            querystring['negated'] = 'negated'
            iter_sentence_type.append(grammar_arguments['negated'])

        if 'passive' in grammar_arguments:
            querystring['passive'] = 'passive'
            iter_sentence_type.append(grammar_arguments['passive'])

        if 'modal_verb' in grammar_arguments:
            querystring['modal'] = grammar_arguments['modal_verb']

        if 'sentence_art' in grammar_arguments:
            querystring['sentencetype'] = grammar_arguments['sentence_art']
        iter_sentence_type.append("sentence.")
        type_of_sentence = ' '.join(iter_sentence_type)

        headers = {
            'x-rapidapi-host': "linguatools-sentence-generating.p.rapidapi.com",
            'x-rapidapi-key': LINGUA_KEY
        }
        print(100*"#")
        print(f"{requests.request('GET', url, headers=headers, params=querystring).json()} --- {type_of_sentence}")
        resp = requests.request("GET", url, headers=headers, params=querystring).json()['sentence']


        # return [requests.request("GET", url, headers=headers, params=querystring).json()['sentence'],
        #         type_of_sentence]

        topic.append(resp)
        sentence_type.append(type_of_sentence)


        return 0

    tenses = ['past', 'present', 'future']
    other_grammar = ['passive', 'progressive', 'perfect', 'negated']
    results = []
    result_ids = []
    counter = 0
    for tense in tenses:
        for grammar in other_grammar:
            counter += 1
            count = count + 1
            #sentence_results = SentenceResults(sentence_grammar=sentence_grammar)
            arguments = {'tense': tense, grammar: grammar}
            results.append(api_call(arguments,str(count)))

    print(results)
    results1 = {
        "id" : '1',
        "topic" : topic,
        "sentence_type" : sentence_type

        }

    #results = f"{object1} and sub:{subject}"

    return Response(json.dumps(results1), mimetype='application/json')
    #return Response(json.dumps(results), mimetype='application/json')








# using in social media app
@app.route('/topicApptest/<name>', methods=['GET','POST'])
def topicApptest(name):

    payload = request.json

    #topic = payload['topic']
    topic = "global warming"
    #name = topic

    cursor=collection.find()
    article =[]

    try:
        count = 0
        for record in collection.find({'Topic' :topic}):
            temp = {
                "id" : count,
                "sub" : record['Topic_description'],
              "link":"pythonanywhere",
                "heading" : name,
                 "paragraph":name

                }
            article_buffer=record['Topic_description']
            article=[temp]+article
            count = count + 1
    except Exception as e:
            print(e)
    name = f"--{name}--pyt"
    # article = {
    #     "title":name
    #     }
    return Response(json.dumps(article), mimetype='application/json')
    #return make_response(article.to_json(),200)
    #return "hi------------------------"





def get_event_id():
    dd = datetime.now()
    time = dd.strftime("%d:%m:%Y,%H:%M:%S")
    url = "https://100003.pythonanywhere.com/event_creation"
    data = {"platformcode": "FB", "citycode": "101", "daycode": "0",
            "dbcode": "pfm", "ip_address": "192.168.0.41",
            "login_id": "lav", "session_id": "new",
            "processcode": "1", "regional_time": time,
            "dowell_time": time, "location": "22446576",
            "objectcode": "1", "instancecode": "100051", "context": "afdafa ",
            "document_id": "3004", "rules": "some rules", "status": "work"
            }

    r = requests.post(url, json=data)
    return r.text


def get_dowellclock():
    response_dowell = requests.get(
        'https://100009.pythonanywhere.com/dowellclock')
    data = response_dowell.json()
    return data['t1']



@app.route("/dbpost", methods=['GET', 'POST'])
def dbpost():
    global respid_main_count
    collection = database.topicslist
    print("hello")
    url = 'http://100002.pythonanywhere.com/'
    payload = request.json
    email = payload['email']
    product = payload['target_product']

    dict1 = {

              'email':payload['email'],
              'target_industry':payload['target_industry'],
              'target_product' :payload['target_product'],
              'subject_determinant':payload['subject_determinant'],
              'subject':payload['subject'],
              'subject_number':payload['subject_number'],
              'object_determinant':payload['object_determinant'],
              'object':payload['object'],
              'object_number':payload['object_number'],
              'verb':payload['verb'],
              'adjective':payload['adjective']

        }

    count = 0
    for itr in payload['rank_list']:
        dict1[f'api_sentence_{count+1}']={'sentence':payload['resp_Data']['topic'][count],'sentence_type':payload['resp_Data']['sentence_type'][count],'sentence_id':respid_main_count}
        dict1[f'sentence_rank_{count+1}']={'sentence_rank':itr,'sentence_result':payload['resp_Data']['topic'][count],'sentence_id':respid_main_count}
        count = count+1
        respid_main_count = respid_main_count+1

    respid_main_count = respid_main_count+1

    #dict1['user_id'] = payload['email']
    #dict1['session_id'] = payload['email']
    dict1['event_id'] = get_event_id()
    dict1['dowelltime'] = get_dowellclock()

    print(dict1)
    data = {
    "cluster": "socialmedia",
    "database": "socialmedia",
    "collection": "socialmedia",
    "document": "socialmedia",
    "team_member_ID": "345678977",
    "function_ID": "ABCDE",
    "command": "insert",

    "field": dict1,

    'update_field': {
        "name": "Joy update",
        "phone": "123456",
        "age": "26",
        "language": "English",

    },
    "platform": "bangalore",

    }

    headers = {'content-type': 'application/json'}

    response = requests.post(url, json=data, headers=headers)
    print(f"saved in database{response.text}")
    print(data)
    resp = response.json()
    inserted_id = resp['inserted_id']
    print()
    data_topic = {

        "email":email,
        "productid" : inserted_id,
        'product': product


        }

    collection.insert(data_topic)
    #return response.json()
    #return "hi----"
    return Response(json.dumps(str(response.json())), mimetype='application/json')



@app.route("/qrcode", methods=['GET', 'POST'])
def qrcode_generator():
    if request.method=="GET":
        return render_template('qrcode1.html')

    elif request.method == "POST":
        print("------qrcode_generator-----------------------")
        qrlink = request.values.get("qrlink")
        try:
            file = request.files['query_img']
            query_path=os.path.join(present_dir,'static/qrcode')
            file.save(os.path.join(query_path,'qr_image.png'))
            dir = os.path.join(present_dir,"static/qrcode/qr_image.png")
            logo = Image.open(dir)
            basewidth = 100
            wpercent = (basewidth/float(logo.size[0]))
            hsize = int((float(logo.size[1])*float(wpercent)))
            logo = logo.resize((basewidth,hsize),Image.ANTIALIAS)
            QRcode = qrcode.QRCode(error_correction = qrcode.constants.ERROR_CORRECT_H)
            QRcode.add_data(qrlink)
            QRcode.make()
            QRcolor = 'Green'
            QRimg = QRcode.make_image(fill_color =QRcolor,back_color="white").convert('RGB')
            pos = ((QRimg.size[0] - logo.size[0])//2,
                    (QRimg.size[1] - logo.size[1]) //2)
            QRimg.paste(logo, pos)
            QRimg.save(dir)
            qr_image=os.path.join('static/qrcode','qr_image.png')
            return render_template('qrcode2.html',query_path=qr_image,url = qrlink)



        except Exception as e :
            print(f'------->{e}')
            file = None
            link="www.geeksforgeeks.com"
            dir = os.path.join(present_dir,"static/qrcode/myqrcode.png")
            url = pyqrcode.create(qrlink)
            url.png(dir,scale = 6)
            qr_image=os.path.join('static/qrcode','myqrcode.png')
            return render_template('qrcode2.html',query_path=qr_image,url = qrlink)

        #return qrlink
        #return make_response("recieved data {}".format(tags))




#FOR SOCIAL MEDIA APP AI COMMENT  generator
@app.route('/commentgenerator', methods=['GET','POST'])
def AI_Comment_Generator():
    print("----------> AI_Comment_Generator--")


    Product = "food"
    Hashtag = "#innovation"

    Dowellhandler ='UXLivingLab'
    Product = '628cf5ce7042698fbe9a0868'
    Hashtag ='#innovation 1'
    Topic = 'the'

    payload = request.json
    Hashtag = f"#{payload['Hashtag']}"
    print(f"---{Hashtag}--")
    product_list = payload['product_list']
    product_ids = payload['product_ids']
    print(product_list)
    print(product_ids)
    print(product_ids[product_list.index(payload['Product'])])
    Product = product_ids[product_list.index(payload['Product'])]

    topic = []
    sentence_type = []

    #Dowellhandler = request.POST.get("Dowellhandler")
    #Product = request.POST.get("Product")
    #Hashtag = request.POST.get("Hashtag")
    #Topic = request.POST.get("Topic")


    # Dowellhandler = 'Dowellhandler'
    # Product = payload['Product']
    # Hashtag = payload['Hashtag']
    # Topic = 'Uxlivinglab'

    print(f"{Dowellhandler} product {Product} Hashtag {Hashtag} Topic : {Topic} ")

    #Hashtag = Hashtag.replace('#', '')
    #hashtag_split = Hashtag.split()

    #Hashtag = hashtag_split[0]
    #Hashtag_group = hashtag_split[1]
    Hashtag = Hashtag
    Hashtag_group = Hashtag

    url = 'http://100002.pythonanywhere.com/'

    data = {
                "cluster": "socialmedia",
                "database": "socialmedia",
                "collection": "socialmedia",
                "document": "socialmedia",
                "team_member_ID": "345678977",
                "function_ID": "ABCDE",
                "command": "find",
                "field": {"_id": Product},

                'update_field': {
                    "name": "Joy update",
                    "phone": "123456",
                    "age": "26",
                    "language": "English",

                },
                "platform": "bangalore",

    }
    headers = {'content-type': 'application/json'}

    response = requests.post(url, json=data, headers=headers)
    topics = response.json()
    # print(topics['data']['target_product'])

    print(Dowellhandler, topics, Hashtag, Topic)




    count = 0


    url = "https://linguatools-sentence-generating.p.rapidapi.com/realise"
    LINGUA_KEY = '1ab6a8ab35msh454e13d4febb540p1f0fe3jsn5303c2162430'

    def api_call(grammar_arguments=None,count=None):
        if grammar_arguments is None:
            grammar_arguments = {}
        querystring = {
                    "object": Dowellhandler,
                    "subject": topics['data']['target_product'],
                    "verb": Hashtag,
                    'subjdet': Topic

        }
        iter_sentence_type = []
        if 'tense' in grammar_arguments:
            # print('Current tense is {}'.format(grammar_arguments['tense']))
            querystring['tense'] = grammar_arguments['tense'].capitalize()
            iter_sentence_type.append(
                grammar_arguments['tense'].capitalize())
        if 'progressive' in grammar_arguments:
            querystring['progressive'] = 'progressive'
            iter_sentence_type.append(grammar_arguments['progressive'])

        if 'perfect' in grammar_arguments:
            querystring['perfect'] = 'perfect'
            iter_sentence_type.append(grammar_arguments['perfect'])

        if 'negated' in grammar_arguments:
            querystring['negated'] = 'negated'
            iter_sentence_type.append(grammar_arguments['negated'])

        if 'passive' in grammar_arguments:
            querystring['passive'] = 'passive'
            iter_sentence_type.append(grammar_arguments['passive'])

        if 'modal_verb' in grammar_arguments:
            querystring['modal'] = grammar_arguments['modal_verb']

        if 'sentence_art' in grammar_arguments:
            querystring['sentencetype'] = grammar_arguments['sentence_art']
        iter_sentence_type.append("sentence.")
        type_of_sentence = ' '.join(iter_sentence_type)

        headers = {
            'x-rapidapi-host': "linguatools-sentence-generating.p.rapidapi.com",
            'x-rapidapi-key': LINGUA_KEY
        }
        print(100*"#")
        print(f"{requests.request('GET', url, headers=headers, params=querystring).json()} --- {type_of_sentence}")
        resp = requests.request("GET", url, headers=headers, params=querystring).json()['sentence']


        # return [requests.request("GET", url, headers=headers, params=querystring).json()['sentence'],
        #         type_of_sentence]

        topic.append(resp)
        sentence_type.append(type_of_sentence)


        return 0

    tenses = ['past', 'present', 'future']
    other_grammar = ['passive', 'progressive', 'perfect', 'negated']
    results = []
    result_ids = []
    counter = 0
    for tense in tenses:
        for grammar in other_grammar:
            counter += 1
            count = count + 1
            #sentence_results = SentenceResults(sentence_grammar=sentence_grammar)
            arguments = {'tense': tense, grammar: grammar}
            results.append(api_call(arguments,str(count)))

    print(results)
    results1 = {
        "id" : '1',
        "topic" : topic,
        "sentence_type" : sentence_type

        }

    #results = f"{object1} and sub:{subject}"

    return Response(json.dumps(results1), mimetype='application/json')
    #return Response(json.dumps(results), mimetype='application/json')


@app.route('/dblist')
def dblist():
    db_names = connection.list_database_names()
    col_name = connection['client_data'].list_collection_names()
    cols_name = connection['DB_IMAGE'].list_collection_names()

    return make_response(f"ok{col_name}  {cols_name}")

@app.route('/productlist', methods=['GET','POST'])
#@app.route('/productlist')
def productlist():
    print("-----productlist--------------")
    payload = request.json
    email = payload['email']
    #email = 'eshwarmachapur@gmail.com'
    collection = database.topicslist
    data_topic = {

        "email":"example@gmail.com",
        "productid" : "12345",
        'product': 'Product'


        }

    #rec1 = collection.insert(data_topic)
    cursor = collection.find()
    productdata = {
     'id':'1',
     'Category':'Test1'

    }
    product = []
    productid =[]
    print("----<<<<<<__------")
    for record in collection.find({'email' :email}):
    #for record in cursor:
        product.append(record['product'])
        productid.append(record['productid'])
    data1 = ['food','money','technology','restaurent','drinks']
    data2 = {
        'productlist' :product[::-1],
        'productid' : productid[::-1]
        }
    print(data2)
    print("end of product id")
    return Response(json.dumps(data2), mimetype='application/json')
    #return make_response(f"ok{data2}")


@app.route('/comments', methods=['GET','POST'])
#@app.route('/save_comments')
def comments():
    payload = request.json
    comments = payload['comments']
    selected_comment = payload['selected_comment']
    status = [False for i in range(12)]
    status[comments.index(selected_comment)] = True
    print(status)
    print(comments.index(selected_comment))
    print(payload)
    data = "hello world!"
    Topic_id = ""
    Dowellhandler =""
    Product = ""
    Hashtag = ""
    email = ""
    sentence =[]
    status =[]
    data1= {'Topic_id': Topic_id, 'Dowellhandler': Dowellhandler, 'Product': Product, 'Hashtag': Hashtag, 'Topic': 'the',
'session_id': email, 'Hashtag_group': '3',
'api_sentence_1': {'sentence': sentence[0],
'sentence_type': 'Past passive sentence.', 'sentence_id': 3013, 'selected': status[0]},
'api_sentence_2': {'sentence': sentence[1],
'sentence_type': 'Past progressive sentence.', 'sentence_id': 3014, 'selected': status[1]},
'api_sentence_3': {'sentence': sentence[2],
'sentence_type': 'Past perfect sentence.', 'sentence_id': 3015, 'selected': status[2]},
'api_sentence_4': {'sentence': sentence[3],
'sentence_type': 'Past negated sentence.', 'sentence_id': 3016, 'selected': status[3]},
'api_sentence_5': {'sentence': sentence[4],
'sentence_type': 'Present passive sentence.', 'sentence_id': 3017, 'selected': status[4]},
'api_sentence_6': {'sentence': sentence[5],
'sentence_type': 'Present progressive sentence.', 'sentence_id': 3018, 'selected': status[5]},
'api_sentence_7': {'sentence': sentence[6],
'sentence_type': 'Present perfect sentence.', 'sentence_id': 3019, 'selected': status[6]},
'api_sentence_8': {'sentence': sentence[7],
'sentence_type': 'Present negated sentence.', 'sentence_id': 3020, 'selected': status[7]},
'api_sentence_9': {'sentence': sentence[8],
'sentence_type': 'Future passive sentence.', 'sentence_id': 3021, 'selected': status[8]},
'api_sentence_10': {'sentence': sentence[9],
'sentence_type': 'Future progressive sentence.', 'sentence_id': 3022, 'selected': status[9]},
'api_sentence_11': {'sentence': sentence[10],
'sentence_type': 'Future perfect sentence.', 'sentence_id': 3023, 'selected': status[10]},
'api_sentence_12': {'sentence': sentence[11],
'sentence_type': 'Future negated sentence.', 'sentence_id': 3024, 'selected': status[11]},
'comment': 'The food will have goodmorninged an UXLivingLab.'}
    return Response(json.dumps(data), mimetype='application/json')




@app.route('/save_comments', methods=['GET','POST'])
#@app.route('/save_comments')
def save_comments():
    payload = request.json
    sentence =comments = payload['comments']
    selected_comment = payload['selected_comment']
    status = [False for i in range(12)]
    status[comments.index(selected_comment)] = True
    print(status)
    print(comments.index(selected_comment))
    Hashtag = f"#{payload['Hashtag']}"
    email = payload['email']
    Product = payload['Product']
    Dowellhandler = 'UXLivingLab'
    Topic_id = payload['product_ids'][payload['product_list'].index(Product)]
    print(f"{Hashtag} {email}  {Topic_id}  {Dowellhandler} {Product} ")
    print(payload)
    field= {'Topic_id': Topic_id, 'Dowellhandler': Dowellhandler, 'Product': Product, 'Hashtag': Hashtag, 'Topic': 'the',
'session_id': email, 'Hashtag_group': '3',
'api_sentence_1': {'sentence': sentence[0],
'sentence_type': 'Past passive sentence.', 'sentence_id': 3013, 'selected': status[0]},
'api_sentence_2': {'sentence': sentence[1],
'sentence_type': 'Past progressive sentence.', 'sentence_id': 3014, 'selected': status[1]},
'api_sentence_3': {'sentence': sentence[2],
'sentence_type': 'Past perfect sentence.', 'sentence_id': 3015, 'selected': status[2]},
'api_sentence_4': {'sentence': sentence[3],
'sentence_type': 'Past negated sentence.', 'sentence_id': 3016, 'selected': status[3]},
'api_sentence_5': {'sentence': sentence[4],
'sentence_type': 'Present passive sentence.', 'sentence_id': 3017, 'selected': status[4]},
'api_sentence_6': {'sentence': sentence[5],
'sentence_type': 'Present progressive sentence.', 'sentence_id': 3018, 'selected': status[5]},
'api_sentence_7': {'sentence': sentence[6],
'sentence_type': 'Present perfect sentence.', 'sentence_id': 3019, 'selected': status[6]},
'api_sentence_8': {'sentence': sentence[7],
'sentence_type': 'Present negated sentence.', 'sentence_id': 3020, 'selected': status[7]},
'api_sentence_9': {'sentence': sentence[8],
'sentence_type': 'Future passive sentence.', 'sentence_id': 3021, 'selected': status[8]},
'api_sentence_10': {'sentence': sentence[9],
'sentence_type': 'Future progressive sentence.', 'sentence_id': 3022, 'selected': status[9]},
'api_sentence_11': {'sentence': sentence[10],
'sentence_type': 'Future perfect sentence.', 'sentence_id': 3023, 'selected': status[10]},
'api_sentence_12': {'sentence': sentence[11],
'sentence_type': 'Future negated sentence.', 'sentence_id': 3024, 'selected': status[11]},
'comment': 'The food will have goodmorninged an UXLivingLab.'}
    print(field)

    url = "http://100002.pythonanywhere.com/"

    payload = json.dumps({
      "cluster": "socialmedia",
      "database": "socialmedia",
      "collection": "comments",
      "document": "comments",
      "team_member_ID":"12345",
      "function_ID": "ABCDE",
      "command": "insert",
      "field": field,
      "update_field": {
        "order_nos": 21
      },
      "platform": "bangalore"
    })
    headers = {
      'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    print(response.json())

    return Response(json.dumps(response.text), mimetype='application/json')



