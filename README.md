# pi-facedetect-security-camera

## Raspberry Pi security camera with face detection

This is a simple raspberry pi camera that detects motion and once it does tries to match to faces that it already know. This is all based on the work from pyimagesearch by Adrian Rosebrock at https://www.pyimagesearch.com/

I put together a couple of his projects together to get this to work

Example of how to run

python webstreaming.py --ip 127.0.0.1 --port 8080 -e encodings.new -c models\haarcascade_frontalface_default.xml

The project is using [dlib](http://dlib.net/compile.html) and a wrapper around it [face_recognition](https://github.com/ageitgey/face_recognition) (Here is how to prep your raspberrypi), credit to [Adam Geitgey face_recognition](https://github.com/ageitgey)

## Installation  instructions:

sudo apt-get update
sudo apt-get upgrade
sudo apt-get install build-essential \
    cmake \
    gfortran \
    git \
    wget \
    curl \
    graphicsmagick \
    libgraphicsmagick1-dev \
    libatlas-dev \
    libavcodec-dev \
    libavformat-dev \
    libboost-all-dev \
    libgtk2.0-dev \
    libjpeg-dev \
    liblapack-dev \
    libswscale-dev \
    pkg-config \
    python3-dev \
    python3-numpy \
    python3-pip \
    zip
sudo apt-get clean

**Install the picamera python library with array support (if you are using a camera):**

sudo apt-get install python3-picamera
sudo pip3 install --upgrade picamera[array]

**Temporarily enable a larger swap file size (so the dlib compile won't fail due to limited memory):

sudo nano /etc/dphys-swapfile

< change CONF_SWAPSIZE=100 to CONF_SWAPSIZE=1024 and save / exit nano >

sudo /etc/init.d/dphys-swapfile restart

**Download and install dlib v19+:**

mkdir -p dlib
git clone -b --single-branch https://github.com/davisking/dlib.git dlib/
cd ./dlib
sudo python3 setup.py install --compiler-flags "-mfpu=neon"

**Install face_recognition:**

sudo pip3 install face_recognition

**Revert the swap file size change now that dlib is installed:**

sudo nano /etc/dphys-swapfile

< change CONF_SWAPSIZE=1024 to CONF_SWAPSIZE=100 and save / exit nano >

sudo /etc/init.d/dphys-swapfile restart

**Download the face recognition code examples:**

git clone --single-branch https://github.com/ageitgey/face_recognition.git
cd ./face_recognition/examples
python3 facerec_on_raspberry_pi.py

