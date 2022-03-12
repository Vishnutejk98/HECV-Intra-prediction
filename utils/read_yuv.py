import cv2
import numpy as np

from tempfile import mkstemp

#implement 2D IDCT def idct2(a): return idct(idct(a.T, norm='ortho').T, norm='ortho')

from skimage.io import imread 
from skimage.color import rgb2gray 
import numpy as np 
import matplotlib.pylab as plt

#implement 2D DCT

from scipy.fftpack import dct, idct

#Importing Image module from PIL package

from PIL import Image 
import PIL

class VideoCaptureYUV:
    def __init__(self, filename, size):
        self.height, self.width = size
        self.frame_len = self.width * self.height * 3 / 2
        self.f = open(filename, 'rb')
        self.shape = (int(self.height*1.5), self.width)

    def read_raw(self):
        try:
            raw = self.f.read(self.frame_len)
            yuv = np.frombuffer(raw, dtype=np.uint8)
            yuv = yuv.reshape(self.shape)
        except Exception as e:
            #print(e)
            return False, None
        return True, yuv

    def read(self):
        ret, yuv = self.read_raw()
        print(ret)
        if not ret:
            return ret, yuv
        bgr = cv2.cvtColor(yuv, cv2.COLOR_YUV2BGR_I420)
        return ret, bgr

def dct2(a): 
    return dct(dct(a.T, norm='ortho').T, norm='ortho')

import subprocess as sp
import numpy as np

if __name__ == "__main__":
    filename = "example.yuv"
    size = (256, 256)
        
    command = ['ffmpeg', 
                '-f', 'rawvideo',
                '-framerate', '30', 
                '-s', '256x256', 
                '-pixel_format', 'yuv420p' ,
                '-i', filename ,
                '-c','copy', 
                '-f', 'segment', 
                '-segment_time', '0.01', 'frames/frames%d.yuv']

    pipe = sp.Popen(command, stdout = sp.PIPE, bufsize=10**8)

    raw_image = pipe.stdout.read(256*256*3)
    # transform the byte read into a numpy array
    image =  np.fromstring(raw_image, dtype='uint8')
    print(image.shape)
    # image = image.reshape((360,420,3))
    # throw away the data in the pipe's buffer.
    pipe.stdout.flush()

    # cap = VideoCaptureYUV(filename, size)
    
    # while 1:
    #     ret, frame = cap.read()
    #     print(ret)
    #     if ret==True:
    #         # DCT  
    #         # read the frame and convert it to grayscale 
    #         im = rgb2gray(frame) 
    #         imF = dct2(im) 
            
    #         cv2.imwrite() #this is just to test visually

    #         #quantize a frame 
    #         imF = imF.quantize(256) 
              
    #         #to show specified quantized frame just for testing
    #         imF.show() 

    #         #Inverse DCT            
    #         im2 = idct(imF)

    #         #to show specified IDCT frame just for testing
    #         im2.show() 
            
    #         #cv2.VideoWriter.write()
    #         #out.write(frame)
    #         #cv2.imwrite("frame_"+str(i)+'.yuv', video)
           
    #         cv2.imshow('frame',frame)
    #         cv2.waitKey(1)

            
           
    #     else:
    #         break