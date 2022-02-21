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

parser = argparse.ArgumentParser(description="Simulate event data from AirSim")
parser.add_argument("--debug", action="store_true", default=True)
parser.add_argument("--save", action="store_true")
parser.add_argument("--height", type=int, default=144)
parser.add_argument("--width", type=int, default=256)
global image
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


if __name__ == "__main__":
    args = parser.parse_args()
    event_generator = AirSimEventGen(args.width, args.height, save=args.save, debug=args.debug)
    i = 0
    start_time = 0
    t_start = time.time()

    signal.signal(signal.SIGINT, event_generator._stop_event_gen)

    while True:
        image_request = airsim.ImageRequest("0", airsim.ImageType.Scene, False, False)


        response = event_generator.client.simGetImages([event_generator.image_request])
        while response[0].height == 0 or response[0].width == 0:
            response = event_generator.client.simGetImages(
                [event_generator.image_request]
            )

        ts = time.time() * 1000000000

        if event_generator.init:
            event_generator.start_ts = ts
            event_generator.init = False

        img = np.reshape(
            np.fromstring(response[0].image_data_uint8, dtype=np.uint8),
            event_generator.rgb_image_shape,
        )

        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY).astype(np.float32)
        # Add small number to avoid issues with log(I)
        img = cv2.add(img, 0.001)

        ts = time.time() * 1000000000
        ts_delta = (ts - event_generator.start_ts) * 1e-3

        # Event sim keeps track of previous image automatically
        event_img, events = event_generator.ev_sim.image_callback(img, ts_delta)

        if events is not None and events.shape[0] > 0:
            if event_generator.save:
                # Using pickle dump in a per-frame fashion to save time, instead of savetxt
                # Optimizations possible
                pickle.dump(events, event_generator.event_file)

            image = event_generator.visualize_events(event_img)
            print("*++++++*")
            print("******")
            cv2.imshow("Events", image)
            roi = image[40:104, 0:256]
            cv2.imshow("ROI", roi)
            cv2.waitKey(1)



