#!/usr/bin/env python
from glob import glob
from flask import Flask, render_template, Response
import io
import os
from imageio import imread


import cv2
#import device
app = Flask(__name__)




# Read - file 
from YVideo import YUVReader
Ysize = [352,288]
Ystart = 0
Yend = 150
Yfps = 1
Yreader = YUVReader("akiyo_cif.y", Ysize, Ystart, Yend, Yfps, "out/",False)
Yframes = Yreader.frames




################################ IMAGE 2 RLE 

import numpy as np
import math

# import zigzag functions
from zigzag import *


import time 

def get_run_length_encoding(image):
    i = 0
    skip = 0
    stream = []    
    bitstream = ""
    image = image.astype(int)
    while i < image.shape[0]:
        if image[i] != 0:            
            stream.append((image[i],skip))
            bitstream = bitstream + str(image[i])+ " " +str(skip)+ " "
            skip = 0
        else:
            skip = skip + 1
        i = i + 1

    return bitstream


block_size = 8

# Quantization Matrix 
QUANTIZATION_MAT = np.array([[16,11,10,16,24,40,51,61],[12,12,14,19,26,58,60,55],[14,13,16,24,40,57,69,56 ],[14,17,22,29,51,87,80,62],[18,22,37,56,68,109,103,77],[24,35,55,64,81,104,113,92],[49,64,78,87,103,121,120,101],[72,92,95,98,112,100,103,99]])


###### CONFIG 
import numpy as np
import tools as tl
import time
bl_size = 4
dst = 'fig'
processor = 'numpy'
from PIL import Image


################################ RLE 2 IMAGE 



#flask code
@app.route('/')
def index():
    """Video streaming home page."""
    return render_template('index.html')


import time
def gen():
    global yuv2play
    global Yframes
    global Ystart
    global Yend
    #for i in range(yuv2play.frmCount):
    for i in range(Ystart,Yend):
        # get video frame
        #img = yuv2play.getFrm(i)
        img = imread(f"out/{i}_y.png")
        encode_return_code, image_buffer = cv2.imencode('.jpg', img)
        io_buf = io.BytesIO(image_buffer)
        
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + io_buf.read() + b'\r\n')
        time.sleep(3)





# Parameters for Shi-Tomasi corner detection
feature_params = dict(maxCorners = 300, qualityLevel = 0.2, minDistance = 2, blockSize = 7)
# Parameters for Lucas-Kanade optical flow
lk_params = dict(winSize = (15,15), maxLevel = 2, criteria = (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 0.03))
# The video feed is read in as a VideoCapture object

# Variable for color to draw optical flow track
color = (0, 255, 0)
# Finds the strongest corners in the first frame by Shi-Tomasi method - we will track the optical flow for these corners
# https://docs.opencv.org/3.0-beta/modules/imgproc/doc/feature_detection.html#goodfeaturestotrack
# Creates an image filled with zero intensities with the same dimensions as the frame - for later drawing purposes




def motion():
    global yuv2play
    global Yframes
    global Ystart
    global Yend
    #first_frame = yuv2play.getFrm(0)
    first_frame = imread(f"out/{0}_y.png")
    prev_gray = first_frame
    prev = cv2.goodFeaturesToTrack(prev_gray, mask = None, **feature_params)
    mask = np.zeros_like(first_frame)

    #for i in range(yuv2play.frmCount):
    for i in range(Ystart,Yend):

        # get video frame
        #frame = yuv2play.getFrm(i)
        frame = imread(f"out/{i}_y.png")
        
        # Converts each frame to grayscale - we previously only converted the first frame to grayscale
        gray = frame
        # Calculates sparse optical flow by Lucas-Kanade method
        # https://docs.opencv.org/3.0-beta/modules/video/doc/motion_analysis_and_object_tracking.html#calcopticalflowpyrlk
        prev = cv2.goodFeaturesToTrack(prev_gray, mask = None, **feature_params)
        next, status, error = cv2.calcOpticalFlowPyrLK(prev_gray, gray, prev, None, **lk_params)
        # Selects good feature points for previous position
        good_old = prev[status == 1].astype(int)
        # Selects good feature points for next position
        good_new = next[status == 1].astype(int)
        # Draws the optical flow tracks
        for i, (new, old) in enumerate(zip(good_new, good_old)):
            # Returns a contiguous flattened array as (x, y) coordinates for new point
            a, b = new.ravel()
            # Returns a contiguous flattened array as (x, y) coordinates for old point
            c, d = old.ravel()
            # Draws line between new and old position with green color and 2 thickness
            mask = cv2.line(mask, (a, b), (c, d), color, 2)
            # Draws filled circle (thickness of -1) at new position with green color and radius of 3
            frame = cv2.circle(frame, (a, b), 3, color, -1)
        # Overlays the optical flow tracks on the original frame
        output = cv2.add(frame, mask)
        # Updates previous frame
        prev_gray = gray.copy()
        # Updates previous good feature points
        prev = good_new.reshape(-1, 1, 2)
        # Opens a new window and displays the output frame
        encode_return_code, image_buffer = cv2.imencode('.jpg', output)
        io_buf = io.BytesIO(image_buffer)
        yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + io_buf.read() + b'\r\n')
        time.sleep(3)




@app.route('/motion_feed')
def motion_feed():
    """Video streaming route. Put this in the src attribute of an img tag."""
    return Response(
        motion(),
        mimetype='multipart/x-mixed-replace; boundary=frame'
    )

@app.route('/raw_video')
def raw_video():
    """Video streaming route. Put this in the src attribute of an img tag."""
    return Response(
        gen(),
        mimetype='multipart/x-mixed-replace; boundary=frame'
    )

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, threaded=True)
    
