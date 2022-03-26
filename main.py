from class_event import *
from glob import glob
import numpy as np
import airsim
import time
import cv2
import matplotlib.pyplot as plt
import sys, signal
from api3 import *

import pickle
from event_simulator import *

event_generator = AirSimEventGen(256, 144, save= False,  debug=True)
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
    img = cv2.add(img, 0.001)

    ts = time.time() * 1000000000
    ts_delta = (ts - event_generator.start_ts) * 1e-3
    event_img, events = event_generator.ev_sim.image_callback(img, ts_delta)

    if events is not None and events.shape[0] > 0:
        if event_generator.save:
            pickle.dump(events, event_generator.event_file)

        image = event_generator.visualize_events(event_img)
        cv2.imshow("Events", image)
        roi = image[0:64, 2:254]
        cv2.imshow("ROI", roi)
        x = 1
        img1 = image[0:64,0:84]
        img2 = image[0:64,84:168]
        img3 = image[0:64,168:252]
        img1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
        img2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)
        img3 = cv2.cvtColor(img3, cv2.COLOR_BGR2GRAY)
        n = score(img1,img2,img3)
        #cv2.imshow("1", img1)
        #cv2.imshow("2", img2)
        #cv2.imshow("3", img3)
        cv2.waitKey(1)
        process(n)
