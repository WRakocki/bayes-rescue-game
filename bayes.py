import sys
import random
import itertools
import numpy as np
import cv2 as cv

MAP_FILE = "cape_python.png"

SA1_CORNERS = (130, 265, 180, 315) #(LT X, LT Y, RB X, RB Y)
SA2_CORNERS = (80, 255, 130, 305) #(LT X, LT Y, RB X, RB Y)
SA3_CORNERS = (105, 205, 155, 255) #(LT X, LT Y, RB X, RB Y)