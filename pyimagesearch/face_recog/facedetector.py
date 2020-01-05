import cv2
import face_recognition

class FaceDetector:
	def __init__(self, encodings, model):

		#initialize model and encodings
		self.data = encodings
		self.detector = model

	
	def detect_face(self, gray, rgb):

		#detect faces in the grayscale frame
		rects = self.detector.detectMultiScale(gray, scaleFactor=1.1,
			minNeighbors=5, minSize=(30,30),
			flags=cv2.CASCADE_SCALE_IMAGE)
		
		# OpenCV returns bounding box coordinates in (x, y, w, h) order
		# # but we need them in (top, right, bottom, left) order, so we
		# # need to do a bit of reordering
		boxes = [(y, x + w, y + h, x) for (x, y, w, h) in rects]

		# compute the facial embeddings for each face bounding box
		encodings = face_recognition.face_encodings(rgb, boxes)
		names = []

		#loop over the facial embeddins
		for encoding in encodings:
			# attempt to match each face in the input image to our known encodings
			matches = face_recognition.compare_faces(self.data["encodings"], encoding)
			name = "Unknown"

			
			if True in matches:
				
				# find the indexes of all matched faces then initialize a
				# dictionary to count the total number of times a face
				# was matched
				matchIdxs =[i for (i, b) in enumerate(matches) if b]
				counts = {}

				# loop over the matched indexes and maintain a count for
				# each recognized face
				for i in matchIdxs:
					name = self.data["names"][i]
					counts[name] = counts.get(name, 0) + 1

					# determine the recognized face with the largest number
					# of votes (note: in the event of an unlikely tie Python
					# will select first entry in the dictionary)
					name = max(counts, key=counts.get)

			#update the list of names
			names.append(name)
		return zip(boxes,names)