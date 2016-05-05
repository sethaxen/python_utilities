"""Utility functions for plotting.

Author: Seth Axen
E-mail: seth.axen@gmail.com"""
from collections import deque


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


def lighten_rgb(rgb, p=0.):
    """Lighten RGB colors by percentage p of total."""
    h, s, v = rgb_to_hsv(rgb)
    print(rgb)
    print((h, s, v))
    hsv = (h, s, min(1, v + p))
    print(hsv)
    return hsv_to_rgb(hsv)
