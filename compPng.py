# Compare the exact pixels of two images
from PIL import Image
import numpy as np

def compPng(a,b):
    im = Image.open(a)
    pixels = list(im.getdata())
    width, height = im.size
    pixels1 = [pixels[i * width:(i + 1) * width] for i in range(height)]
    im.close()

    im = Image.open(b)
    pixels = list(im.getdata())
    width, height = im.size
    pixels2 = [pixels[i * width:(i + 1) * width] for i in range(height)]
    im.close()

    return np.array_equal(pixels1,pixels2)