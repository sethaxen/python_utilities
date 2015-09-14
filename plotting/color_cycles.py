"""Color cycles for maximum contrast/viewability.

Author: Seth Axen
E-mail: seth.axen@gmail.com"""
from collections import OrderedDict


# Reference:
# - KL Kelly. Color Eng. 1965. 3(6).
MAX_CONTRAST_COLORS = OrderedDict([
    # best colors to use
    ((1.000, 0.702, 0.000), 'vivid_yellow'),
    ((0.502, 0.243, 0.459), 'strong_purple'),
    ((1.000, 0.408, 0.000), 'vivid_orange'),
    ((0.651, 0.741, 0.843), 'very_light_blue'),
    ((0.757, 0.000, 0.125), 'vivid_red'),
    ((0.808, 0.635, 0.384), 'grayish_yellow'),
    ((0.506, 0.439, 0.400), 'medium_gray'),
    # not good for people with defective color vision,
    ((0.000, 0.490, 0.204), 'vivid_green'),
    ((0.965, 0.463, 0.557), 'strong_purplish_pink'),
    ((0.000, 0.325, 0.541), 'strong_blue'),
    ((1.000, 0.478, 0.361), 'strong_yellowish_pink'),
    ((0.325, 0.216, 0.478), 'strong_violet'),
    ((1.000, 0.557, 0.000), 'vivid_orange_yellow'),
    ((0.702, 0.157, 0.318), 'strong_purplish_red'),
    ((0.957, 0.784, 0.000), 'vivid_greenish_yellow'),
    ((0.498, 0.094, 0.051), 'strong_reddish_brown'),
    ((0.576, 0.667, 0.000), 'vivid_yellowish_green'),
    ((0.349, 0.200, 0.082), 'deep_yellowish_brown'),
    ((0.945, 0.227, 0.075), 'vivid_reddish_orange'),
    ((0.137, 0.173, 0.086), 'dark_olive_green')])

# Reference:
# - P Green-Armytage. Colour: Design & Creativity. 2010. 5(10).
COLOR_ALPHABET = OrderedDict([
    ((0.941, 0.639, 1.000), 'amethyst'),
    ((0.000, 0.459, 0.863), 'blue'),
    ((0.600, 0.247, 0.000), 'caramel'),
    ((0.298, 0.000, 0.361), 'damson'),
    ((0.098, 0.098, 0.098), 'ebony'),
    ((0.000, 0.361, 0.192), 'forest'),
    ((0.169, 0.808, 0.282), 'green'),
    ((1.000, 0.800, 0.600), 'honeydew'),
    ((0.502, 0.502, 0.502), 'iron'),
    ((0.580, 1.000, 0.710), 'jade'),
    ((0.561, 0.486, 0.000), 'khaki'),
    ((0.616, 0.800, 0.000), 'lime'),
    ((0.761, 0.000, 0.533), 'mallow'),
    ((0.000, 0.200, 0.502), 'navy'),
    ((1.000, 0.643, 0.020), 'orpiment'),
    ((1.000, 0.659, 0.733), 'pink'),
    ((0.259, 0.400, 0.000), 'quagmire'),
    ((1.000, 0.000, 0.063), 'red'),
    ((0.369, 0.945, 0.949), 'sky'),
    ((0.000, 0.600, 0.561), 'turquoise'),
    ((0.878, 1.000, 0.400), 'uranium'),
    ((0.455, 0.039, 1.000), 'violet'),
    ((0.600, 0.000, 0.000), 'wine'),
    ((1.000, 1.000, 0.502), 'xanthin'),
    ((1.000, 1.000, 0.000), 'yellow'),
    ((1.000, 0.314, 0.020), 'zinnia')])
