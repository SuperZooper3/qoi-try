# This file converts all images in /imgSource to bye representations of all their data in /imgBits
import os
from PIL import Image

in_directory = 'refference'
out_directory = 'imgBits'

def loadTo(filename):
    # Create the outfile
    outFile = open(out_directory+'/'+os.path.splitext(filename)[0], 'w')
    outFile.close()
    # Once made, open to write bytes
    outFile = open(out_directory+'/'+os.path.splitext(filename)[0], 'wb')
    
    # Ingest image
    im = Image.open(in_directory+"/"+filename)
    rgb_im = im.convert('RGBA')
    size = im.size

    # Write all da bits
    for y in range(size[1]):
        for x in range(size[0]):
            px = rgb_im.getpixel((x,y))
            # Write R, G B
            for v in px:
                d = bytearray(v.to_bytes(2, byteorder='big'))
                outFile.write(d[1:3])
    outFile.close()

    header = open(out_directory+'/'+os.path.splitext(filename)[0]+".head", 'w')
    header.write(str(im.width)+"\n")
    header.write(str(im.height))

for filename in os.listdir(in_directory):
    if filename.endswith(".jpg") or filename.endswith(".png"):
        print(filename)
        loadTo(filename)