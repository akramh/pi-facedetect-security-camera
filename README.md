# pi-facedetect-security-camera
Raspberry Pi security camera with face detection

This is a simple raspberry pi camera that detects motion and once it does tries to match to faces that it already know. 


Example of how to run

python webstreaming.py --ip 127.0.0.1 --port 8080 -e encodings.new -c models\haarcascade_frontalface_default.xml