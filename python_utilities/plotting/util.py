"""Utility functions for plotting.

Author: Seth Axen
E-mail: seth.axen@gmail.com"""
from collections import deque

import numpy as np


def rgb_to_hsv(rgb):
    """Convert RGB colors to HSV colors."""
    r, g, b = tuple(map(float, rgb))
    if any([r > 1, g > 1, b > 1]):
        r /= 255.
        g /= 255.
        b /= 255.
    mmax = max(r, g, b)
    mmin = min(r, g, b)
    c = mmax - mmin
    if (c == 0.):
        hp = 0.
    elif (mmax == r):
        hp = ((g - b) / c) % 6
    elif (mmax == g):
        hp = ((b - r) / c) + 2
    elif (mmax == b):
        hp = ((r - g) / c) + 4
    h = 60 * hp
    v = mmax
    if (c == 0):
        s = 0
    else:
        s = c / v
    return (h, s, v)


def hsv_to_rgb(hsv):
    """Convert HSV colors to RGB colors."""
    h, s, v = tuple(map(float, hsv))
    c = v * s
    m = v - c
    hp = h / 60.
    x = c * (1. - abs((hp % 2) - 1.))
    hp = int(hp)
    rgb = deque((c + m, x + m, m))
    if (hp % 2):
        rgb.reverse()
        rgb.rotate((hp - 3) / 2)
    else:
        rgb.rotate(hp / 2)
    return tuple(rgb)


def rgb_to_yuv(rgb):
    """Convert RGB colors to Y'UV colors, useful for comparison."""
    rgbv = np.array(rgb).reshape(3, 1)
    if np.any(rgbv > 1.):
        rgbv = rgbv / 255.
    yuv = np.dot(np.array([[ .299,    .587,    .114],
                           [-.14713, -.28886,  .436],
                           [ .615,   -.51499, -.10001]], dtype=np.double),
                 rgbv)
    return list(yuv)


def yuv_to_rgb(yuv):
    """Convert Y'UV colors to RGB colors."""
    yuvv = np.array(yuv).reshape(3, 1)
    rgb = np.dot(np.array([[1., 0.,      1.13983],
                           [1., -.39465, -.58060],
                           [1., 2.03211, 0.]], dtype=np.double),
                 yuvv)
    return list(rgb)


def compute_yuv_dist(rgb1, rgb2):
    """Compute Euclidean Y'UV distance between RGB colors."""
    yuv1 = rgb_to_yuv(rgb1)
    yuv2 = rgb_to_yuv(rgb2)
    return float(sum((np.array(yuv1) - np.array(yuv2))**2)**.5)


def lighten_rgb(rgb, p=0.):
    """Lighten RGB colors by percentage p of total."""
    h, s, v = rgb_to_hsv(rgb)
    hsv = (h, s, min(1, v + p))
    return hsv_to_rgb(hsv)
