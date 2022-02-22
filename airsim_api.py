#airsim_api
#helper functions for airsims
wp = [0,0]
step = 0.1
velocity = 1
client = airsim.MultirotorClient()
client.confirmConnection()
client.enableApiControl(True)

print (" ######################## UAV in start position ########################")

print (" ################################# ARM #################################")
client.armDisarm(True) # False to disarm

print (" ############################### TAKEOFF ###############################")
client.takeoffAsync(timeout_sec=10) # Takeoff to 3m from current pose

print (" ###################### Avoidance Algorithm Start ######################")
def process(score):
    '''
    find the lowest in the list and return the index and if elemnts are same and minimum return the first index
    '''
    min_value = min(score)
    min_index = score.index(min_value)
    if min_value == score[1]:
        min_index = 1
    if min_value > 200:
        min_index = 3
    return direction(min_index)

def direction(direction):
    '''
    convert the direction to the corresponding action
    '''
    if direction == 1:
        wp[1] = wp[1]
        wp[0] = wp[0] + step
        return 'forward'
    elif direction == 0:
        wp[1] = wp[1] - step
        wp[0] = wp[0]
        return 'left'
    elif direction == 2:
        wp[1] = wp[1] + step
        wp[0] = wp[0] 
        return 'right'
    elif direction == 3:
        wp[1] = wp[1]
        wp[0] = wp[0] 
        return 'stop'
    client.moveToPositionAsync(wp[0], wp[1], height, velocity, timeout_sec=3e+38, yaw_mode=False).join()

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