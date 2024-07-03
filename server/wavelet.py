import numpy as np
import pywt
import cv2


def w2d(img, mode="hear", level=1):
    imarray = img
    imarray = cv2.cvtColor(imarray, cv2.COLOR_RGB2GRAY)
    imarray = np.float32(imarray)
    imarray /= 255

    coeffs = pywt.wavedec2(imarray, mode, level=level)
    coeffs_h = list(coeffs)
    coeffs_h[0] *= 0

    imarray_h = pywt.waverec2(coeffs_h, mode)
    imarray_h *= 255
    imarray_h = np.uint8(imarray_h)

    return imarray_h
