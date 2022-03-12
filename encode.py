#!/usr/bin/env python
from glob import glob
import io
import os
from imageio import imread


import cv2
#import device



import sys





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
processor = 'numpy'
from PIL import Image

from IPython.display import display
from IPython.display import Image as Ing
def encode(i):

    filename = f"out/{i}_y.png"
    filenametowriteNPY = f"algoapplied/{i}_y"
    filenametowritePNG = f"algopng/{i}_y.png"
    encodedFile = f"encoded/{i}_y.txt"
    uncompressed = f"uncompressed/{i}_y.bmp"

    img = tl.read_file(filename)
    img = tl.pad(img, bl_size)
    shape = np.shape(img)
    block = tl.break_block(img, bl_size)
    predict, mode_predict = tl.inpainting(block, bl_size, processor = processor)
    predict = tl.group_block(predict, bl_size, shape)
    np.save(filenametowriteNPY, predict)
    img = np.load(filenametowriteNPY+".npy")
    img = Image.fromarray(np.uint8(img))
    img.save(filenametowritePNG)
    


    img = imread(filenametowritePNG)
    

    #img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    #You can try with this matrix to understand working of DCT
    #img = np.array([[255,255,227,204,204,203,192,217],[215,189,167,166,160,135,167,244],[169,115,99,99,99,82,127,220],[146,90,86,88,84,63,195,189],[255,255,231,239,240,182,251,232],[255,255,21,245,226,169,229,247],[255,255,222,251,174,209,174,163],[255,255,221,184,205,248,249,220]])


    # get size of the image
    [h , w] = img.shape



    # No of blocks needed : Calculation

    height = h
    width = w
    h = np.float32(h) 
    w = np.float32(w) 

    nbh = math.ceil(h/block_size)
    nbh = np.int32(nbh)

    nbw = math.ceil(w/block_size)
    nbw = np.int32(nbw)


    # Pad the image, because sometime image size is not dividable to block size
    # get the size of padded image by multiplying block size by number of blocks in height/width

    # height of padded image
    H =  block_size * nbh

    # width of padded image
    W =  block_size * nbw

    # create a numpy zero matrix with size of H,W
    padded_img = np.zeros((H,W))

    # copy the values of img into padded_img[0:h,0:w]
    # for i in range(height):
    #         for j in range(width):
    #                 pixel = img[i,j]
    #                 padded_img[i,j] = pixel

    # or this other way here
    padded_img[0:height,0:width] = img[0:height,0:width]

    cv2.imwrite(uncompressed, np.uint8(padded_img))



    # start encoding:
    # divide image into block size by block size (here: 8-by-8) blocks
    # To each block apply 2D discrete cosine transform
    # reorder DCT coefficients in zig-zag order
    # reshaped it back to block size by block size (here: 8-by-8)

    for i in range(nbh):
        
            # Compute start and end row index of the block
            row_ind_1 = i*block_size                
            row_ind_2 = row_ind_1+block_size
            
            for j in range(nbw):
                
                # Compute start & end column index of the block
                col_ind_1 = j*block_size                       
                col_ind_2 = col_ind_1+block_size
                            
                block = padded_img[ row_ind_1 : row_ind_2 , col_ind_1 : col_ind_2 ]
                        
                # apply 2D discrete cosine transform to the selected block                       
                DCT = cv2.dct(block)            

                DCT_normalized = np.divide(DCT,QUANTIZATION_MAT).astype(int)            
                
                # reorder DCT coefficients in zig zag order by calling zigzag function
                # it will give you a one dimentional array
                reordered = zigzag(DCT_normalized)

                # reshape the reorderd array back to (block size by block size) (here: 8-by-8)
                reshaped= np.reshape(reordered, (block_size, block_size)) 
                
                # copy reshaped matrix into padded_img on current block corresponding indices
                padded_img[row_ind_1 : row_ind_2 , col_ind_1 : col_ind_2] = reshaped
    
    arranged = padded_img.flatten()

    # Now RLE encoded data is written to a text file (You can check no of bytes in text file is very less than no of bytes in the image
    # THIS IS COMPRESSION WE WANTED, NOTE THAT ITS JUST COMPRESSION DUE TO RLE, YOU CAN COMPRESS IT FURTHER USING HUFFMAN CODES OR MAY BE 
    # REDUCING MORE FREQUENCY COEFFICIENTS TO ZERO)

    bitstream = get_run_length_encoding(arranged)

    # Two terms are assigned for size as well, semicolon denotes end of image to reciever
    bitstream = str(padded_img.shape[0]) + " " + str(padded_img.shape[1]) + " " + bitstream + ";"

    # Written to image.txt
    file1 = open(encodedFile,"w")
    file1.write(bitstream)
    file1.close()
    one= Image.open(  filenametowritePNG)
    one.show()
    one= Image.open( uncompressed)
    one.show()
    print("Completed Frame -",i)

encode(sys.argv[1])
