
# A very simple Flask Hello World app for you to get started with...

from flask import Flask,make_response,request,render_template
import glob
import os.path
import os,re
import cv2
import numpy as np
import imutils
import csv
from PIL import Image
# from datetime import datetime
# import random
from datetime import datetime
from pymongo import MongoClient
import gridfs
import ssl
import certifi
present_dir=os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__)

connection = MongoClient("mongodb+srv://qruser:qr1234@cluster0.n2ih9.mongodb.net/DB_IMAGE?retryWrites=true&w=majority",ssl_cert_reqs=ssl.CERT_REQUIRED, ssl_ca_certs=certifi.where())

database = connection['client_data']
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
        file_path_name=os.path.join(query_path,file.filename)
        file_path_name1=os.path.join(query_path1,file.filename)
        #file.save(file_path_name)
        img=Image.open(file.stream)    #PIL Image
        file1 = request.files['image']
        img1=Image.open(file1.stream)
        uploaded_img_path =file_path_name +".png"
        uploaded_img_path1 =file_path_name1 +".jpg"

        #uploaded_img_path = query_path + datetime.now().isoformat.replace(":",".") + "_" +file1.filename +".png"
        img.save(uploaded_img_path)
        img1.save(uploaded_img_path1)

        # with open('e2.txt', 'w') as f:
        #     f.write(x)

        return make_response(uploaded_img_path1)



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
        with open(query_image,'rb') as f:
            contents=f.read()
        fs.put(contents,filename=input_image)

        return render_template('index.html',query_path=imagename,scores=seo_filter)
        #return make_response('matching images are {}'.format(filter_image))
    else :
        return render_template('index.html')
        #b=os.path.join(present_dir,'index.html')





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
        with open(query_image,'rb') as f:
            contents=f.read()
        fs.put(contents,filename=input_image)

        return render_template('index.html',query_path=imagename,scores=seo_filter)
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
        with open(query_image,'rb') as f:
            contents=f.read()
        fs.put(contents,filename=input_image)
        return render_template('index.html',query_path=imagename,scores=seo_filter)

        #return render_template('index.html',query_path=imagename,scores = seo_filter)

@app.route('/testt')
def hello_world1():
    x=fs.find()
    c=[(f.filename)for f in x]

    return make_response("hlo{}".format(c))


@app.route('/')
def hello_world():
    x=fs.find()
    i=0
    for f in x:
        i=i+1

    return make_response("ok{}".format(i))

