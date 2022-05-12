# qoi-try
My shot at making a QOI encoder and decoder

https://qoiformat.org/qoi-specification.pdf

## How to use

1. Put images (PNG or JPEG) in a folder.
2. Set that folder as `in_directory` inthe `loadToBytes.py` file.
3. Run `python3 loadToBytes.py` to encode the images into raw RGBA bytes.
4. In `encode.py` set `toQoi("imgBits/kodim23","imgQoi/kodim23.qoi", debug=False)` to have whatever bytes file you want aswell as the name and location of the ouput QOI file.
5. Run `python3 encode.py` to encode the bytes into a QOI image.
6. You can also use `python3 decode.py` to decode the QOI image which will save an immage in `imgRevQoi/` with the decoded png.

## Tests and Future Features
Currently, you will notice the tests dont pass even though the images are identical. This is because my encoder allways encodes as RGBA as I didnt find a clean way of figuring out if a PNG has 3 or 4 channels. This means the array comparrisons used to check if the encoded version are identical fails due to having 4 values instead of 3. This could be fixed later.
