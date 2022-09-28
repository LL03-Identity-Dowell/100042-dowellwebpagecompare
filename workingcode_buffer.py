
# A very simple Flask Hello World app for you to get started with...

from flask import Flask,make_response,request,render_template
import os
import glob
import cv2
import numpy as np
import imutils
import csv

present_dir=os.path.dirname(os.path.abspath(__file__))
app = Flask(__name__)

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
	def search(self, queryFeatures, limit = 10):
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
		return results[:limit]


	def chi2_distance(self, histA, histB, eps = 1e-10):
		# compute the chi-squared distance
		d = 0.5 * np.sum([((a - b) ** 2) / (a + b + eps)
			for (a, b) in zip(histA, histB)])
		# return the chi-squared distance
		return d




@app.route('/seo',methods=['POST','GET'])
def seo():
    if request.method == 'POST':

        file = request.files['query_img']
        query_path=os.path.join(present_dir,'static/Query')
        file.save(os.path.join(query_path,file.filename))
        query_image=(os.path.join(query_path,file.filename))
        imagename=os.path.join('static/Query',file.filename)
        cd = ColorDescriptor((8, 12, 3))
        # open the output index file for writing
        output = open("index.csv", "w")
        databasedir=os.path.join(present_dir,'static/dataset')
        #print("----image database -path----")
        #print(databasedir)
        # use glob to grab the image paths and loop over them
        for imagePath in glob.glob(databasedir + "/*.JPG"):    #for jpg images
        	# extract the image ID (i.e. the unique filename) from the image
        	# path and load the image itself
        	#print(imagePath)
        	imageID = imagePath[imagePath.rfind("/") + 1:]
        	image = cv2.imread(imagePath)
        	# describe the image
        	features = cd.describe(image)
        	# write the features to file
        	features = [str(f) for f in features]
        	output.write("%s,%s\n" % (imageID, ",".join(features)))
        # close the index file
        output.close()

        # initialize the image descriptor
        cd = ColorDescriptor((8, 12, 3))
        #query=input("enter the inputimagepath/inputimagename ")
        #load the query image and describe it
        #query=os.path.join(path,query)
        #print("---image path-----")
        #print(query)

        query = cv2.imread(query_image)
        features = cd.describe(query)
        # perform the search
        searcher = Searcher("index.csv")
        results = searcher.search(features)
        # display the query
        #cv2.imshow("Query", query)
        # loop over the results
        #print("-------")
        #print(path)
        #scores=[(score,resultID) for(score,resultID)in results]
        print("filtered image paths from data bases are")
        #print(scores)

        #for (score, resultID) in results:
        # 	# load the result image and display it
        #     #result = cv2.imread(args["result_path"] + "/" + resultID)
        #     result = cv2.imread(resultID)
        # 	cv2.imshow("Result", result)
        # 	cv2.waitKey(0)
        seo_filter=[]
        for (score, resultID) in results:
        # 	# load the result image and display it
              result =os.path.join('static/dataset',resultID)
              seo_filter=seo_filter+[(score,result)]

        return render_template('index.html',query_path=imagename,scores=seo_filter)

        #return make_response('matching images are {}'.format(seo_filter))
    else :
        return render_template('index.html')
        #b=os.path.join(present_dir,'index.html')


@app.route('/')
def hello_world():
    return 'Hello from Flask! for testing'

