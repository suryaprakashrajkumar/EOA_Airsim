
#airsim_api
#helper functions for airsims
from matplotlib.pyplot import flag
import airsim
import numpy as np
import time
import cv2
wp = [0,0]
step = 0.5
velocity = 5
height = 5
client = airsim.MultirotorClient()
client.confirmConnection()
client.enableApiControl(True)
flag = 0
print (" ######################## UAV in start position ########################")

print (" ################################# ARM #################################")
client.armDisarm(True) # False to disarm

print (" ############################### TAKEOFF ###############################")
client.takeoffAsync(timeout_sec=10)
client.moveToZAsync( -2, 1).join()
prev_wp = [0,0]

print (" ###################### Avoidance Algorithm Start ######################")
def process(score):
    '''
    find the lowest in the list and return the index and if elemnts are same and minimum return the first index
    '''
    min_value = min(score)
    min_index = score.index(min_value)
    if min_value < 100:
        min_index = 1
    if min_value > 200:
        min_index = 3
    print(min_value)
    direction(min_index)

def direction(direction):
    '''
    convert the direction to the corresponding action
    '''
    if direction == 1:
        wp[1] = wp[1]
        wp[0] = wp[0] + step
    elif direction == 0:
        wp[1] = wp[1] - step
        wp[0] = wp[0]
    elif direction == 2:
        wp[1] = wp[1] + step
        wp[0] = wp[0] 
    elif direction == 3:
        wp[1] = wp[1]
        wp[0] = wp[0]
    
    if flag==0:
        client.simSetVehiclePose(airsim.Pose(airsim.Vector3r(wp[0], wp[1], -2), airsim.to_quaternion(0, 0, 0)), True)
        prev_wp = wp
        flag = 1
    else:
        if wp[0] != prev_wp[0] and wp[1] != prev_wp[1]:
            client.simSetVehiclePose(airsim.Pose(airsim.Vector3r(wp[0], wp[1], -2), airsim.to_quaternion(0, 0, 0)), True)
            prev_wp = wp
        else:
            print("holding")
    print(wp)

def score(x1,x2,x3):
  #find the more black score or less black score. 
  count = [0,0,0]
  count[0] = cv2.countNonZero(x1)
  count[1] = cv2.countNonZero(x2)
  count[2]= cv2.countNonZero(x3)
  min_value = min(count)
  min_index = count.index(min_value)
  print(min_index)
  #print(min_value)
  return count