#python

#airsim_api
#helper functions for airsims
import airsim
import numpy as np
import time
import cv2
import math
wp = [0,0]
pos = []
step = 2
velocity = 0.5
height = 5
duration = 0.5
client = airsim.MultirotorClient()
client.confirmConnection()
client.enableApiControl(True)
pitch = 0
roll = 0
yaw = 0
speed = velocity
print (" ######################## UAV in start position ########################")

print (" ################################# ARM #################################")
client.armDisarm(True) # False to disarm

print (" ############################### TAKEOFF ###############################")
client.takeoffAsync(timeout_sec=10)
client.moveToZAsync( -2, 1).join()


print (" ###################### Avoidance Algorithm Start ######################")
def process(score):
    '''
    find the lowest in the list and return the index and if elemnts are same and minimum return the first index
    '''
    min_value = min(score)
    min_index = score.index(min_value)
    if min_value < 100:
        min_index = 1
    print("Min_value:",min_value)
    print("Direction:",min_index)
    direction(min_index)

def direction(direction):
    '''
    convert the direction to the corresponding action
    '''
    if direction == 1:
        pitch, roll, yaw  = airsim.to_eularian_angles(client.simGetVehiclePose().orientation)
        vx = math.cos(yaw) * speed
        vy = math.sin(yaw) * speed
        client.moveByVelocityZAsync(vx, vy,-2, 1, airsim.DrivetrainType.ForwardOnly, airsim.YawMode(False, 0)).join()
        print("Taking Straight")
    elif direction == 0:
        client.rotateByYawRateAsync(-30, duration).join()
        print("Taking left")
    elif direction == 2:
        client.rotateByYawRateAsync(30, duration).join()
        print("Taking right")

    #client.simSetVehiclePose(airsim.Pose(airsim.Vector3r(wp[0], wp[1], -2), airsim.to_quaternion(0, 0, 0)), True)
    #print("WP",wp)

def score(x1,x2,x3):
  #find the more black score or less black score. 
  count = [0,0,0]
  count[0] = cv2.countNonZero(x1)
  count[1] = cv2.countNonZero(x2)
  count[2]= cv2.countNonZero(x3)
  return count