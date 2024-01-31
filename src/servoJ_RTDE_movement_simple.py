import sys
sys.path.append('')
import logging
import rtde.rtde as rtde
import rtde.rtde_config as rtde_config
import time
import random


# -------- Consts -------- #

## Communication
ROBOT_HOST = '192.168.1.102'
ROBOT_PORT = 30004 # RTDE port
CONFIG_FILENAME = 'config/servoJ_movemnet_conf.xml'
SEND_FREQUENCY = 500
POINT_STEP = 0.01

## Positions
START_POSE = [1.57, -1.57, 0, 0, 0, 0] #-- Base and shoulder(def) 90 degrees and rest 0
FINAL_POSE = [1.57, -1.0, 0, 0, 0, 0]


# -------- support functions -------- #
def setp_to_list(setp):
    temp = []
    for i in range(0, 6):
        temp.append(setp.__dict__["input_double_register_%i" % i])
    return temp


def list_to_setp(setp, list):
    for i in range(0, 6):
        setp.__dict__["input_double_register_%i" % i] = list[i]
    return setp


# -------- Communication vars init -------- #
conf = rtde_config.ConfigFile(CONFIG_FILENAME)
state_names, state_types = conf.get_recipe('state')  # Define recipe for access to robot output ex. joints,tcp etc.
setp_names, setp_types = conf.get_recipe('setp')  # Define recipe for access to robot input
watchdog_names, watchdog_types= conf.get_recipe('watchdog')

def main():

    # -------- Establish connection -------- #
    con = rtde.RTDE(ROBOT_HOST, ROBOT_PORT)
    con.connect()
    connection_state = con.is_connected()

    # check if connection has been established
    while connection_state != True:
        time.sleep(0.5)
        con.connect()
        connection_state = con.is_connected()
    print("---------------Successfully connected to the robot-------------\n")
    
    
    # -------- Communication setup -------- #
    con.send_output_setup(state_names, state_types, SEND_FREQUENCY)
    setp = con.send_input_setup(setp_names, setp_types)
    watchdog = con.send_input_setup(watchdog_names, watchdog_types)

    setp.input_double_register_0 = 0
    setp.input_double_register_1 = 0
    setp.input_double_register_2 = 0
    setp.input_double_register_3 = 0
    setp.input_double_register_4 = 0
    setp.input_double_register_5 = 0

    setp.input_bit_registers0_to_31 = 0
    
    watchdog.input_int_register_0 = 0

    if not con.send_start():
        print("--------------- Server start error -------------\n")
        sys.exit()

    # ====================mode 1(moveJ)===================
    while True:
        print('Boolean 1 is False, please click CONTINUE on the Polyscope')
        state = con.receive()
        con.send(watchdog)
        if state.output_bit_registers0_to_31 == True:
                print('Boolean 1 is True, Robot Program can proceed to mode 1\n')
                break

    print("-------Executing moveJ -----------\n")

    watchdog.input_int_register_0 = 1
    con.send(watchdog)  # sending mode == 1
    list_to_setp(setp, START_POSE)  # changing initial pose to setp
    con.send(setp) # sending initial pose

    while True:
        print('Waiting for movej() to finish')
        state = con.receive()
        con.send(watchdog)
        if state.output_bit_registers0_to_31 == False:
            print('Proceeding to mode 2\n')
            break
    
    # ====================mode 2(ServoJ)===================
    print("-------Executing servoJ  -----------\n")
    watchdog.input_int_register_0 = 2
    next_pose = START_POSE
    con.send(watchdog)  # sending mode == 2


    
    state = con.receive()
    while True:
        #-- Current pose
        state = con.receive()
        current_joints = state.actual_q

        print(current_joints)
        
        #-- Next position compute and send it
        '''
        if(current_joints[1] < -1.0):
            next_pose[1] = next_pose[1] + POINT_STEP
        else:
            next_pose[1] = next_pose[1] - POINT_STEP
        '''

        if(random.uniform(0, 1) < 0.5):
            next_pose[0] = random.uniform( next_pose[0] - 0.8, next_pose[0])
            next_pose[1] = random.uniform( next_pose[1], next_pose[1] + 0.8)
        else:
            next_pose[0] = random.uniform( next_pose[0] , next_pose[0] + 0.8)
            next_pose[1] = random.uniform( next_pose[1] - 0.8, next_pose[1])

        next_pose[0] = max(0, min(1.57, next_pose[0]))
        next_pose[1] = max(-1.57, min(-1, next_pose[1]))


        time.sleep(1)
        


        list_to_setp(setp, next_pose)
        con.send(setp)

        if state.output_bit_registers0_to_31 == True:
            print('Proceeding to mode 3 --- Exit...\n')
            break
    

    # ====================mode 3(Disconnect)===================
    watchdog.input_int_register_0 = 3
    con.send(watchdog)

    con.send_pause()
    con.disconnect()


if __name__ == "__main__":
    main()