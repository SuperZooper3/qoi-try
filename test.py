import decode
import encode
import compPng
import os

def test_decode():
    for filename in os.listdir("refference/"):
        if filename.endswith(".jpg") or filename.endswith(".png"): # We have an image
            decode.fromQoi(filename.split('.')[0]+'.qoi')
            assert compPng.compPng("refference/"+filename,'imgRevQoi'+'/'+filename)
    return True

def test_encode():
    for filename in os.listdir("refference/"):
        if filename.endswith(".jpg") or filename.endswith(".png"): # We have an image
            encode.toQoi(filename.split('.')[0])
            decode.fromQoi(filename.split('.')[0]+'.qoi')
            print(filename)
            assert compPng.compPng("refference/"+filename,'imgRevQoi'+'/'+filename)
    return True

if __name__ == "__main__":
    # test_decode()
    test_encode()
    print("Tests Passed")