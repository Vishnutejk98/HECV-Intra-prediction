#!/bin/bash

src=$1
out_dir=$2
idx_frame=$3

# Absolute path of the python script to convert pgm to png
convert_img_python_path=$4

wdt=$5
hgt=$6

# Creating header for PGM files
stry="P5 $wdt $hgt 255"

LY=${#stry}
LY=$((LY+1))
echo  $stry> ${out_dir}headerY.bin

# Size for Y plane 
sizeY=$((wdt*hgt))
# Size for U and V plane
sizeUV=$((wdt*hgt/2))

block_size=$sizeUV
blockY=$(($sizeY/$block_size))
blockUV=$(($sizeUV/$block_size))


# yuv --> raw stream
# frame 0 (nothing is skipped, otherwise blockY+2*blockUV per frame)
skip=$(($idx_frame * ($blockY + 2 * $blockUV)))
dd skip=$skip count=$blockY  if=$src of=${out_dir}tempY.raw bs=$block_size &> /dev/null

recy=${out_dir}${idx_frame}_y.png

# raw stream --> pgm --> png
cat ${out_dir}headerY.bin ${out_dir}tempY.raw > ${out_dir}rec_y.pgm
python $convert_img_python_path ${out_dir}rec_y.pgm $recy &>/dev/null

# Remove intermediary files
rm ${out_dir}headerY.bin ${out_dir}tempY.raw ${out_dir}rec_y.pgm

