# coding:utf-8
import os
import lmdb  # install lmdb by "pip install lmdb"
import cv2
import re
from PIL import Image
import numpy as np
import imghdr


def checkImageIsValid(imageBin):
    if imageBin is None:
        return False
    try:
        imageBuf = np.fromstring(imageBin, dtype=np.uint8)
        img = cv2.imdecode(imageBuf, cv2.IMREAD_GRAYSCALE)
        imgH, imgW = img.shape[0], img.shape[1]
    except:
        return False
    else:
        if imgH * imgW == 0:
            return False
    return True


def writeCache(env, cache):
    with env.begin(write=True) as txn:
        for k, v in cache.items():
            txn.put(str(k).encode('utf-8'), str(v).encode('utf-8'))
        # or
        #    if (isinstance(v, bytes)):
        #        txn.put(k.encode(), v)
        #    else:
        #        txn.put(k.encode(), v.encode())
        # both are ok.

def createDataset(outputPath, imagePathList, labelList, lexiconList=None, checkValid=True):
    """
    Create LMDB dataset for CRNN training.
    ARGS:
        outputPath    : LMDB output path
        imagePathList : list of image path
        labelList     : list of corresponding groundtruth texts
        lexiconList   : (optional) list of lexicon lists
        checkValid    : if true, check the validity of every image
    """
    assert (len(imagePathList) == len(labelList))
    nSamples = len(imagePathList)
    env = lmdb.open(outputPath, map_size=40000000000)
    cache = {}
    cnt = 1
    for i in range(nSamples):
        imagePath = imagePathList[i].replace('\n', '').replace('\r\n', '')
        # print(imagePath)
        label = labelList[i]
        print(label)
        # if not os.path.exists(imagePath):
        #     print('%s does not exist' % imagePath)
        #     continue	

        with open(imagePath, 'rb') as f:
            imageBin = f.read()

        if checkValid:
            if not checkImageIsValid(imageBin):
                print('%s is not a valid image' % imagePath)
                continue
        imageKey = 'image-%09d' % cnt
        labelKey = 'label-%09d' % cnt
        cache[imageKey] = imageBin
        cache[labelKey] = label
        if lexiconList:
            lexiconKey = 'lexicon-%09d' % cnt
            cache[lexiconKey] = ' '.join(lexiconList[i])
        if cnt % 1000 == 0:
            writeCache(env, cache)
            cache = {}
            print('Written %d / %d' % (cnt, nSamples))
        cnt += 1
        print(cnt)
    nSamples = cnt - 1
    cache['num-samples'] = str(nSamples)
    writeCache(env, cache)
    print('Created dataset with %d samples' % nSamples)


if __name__ == '__main__':
    outputPath = "./lmdb"
    imgdata = open("E:/datasets/text/360label/360_train.txt", mode='rb')
    lines = list(imgdata)

    imgDir = 'E:/datasets/text/images/'
    imgPathList = []
    labelList = []
    for line in lines:
        imgPath = os.path.join(imgDir, line.split()[0].decode('utf-8'))
        imgPathList.append(imgPath)
        word = line.split()[1]
        labelList.append(word)
    createDataset(outputPath, imgPathList, labelList)
