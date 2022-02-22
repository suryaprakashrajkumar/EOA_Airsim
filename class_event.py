from glob import glob
import numpy as np
import airsim
import time
import cv2
import matplotlib.pyplot as plt
import argparse
import sys, signal
import pandas as pd
import pickle
from event_simulator import *


class AirSimEventGen:
    def __init__(self, W, H, save=False, debug=False):
        self.ev_sim = EventSimulator(W, H)
        self.W = W
        self.H = H

        self.image_request = airsim.ImageRequest(
            "0", airsim.ImageType.Scene, False, False
        )
        

        self.client = airsim.VehicleClient()
        self.client.confirmConnection()
        self.init = True
        self.start_ts = None
        self.rawImage = self.client.simGetImage("0", airsim.ImageType.Scene)
        self.png = cv2.imdecode(airsim.string_to_uint8_array(self.rawImage), cv2.IMREAD_UNCHANGED)
        self.rgb_image_shape = [H, W, 3]
        self.debug = debug
        self.save = save
        self.fourcc = cv2.VideoWriter_fourcc(*'XVID')
        self.out = cv2.VideoWriter('outputevent.avi', self.fourcc, 20.0, (640, 480))

        self.event_file = open("events.pkl", "ab")
        self.event_fmt = "%1.7f", "%d", "%d", "%d"

        if debug:
            self.fig, self.ax = plt.subplots(1, 1)

    def visualize_events(self, event_img):
        self.rawImage = self.client.simGetImage("0", airsim.ImageType.Scene)
        self.png = cv2.imdecode(airsim.string_to_uint8_array(self.rawImage), cv2.IMREAD_UNCHANGED)
        event_img = self.convert_event_img_rgb(event_img)
        #cv2.imshow("Event", event_img)
        self.png = event_img
        global image
        image = event_img
        #cv2.imshow("RGB", self.png)
        #cv2.waitKey(1)
        return event_img

    def convert_event_img_rgb(self, image):
        image = image.reshape(self.H, self.W)
        out = np.zeros((self.H, self.W, 3), dtype=np.uint8)
        out[:, :, 0] = np.clip(image, 0, 1) * 255
        out[:, :, 2] = np.clip(image, -1, 0) * -255

        return out

    def _stop_event_gen(self, signal, frame):
        print("\nCtrl+C received. Stopping event sim...")
        self.event_file.close()
        sys.exit(0)