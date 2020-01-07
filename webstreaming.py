# USAGE
# python webstreaming.py --ip 0.0.0.0 --port 8000

# import the necessary packages
from pyimagesearch.motion_detection import SingleMotionDetector
from pyimagesearch.face_recog import FaceDetector
from pyimagesearch.keyclipwriter import KeyClipWriter
from imutils.video import VideoStream
from flask import Response
from flask import Flask
from flask import render_template
import threading
import argparse
import datetime
import imutils
import time
import pickle
import cv2
import json

# initialize the output frame and a lock used to ensure thread-safe
# exchanges of the output frames (useful for multiple browsers/tabs
# are viewing tthe stream)
outputFrame = None
lock = threading.Lock()

# initialize a flask object
app = Flask(__name__)

# initialize the video stream and allow the camera sensor to
# warmup
#vs = VideoStream(usePiCamera=1).start()
vs = VideoStream(src=0).start()
time.sleep(2.0)

@app.route("/")
def index():
	# return the rendered template
	return render_template("index.html")

def detect_motion(frameCount, data, model):
	# grab global references to the video stream, output frame, and
	# lock variables
	global vs, outputFrame, lock

	# initialize the motion detector and the total number of frames
	# read thus far
	md = SingleMotionDetector(accumWeight=0.1)
	fd = FaceDetector(data,model)

	total = 0

	red = (0,0,255)
	green = (0,255,0)

	lastUploaded = datetime.datetime.now()

	# loop over frames from the video stream
	while True:
		# read the next frame from the video stream, resize it,
		# convert the frame to grayscale, and blur it
		frame = vs.read()
		frame = imutils.resize(frame, width=400)
		gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
		gray = cv2.GaussianBlur(gray, (7, 7), 0)
		rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

		text = "no motion"
		color = red

		# grab the current timestamp and draw it on the frame
		timestamp = datetime.datetime.now()
		cv2.putText(frame, timestamp.strftime(
			"%A %d %B %Y %I:%M:%S%p"), (10, frame.shape[0] - 10),
			cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 0, 255), 1)

		# if the total number of frames has reached a sufficient
		# number to construct a reasonable background model, then
		# continue to process the frame
		if total > frameCount:
			# detect motion in the image
			motion = md.detect(gray)

			# cehck to see if motion was found in the frame
			if motion is not None:
				# unpack the tuple and draw the box surrounding the
				# "motion area" on the output frame
				text = "motion detected"
				color = green
				facedetected = fd.detect_face(gray,rgb)
				person = []

				#(thresh, (minX, minY, maxX, maxY)) = motion
				#cv2.rectangle(frame, (minX, minY), (maxX, maxY),green, 2)
				for ((top, right, bottom, left), name) in facedetected:
					cv2.rectangle(frame, (left, top), (right, bottom),(0, 255, 0), 2)
					y = top - 15 if top - 15 > 15 else top + 15
					cv2.putText(frame, name, (left, y), cv2.FONT_HERSHEY_SIMPLEX,0.75, (0, 255, 0), 2)
					person.append(name)

				if (timestamp - lastUploaded).seconds >= 5:
					for x in range(len(person)):
						print(person[x] + " was detected at ", timestamp, " total ", total, " framecount ", frameCount)
						lastUploaded = timestamp
				
		cv2.putText(frame, "{}".format(text), (10, 20),
		cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
		# update the background model and increment the total number
		# of frames read thus far
		md.update(gray)
		total += 1

		# acquire the lock, set the output frame, and release the
		# lock
		with lock:
			outputFrame = frame.copy()
		
def generate():
	# grab global references to the output frame and lock variables
	global outputFrame, lock

	# loop over frames from the output stream
	while True:
		# wait until the lock is acquired
		with lock:
			# check if the output frame is available, otherwise skip
			# the iteration of the loop
			if outputFrame is None:
				continue

			# encode the frame in JPEG format
			(flag, encodedImage) = cv2.imencode(".jpg", outputFrame)

			# ensure the frame was successfully encoded
			if not flag:
				continue

		# yield the output frame in the byte format
		yield(b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + 
			bytearray(encodedImage) + b'\r\n')

@app.route("/video_feed")
def video_feed():
	# return the response generated along with the specific media
	# type (mime type)
	return Response(generate(),
		mimetype = "multipart/x-mixed-replace; boundary=frame")

# check to see if this is the main thread of execution
if __name__ == '__main__':
	# construct the argument parser and parse command line arguments
	ap = argparse.ArgumentParser()
	ap.add_argument("-c", "--conf", required=True,
		help="path to the JSON configuration file")
	args = vars(ap.parse_args())

	conf = json.load(open(args["conf"]))

	data = pickle.loads(open(conf["encodings"], "rb").read())
	detector = cv2.CascadeClassifier(conf["cascade_model"])

	# start a thread that will perform motion detection
	t = threading.Thread(target=detect_motion, args=(
		conf["frame_count"],data, detector))
	t.daemon = True
	t.start()

	# start the flask app
	app.run(host=conf["ip_address"], port=conf["port"], debug=True,
		threaded=True, use_reloader=False)


# release the video stream pointer
vs.stop()