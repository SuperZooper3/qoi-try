# Based off of https://qoiformat.org/qoi-specification.pdf
import time
import numpy as np
from PIL import Image

# Defenitions
QOI_OP_RGB = 0b11111110
QOI_OP_RGBA = 0b11111111
QOI_OP_INDEX = 0b00
QOI_OP_DIFF = 0b01
QOI_OP_LUMA = 0b10
QOI_OP_RUN = 0b11

def QoiPixelHash(px):
    if len(px) == 3: 
        r,g,b = px
        a = 255
    else: r,g,b,a = px
    return (r * 3 + g * 5 + b * 7 + a * 11) % 64

def reverseDiff(lastPx, d):
    out = list(lastPx)
    for i in range(len(d)):
        out[i]+= d[i]
    return out

def fromQoi(filename, outfilename, debug = False):
    """
    Decode a QOI image, returning a 2d array of the pixels and saving an image at the outfilename directory
    filename: str. Ex: "images/bird.qoi"
    outfilename: str. Ex: "outImages/bird.png"
    debug: bool. If you want debug printing for each chunk met
    """
    with open(filename,"rb") as in_f:
        magic = in_f.read(4)
        assert(magic == b'qoif') # Assert that the file has the correct magic at it's head
        width_b = in_f.read(4) # Read a uint-32 for the width
        heigh_b = in_f.read(4) # Read a uint-32 for the height
        width = int.from_bytes(width_b,byteorder='big')
        height = int.from_bytes(heigh_b,byteorder='big')

        channels_b = in_f.read(1) # Read a uint-8 for the number of channels (either 3 or 4)
        colorspace_b = in_f.read(1) # Read a uint-8 for the colorspace (either 0 or 1)
        channels = int.from_bytes(channels_b,byteorder='big')
        colorspace = int.from_bytes(colorspace_b,byteorder='big')

        if debug: print("Head:",width,height,channels,colorspace)

        total_px = width * height
        
        pxls = [] # The 2d array of pixels
        pxl_Stream = [] # A buffer of all the pixels in the working row, and can be inserted into pxls
        n = 0 # Pixel read head

        # Decoder data
        if channels == 3:
            last_px = [0,0,0]
        else:
            last_px = [0,0,0,255]
        prev_pxs = [[0]*channels] * 64

        while n < total_px:
            # Step 1 Take in the first byte
            b1 = int.from_bytes(in_f.read(1),byteorder='big')
            px = [0]*channels
            # if debug: print(format(b1,'b'))
            if b1 == QOI_OP_RGB or b1 == QOI_OP_RGBA: # If we have 8-bit tags
                if b1 == QOI_OP_RGB:
                    # Step. 1-1.1 Take in the 3 more colour bytes
                    br = in_f.read(1)
                    bg = in_f.read(1)
                    bb = in_f.read(1)

                    # Step. 1-1.2 Convert colour bytes to RGB
                    r = int.from_bytes(br,byteorder='big')
                    g = int.from_bytes(bg,byteorder='big')
                    b = int.from_bytes(bb,byteorder='big')

                    # Step. 1-1.3 Write to the bufer 
                    px = [r,g,b]
                    # If we have 4 channels, add 255 as the alpha
                    if channels == 4: 
                        px.append(last_px[3]) # The alpha value remains unchanged from the previous pixel. :)
                    if debug: print("RGB",px)
                    n += 1
                    pxl_Stream.append(px)
                else: # We have an RGBA pair
                    # Step. 1-2.1 Take in the 3 more colour bytes
                    br = in_f.read(1)
                    bg = in_f.read(1)
                    bb = in_f.read(1)
                    ba = in_f.read(1)

                    # Step. 1-2.2 Convert colour bytes to RGB
                    r = int.from_bytes(br,byteorder='big')
                    g = int.from_bytes(bg,byteorder='big')
                    b = int.from_bytes(bb,byteorder='big')
                    a = int.from_bytes(ba,byteorder='big')
                    # Step. 1-2.3 Write to the bufer 
                    px = [r,g,b,a]
                    if debug: print("RGBA",px)
                    n += 1
                    pxl_Stream.append(px)
            else: # If we have a 2 bit tag
                # Process the tag
                tag = b1 >> 6 # Take just the first 2 bits since we truncate away the first 6 
                # Check the tag against all of the op codes
                if tag == QOI_OP_INDEX:
                    data = b1 & 0b00111111 # 6 Bit Mask to read the data
                    px = prev_pxs[data]
                    if debug: print("INDEX",data,px)
                    n += 1
                    pxl_Stream.append(px)
                elif tag == QOI_OP_RUN:
                    data = b1 & 0b00111111 # 6 Bit Mask to read the data
                    run = data + 1 # The run is stored with a -1 bias, this counters that
                    px = last_px
                    if debug: print("RUN",run,px)
                    n += run
                    pxl_Stream.extend([px]*run)
                elif tag == QOI_OP_DIFF:
                    data = b1 & 0b00111111 # 6 Bit Mask to read the data
                    dr = ((data & 0b00110000) >> 4)-2 # -2 Bias
                    dg = ((data & 0b00001100) >> 2)-2
                    db = ((data & 0b00000011))-2
                    px = reverseDiff(list(last_px),[dr,dg,db])
                    if debug: print("DIFF",last_px,dr,dg,db,px)
                    n += 1
                    pxl_Stream.append(px)
                elif tag == QOI_OP_LUMA:
                    dg = (b1 & 0b00111111) -32 # 6 Bit Mask to read the green difference with a bias of 32
                    b2 = int.from_bytes(in_f.read(1),byteorder='big')
                    dr = ((b2 & 0b11110000) >> 4) -8 + dg
                    db = ((b2 & 0b00001111)) -8 + dg
                    px = reverseDiff(list(last_px),[dr,dg,db])
                    if debug: print("LUMA",dr,dg,db,px)
                    n += 1
                    pxl_Stream.append(px)
                else:
                    if debug: print("Unknown Code",format(b1,'b'))
                    exit()
            # Warp up the processing of the chunk:
            # Set the last px
            last_px = list(px)
            
            prev_pxs[QoiPixelHash(px)] = px
            if len(pxl_Stream) >= width:
                pxls.append(pxl_Stream[0:width])
                pxl_Stream = pxl_Stream[width:]
        
        in_f.close()
        # Turn it into an np image
        array = np.array(pxls, dtype=np.uint8)
        # Use PIL to create an image from the new array of pixels
        new_image = Image.fromarray(array)
        new_image.save(outfilename)

        return pxls # Return it anyways


if __name__ == "__main__":
    fromQoi("refference/kodim23.qoi","imgRevQoi/kodim23.png", debug=False)