#airsim_api
#helper functions for airsims

from main import * 

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
        return 'forward'
    elif direction == 0:
        return 'left'
    elif direction == 2:
        return 'right'
    elif direction == 3:
        return 'yaw_left'


process(n)