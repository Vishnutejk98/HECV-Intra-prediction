# HECV-Intra-prediction

Prediction Algorithm Applied: HEVC intra prediction based on impainting algorithm

Approach Taken for Encoding and Decoding:

Encoding 
- Read the .y file and split it to the frames
- Read a frame apply intra prediction and then Quantize + dct algorithm for the encoding on the intra predicted frame 
- Stored the respective files generated during encoding ( .npy , .png , .txt , .bmp)
- Files Gained at the time of encryption as follows 
  - .npy = after applying intra prediction
  - .png = conversion of .npy to png
  - .txt = contains the encoded image information
  - .bmp = just and uncompred file image for reference
Decoding
- Decode with Quantize and store the frame 




Steps to follow to run the code:

Install In your ENV: conda install -c conda-forge pyopencl

Command to run on the bash:
conda run -n videocode convertvideo.py   
converts .y into readable frames 
Normal commands:
Activate your environment

Motion detection between the frames : 
-  Algorithm used is RLE: https://www.section.io/engineering-education/run-length-encoding-algorithm-in-python/#:~:text=Run%20Length%20Encoding%20is%20a,runs%20followed%20by%20the%20data.

Motion detection:
- To Demo Motion detection: python application.py 
- Output: View it in chrome the URL that is console logged 

Encode: 
- Command: python encode frameNumber 
- Sample Command: python encode 2
- Output: Image would be shown upfront

Decode:
- Command: python decode frameNumber 
- Sample Command: python decode 2
- Output: Image would be shown upfront
