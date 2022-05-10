# Based off of https://qoiformat.org/qoi-specification.pdf
import time

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

def CalcDiff(px_1,px_2):
    return [(px_1[i] - px_2[i]) % 256 for i in range(len(px_1))]

def toQoi(filename, outfilename, debug = False):
    """
    Encode a raw bit stream of pixel data (1 byte for each R G B A) into a QOI file
    filename: str. The name of the pixel data file "imgBits/kodim23"
    outfilename: str. The save location of the qoi file "imgQoi/kodim23.qoi"
    debug: bool. If you want debug printing for each chunk met
    """
    # Get the size of the image from the head
    size = []
    with open(filename+".head") as head_f:
        size.append(int(head_f.readline()))
        size.append(int(head_f.readline()))

    total_px = size[0]*size[1]
    
    in_f = open(filename, "rb")
    out_f = open(outfilename,"wb")

    channels = 4 # For now I dont know how to see if a png is rgb, or rgba. So will use RGBA by default

    # Write the header
    out_f.write(bytearray(b"qoif")) # This is the 4 byte magic
    out_f.write(bytearray(size[0].to_bytes(2, byteorder='big')).rjust(4, b'\0')) # Width
    out_f.write(bytearray(size[1].to_bytes(2, byteorder='big')).rjust(4, b'\0')) # Height
    out_f.write(bytearray(int(channels).to_bytes(2, byteorder='big'))[1:3]) # 3 for RGB, 4 for RGBA
    out_f.write(bytearray(int(0).to_bytes(2, byteorder='big'))[1:3]) # 0 for sRGB w/ linear alpha (idk exactly that this is)

    # Start encoding data

    last_px = [0, 0, 0, 255] # The last seen pixel, starts at 0, 0, 0, 255
    prev_pxs = [None] * 64 # A running hash-table based array of previously seen pixels

    run = 0

    # Repeat until we have done each pixel
    for i in range(total_px):
        # Read in the RGB values of the pixel
        px = [int.from_bytes(in_f.read(1), byteorder="big") for _ in range(channels)]
        px_HASH = QoiPixelHash(px)
        # print(px_HASH)
        px_DIFF = CalcDiff(px, last_px)
        
        # Step 0.5: Write runs if run over
        if run > 0 and px != last_px:
            d = (QOI_OP_RUN << 6) | (run-1)
            if debug: print("run",format(d,'b'))
            out_f.write(d.to_bytes(2, byteorder='big')[1:3])
            run = 0

        # Step 1: Check for run
        if px == last_px:
            run += 1
            # if debug: print("Run increase", px_HASH, run)
            if run == 62: # See note in spec on run
                d = (QOI_OP_RUN << 6) | (run-1)
                if debug: print("Run", format(d,'b'))
                out_f.write(d.to_bytes(2, byteorder='big')[1:3])
                run = 0
        
        # Step 2: Check for value in previously seen pixels
        elif prev_pxs[px_HASH] == px:
            d = (QOI_OP_INDEX << 6) | px_HASH
            if debug: print("Index",format(d,'b'))
            out_f.write(d.to_bytes(2, byteorder='big')[1:3])
        
        # Step 3: Try and express difference from last px
        elif px_DIFF[0] <= 1 and px_DIFF[0] >= -2 and px_DIFF[1] <= 1 and px_DIFF[1] >= -2 and px_DIFF[2] <= 1 and px_DIFF[2] >= -2 and px_DIFF[3] == 0:
            d = (QOI_OP_DIFF << 6) | ((px_DIFF[0]+2) << 4) | ((px_DIFF[1]+2) << 2) | ((px_DIFF[2]+2))
            if debug: print("Diff", format(d,'b'))
            out_f.write(d.to_bytes(2, byteorder='big')[1:3])

        # Step 4: Give up and draw the straight colour
        else:
            # If the alpha is the same as the last pixel, the doc says to encode as RGB
            if channels == 3 or px[3] == last_px[3]: # The channels == 3 is redundant here, but keeping for readability
                d = [QOI_OP_RGB,px[0],px[1], px[2]]
                if debug: print("Raw RGB",d)
                for v in d:
                    out_f.write(v.to_bytes(2, byteorder='big')[1:3])
            else: # Write an RGBA block
                d = [QOI_OP_RGBA,px[0],px[1], px[2],px[3]]
                if debug: print("Raw RGBA",d)
                for v in d:
                    out_f.write(v.to_bytes(2, byteorder='big')[1:3])

        # Once done encoding, set last_px to px
        last_px = px
        # Insert into "hash table"
        prev_pxs[px_HASH] = px

    if run > 0:
        d = (QOI_OP_RUN << 6) | (run-1)
        if debug: print("run",format(d,'b'))
        out_f.write(d.to_bytes(2, byteorder='big')[1:3])
        run = 0
        
    # Close the file with 7 * 0x00 and 0x01
    for _ in range(7): out_f.write(bytes([0]))
    out_f.write(bytes([1]))
    in_f.close()
    out_f.close()

if __name__ == "__main__":
    toQoi("imgBits/kodim23","imgQoi/kodim23.qoi", debug=False)