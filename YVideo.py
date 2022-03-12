from argparse import ArgumentParser
import subprocess
import os, sys, shutil
from os import listdir
from os.path import isfile, join
from imageio import imread
from utils.yuv_2_png import yuv_to_png

def get_file_extension(file_path):
    return file_path.split('/')[-1].split('.')[-1]

class YUVReader:
    '''
    A video reader for yuv, y and mp4 videos-
    :: Works ONLY with videos encoded in the YUV420 format
    :: mp4 videos are first converted to yuv420 
    Returns:
        A dictionary with keys corresponding to the video sequence indices.
        ------See how it's used below------
    '''
    def __init__(self, input_file, size=None, start=0, end=0,fps=10, out_dir='out/', clean=True) -> None:
        #Video sequence characteristics -> define carefully
        self.input = input_file
        self.out_dir=out_dir
        if not os.path.exists(self.out_dir):
            os.makedirs(self.out_dir)
        self.size = size
        self.start = start
        self.end = end
        self.fps =  fps
        self.clean=clean
        
        self.frames = {}
        self.n_frames = self.end-self.start
        if self.n_frames <= 0:
            print("[ERROR]: Number of frames must be greater than 0! Exiting..")
            sys.exit()
        self.ext = self._get_file_extension()
        self._read()
        
    def _get_file_extension(self):
        '''checks the file type of the video sequence'''
        return self.input.split('/')[-1].split('.')[-1]

    def _clean(self, idx):
        '''Cleans the temporary files created when readin yuv'''
        try:
            if os.path.isfile(f"{self.out_dir}/{idx}_y.png"):
                os.remove(f"{self.out_dir}/{idx}_y.png")
            if os.path.isfile(f"{self.out_dir}/{idx}_u.png"):
                os.remove(f"{self.out_dir}/{idx}_u.png")
            if os.path.isfile(f"{self.out_dir}/{idx}_v.png"):
                os.remove(f"{self.out_dir}/{idx}_v.png")
        except:
            return

    def _read_yuv(self, input):
        '''Reads frames from .yuv videos'''
        for idx in range(self.start, self.end):
            cmd = f"bash bash_utils/yuv_to_png.sh {input} {self.out_dir} {idx} bash_utils/convert_img.py {self.size[0]} {self.size[1]}"
            subprocess.call(cmd, shell=True)
            frame = {"y": imread(f"{self.out_dir}{idx}_y.png"),
                    "u": imread(f"{self.out_dir}{idx}_u.png"),
                    "v": imread(f"{self.out_dir}{idx}_v.png")}
            self.frames[idx] = frame
        if self.clean:
            shutil.rmtree(self.out_dir)

    def _read_y(self, input):
        '''Reads .y videos'''
        for idx in range(self.start, self.end):
            cmd = f"bash bash_utils/y_to_png.sh {input} {self.out_dir} {idx} bash_utils/convert_img.py {self.size[0]} {self.size[1]}"
            subprocess.call(cmd, shell=True)
            frame = {"y": imread(f"{self.out_dir}/{idx}_y.png")}
            self.frames[idx] = frame
        if self.clean:
            shutil.rmtree(self.out_dir) 

    def _read(self):
        '''Creates the actual sequence dictionary by reading the video frame by frame
            between the defined start and end indices(must be > 0)'''
        if self.ext =='yuv':
            #read directly the yuv file returning dictionaries with y,u and v key values
            self._read_yuv(self.input)
            
        if self.ext == 'y':
            #read luma channel only
            self._read_y(self.input)

        if self.ext == 'mp4':
            #convert losslessly to yuv then read
            out_yuv = self.out_dir+self.input.split('/')[-1].split('.')[0]+'.yuv'
            subprocess.call(['ffmpeg','-nostats','-loglevel','error','-i',self.input,out_yuv, '-r',str(self.fps)])
            #read the output yuv file between the defined frames
            self._read_yuv(out_yuv)