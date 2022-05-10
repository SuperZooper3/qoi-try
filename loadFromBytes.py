# This file converts all images in /imgSource to bye representations of all their data in /imgBits
# This is just used to test if the loadToBytes was done correctly
import os
import numpy as np
from PIL import Image

in_directory = 'imgBits'
out_directory = 'imgRev'

def loadFrom(filename):
    # Get the size of the image
    size = []
    with open(in_directory+"/"+filename+".head") as f:
        size.append(int(f.readline()))
        size.append(int(f.readline()))
    
    with open(in_directory+"/"+filename,"rb") as f:
        rgb = []
        for y in range(size[1]):
            row = []
            for x in range(size[0]):
                colours = [int.from_bytes(f.read(1), byteorder="big") for i in range(3)]
                row.append(colours)
            rgb.append(row)

    # VISUALISATION OF CONVERTED
    # Convert the pixels into an array using numpy
    array = np.array(rgb, dtype=np.uint8)

    # Use PIL to create an image from the new array of pixels
    new_image = Image.fromarray(array)
    new_image.save(out_directory+"/"+filename+'rev.png')

for filename in os.listdir(in_directory):
    if filename.endswith("") and not filename.endswith(".head"):
        print(filename)
        loadFrom(filename)