#airsim_api
#helper functions for airsims

import imp
from eventapi import AirSimEventGen
import cv2

image = AirSimEventGen.visualize_events()
print(image)
