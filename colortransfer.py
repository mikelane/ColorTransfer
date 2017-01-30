#!/usr/bin/env python3

"""
Color Transfer Algorithm

Mike Lane
CS510 - Intro to Visual Computing
Project 1
01/30/2017

Implements the color transfer algorithm by Reinhard, et al. See
http://www.cs.tau.ac.il/~turkel/imagepapers/ColorTransfer.pdf for more information. Additional help with
helpful information was found at http://www.pyimagesearch.com/2014/06/30/super-fast-color-transfer-images/

For information about how to make OpenCV work with Python3 (on a Mac)
see http://www.pyimagesearch.com/2016/12/19/install-opencv-3-on-macos-with-homebrew-the-easy-way/.
"""

__author__ = "Mike Lane"
__copyright__ = "Copyright 2017, Michael Lane"
__license__ = "MIT"
__email__ = "mikelane@gmail.com"

import cv2
import numpy as np


def image_stats(image):
    # compute the mean and standard deviation of each channel
    l, a, b = cv2.split(image)

    # return the color statistics
    return l.mean(), l.std(), a.mean(), a.std(), b.mean(), b.std()


def color_transfer(source_fn, target_fn, result_fn):
    source = cv2.imread(source_fn)
    target = cv2.imread(target_fn)

    # Convert to Lab
    source = cv2.cvtColor(source, cv2.COLOR_BGR2LAB).astype('float32')
    target = cv2.cvtColor(target, cv2.COLOR_BGR2LAB).astype('float32')

    # compute color statistics for the source and target images
    l_mean_src, l_std_src, a_mean_src, a_std_src, b_mean_src, b_std_src = image_stats(source)
    l_mean_tgt, l_std_tgt, a_mean_tgt, a_std_tgt, b_mean_tgt, b_std_tgt = image_stats(target)

    # Separate the color layers of the target
    l, a, b = cv2.split(target)

    # Subtract out the mean of each layer
    l -= l_mean_tgt
    a -= a_mean_tgt
    b -= b_mean_tgt

    # Scale the layers by the standard deviation factors.
    l = (l_std_tgt / l_std_src) * l
    a = (a_std_tgt / a_std_src) * a
    b = (b_std_tgt / b_std_src) * b

    # Add in the mean of the source image.
    l += l_mean_src
    a += a_mean_src
    b += b_mean_src

    # Clip the output values to an 8-bit range
    l = np.clip(l, 0, 255)
    a = np.clip(a, 0, 255)
    b = np.clip(b, 0, 255)

    # Merge the l*a*b* colorspace and convert to RGB and return. Note, colors are
    # 8-bit unsigned ints.
    cv2.imwrite(result_fn, cv2.cvtColor(cv2.merge([l, a, b]).astype("uint8"), cv2.COLOR_LAB2BGR))


if __name__ == '__main__':
    source = 'data/Testing/Seattle Skyline.jpg'
    target = 'data/Mike/target_image.jpg'
    result = 'data/Testing/result_image.jpg'
    color_transfer(source, target, result)
