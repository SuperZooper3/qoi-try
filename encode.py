# Bassed off of https://qoiformat.org/qoi-specification.pdf
import time

in_directory = 'imgBits'
out_directory = 'imgQoi'

def QoiPixelHash(px):
    r,g,b = px
    return (r * 3 + g * 5 + b * 7) % 64

def CalcDiff(px_1,px_2):
    return [(px_1[i] - px_2[i]) % 256 for i in range(len(px_1))]

def toQoi(filename):
    # Get the size of the image from the head
    size = []
    with open(in_directory+"/"+filename+".head") as head_f:
        size.append(int(head_f.readline()))
        size.append(int(head_f.readline()))

    total_px = size[0]*size[1]
    
    in_f = open(in_directory+"/"+filename, "rb")
    out_f = open(out_directory+"/"+filename+".qoi","wb")


    # Write the header
    out_f.write(bytearray(b"qoif")) # This is the 4 byte magic
    out_f.write(bytearray(size[0].to_bytes(2, byteorder='big')).rjust(4, b'\0')) # Width
    out_f.write(bytearray(size[1].to_bytes(2, byteorder='big')).rjust(4, b'\0')) # Height
    out_f.write(bytearray(int(3).to_bytes(2, byteorder='big'))[1:3]) # 3 for RGB
    out_f.write(bytearray(int(0).to_bytes(2, byteorder='big'))[1:3]) # 0 for sRGB w/ linear alpha (idk exactly that this is)

    # Start encoding data

    last_px = [0, 0, 0] # The last seen pixel
    prev_pxs = [None] * 64 # A running hash-table bassed array of previously seen pixels
    run = 0

    # Repeat until we have done each pixel
    for i in range(total_px):
        # Read in the RGB values of the pixel
        px_RGB = [int.from_bytes(in_f.read(1), byteorder="big") for _ in range(3)]
        px_HASH = QoiPixelHash(px_RGB)
        px_DIFF = CalcDiff(px_RGB, last_px)

        # Step 1: Check for run
        if px_RGB == last_px:
            run += 1
            # print("Run increase", px_HASH, run)
            if run == 62: # See note in spec on run
                d = (0b11 << 6) | (run-1)
                out_f.write(d.to_bytes(2, byteorder='big')[1:3])
                run = 0
        
        # Step 2: Check for value in previously seen pixels
        elif prev_pxs[px_HASH] == px_RGB:
            d = (0b00 << 6) | px_HASH
            print("Prev",d)
            out_f.write(d.to_bytes(2, byteorder='big')[1:3])
        
        # Step 3: Try and express difference from last px
        elif px_DIFF[0] <= 1 and px_DIFF[0] >= -2 and px_DIFF[1] <= 1 and px_DIFF[1] >= -2 and px_DIFF[2] <= 1 and px_DIFF[2] >= -2:
            d = (0b11 << 6) | ((px_DIFF[0]+2) << 4) | ((px_DIFF[1]+2) << 2) | ((px_DIFF[2]+2))
            print("Diff", d)
            out_f.write(d.to_bytes(2, byteorder='big')[1:3])

        # Step 4: Give up and draw the straight RGB
        else:
            d = [0b11111110,px_RGB[0],px_RGB[1], px_RGB[2]]
            print("Raw RGB",d)
            for v in d:
                out_f.write(v.to_bytes(2, byteorder='big')[1:3])

        # Step 1.5: Write runs if run over
        if run > 0 and px_RGB != last_px:
            d = (0b11 << 6) | (run-1)
            out_f.write(d.to_bytes(2, byteorder='big'))
            run = 0

        # Once done encoding, set last_px to px
        last_px = px_RGB
        # Insert into "hash table"
        prev_pxs[px_HASH] = px_RGB
        time.sleep(0.01)
        
    # Close the file with 7 * 0x00 and 0x01
    for _ in range(7): out_f.write(bytes([0]))
    out_f.write(bytes([1]))


    

toQoi("kodim10")