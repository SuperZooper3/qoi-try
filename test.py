import decode
import compPng
import os

def test_decode():
    for filename in os.listdir("refference/"):
        if filename.endswith(".jpg") or filename.endswith(".png"): # We have an image
            decode.fromQoi(filename.split('.')[0]+'.qoi')
            assert compPng.compPng("refference/"+filename,'imgRevQoi'+'/'+filename)
    return True

if __name__ == "__main__":
    test_decode()
    print("Tests Passed")