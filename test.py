import decode
import encode
import compPng
import loadToBytes
import os

def test_decode():
    for filename in os.listdir("refference/"):
        print(filename)
        if filename.endswith(".jpg") or filename.endswith(".png"): # We have an image
            decode.fromQoi("refference/"+filename.split('.')[0]+'.qoi','imgRevQoi'+'/'+filename)
            assert compPng.compPng("refference/"+filename,'imgRevQoi'+'/'+filename)
    return True

def test_encode():
    for filename in os.listdir("refference/"):
        if filename.endswith(".jpg") or filename.endswith(".png"): # We have an image
            encode.toQoi("imgBits/"+filename.split('.')[0],"imgQoi/"+filename.split('.')[0]+'.qoi')
            decode.fromQoi("imgQoi/"+filename.split('.')[0]+'.qoi','imgRevQoi'+'/'+filename)
            print(filename)
            assert compPng.compPng("refference/"+filename,'imgRevQoi'+'/'+filename)
    return True

if __name__ == "__main__":
    test_decode()
    test_encode()
    print("Tests Passed")