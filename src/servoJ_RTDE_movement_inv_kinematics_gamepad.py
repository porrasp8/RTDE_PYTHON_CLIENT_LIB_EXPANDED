import sys
sys.path.append('')
import logging
import rtde.rtde as rtde
import rtde.rtde_config as rtde_config
import time
import random
import inputs
from sin_planner import PathPlanSine
from scipy.interpolate import interp1d



# -------- Consts -------- #

## Communication
ROBOT_HOST = '192.168.1.102'
ROBOT_PORT = 30004 # RTDE port
CONFIG_FILENAME = 'config/servoJ_movemnet_conf.xml'
SEND_FREQUENCY = 500
POINT_STEP = 0.01

## Positions
#START_POSE = [-0.042, 0.351, 0.61, 1.08, 1.3, -1.16]
#START_POSE = [0.0232, -0.34, 0.523, -0.72, -1.83, 2.38]
#POSE1 = [0, -0.34, 0.69, 0.23, 1.41, -2.54]
START_POSE = [-0.021, -0.34, 0.501, -0.053, 2.14, -2.13]

### Test positions
POSE2_1 = [0.57, 0.11, 0.3, -1.83, 1.84, -0.59]
POSE2_2 = [0.07, -0.57, 0.297, 0.114, 2.96, -1.0]
POSE2_3 = [0.47, -0.506, 0.124, 0.186, 2.22, -1.26]

### Sin position
SIN_START_POSE = [-0.021, -0.34, 0.501, -0.053, 2.14, -2.13]
SIN_FINAL_POSE = [-0.135, -0.45, 0.576, -0.053, 2.14, -2.13]
SIN_ORIENTATION_CONST = SIN_START_POSE[3:]
SIN_TRAJECTORY_TIME = 8
DT = 1/500  # 500 Hz 


## Modes
STOP = 0
MOVEJ = 1
SERVOJ = 2
EXIT = 3


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


def connect_robot(robot_host = ROBOT_HOST, robot_port = ROBOT_PORT):
    """
    @params: robot_host (string) -> The robot external control ip dir
             robot_port (int) -> The communication port(see rtde manual)
    @descrption: Establish communication with the robot, blocking function!
    """

    connection = rtde.RTDE(robot_host, robot_port)
    connection.connect()
    connection_state = connection.is_connected()

    # Check if connection has been established
    while connection_state != True:
        time.sleep(0.5)
        connection.connect()
        connection_state = connection.is_connected()
    
    print("---------------Successfully connected to the robot-------------\n")
    return connection

def change_mode(connection, mode):

    watchdog.input_int_register_0 = mode
    connection.send(watchdog)

def stop_mode_wait(connection):
    """
    @params: connection (rtde.RTDE) -> communication chanel
    @descrption: Send new mode and wait until popup, blocking function
    """

    while True:
        print('Stop mode, please click CONTINUE on the Polyscope')
        state = connection.receive()
        if state.output_bit_registers0_to_31 == True:
                print('Stop mode finish, Robot Program can proceed to mode')
                break


def moveJ_request(connection, pose):
    """
    @params: connection (rtde.RTDE) -> communication chanel
             pose (float[]) -> pose to move/joints
    @descrption: Send new pose with moveJ and wait, blocking function
    """

    print("-------Executing moveJ -----------\n")
    list_to_setp(setp, pose)  # changing pose to setp
    connection.send(setp) # sending initial pose

    while True:
        #print('Waiting for movej() to finish')
        state = connection.receive()
        if state.output_bit_registers0_to_31 == False:
            #print('ModeJ Finished\n')
            break

def servoJ_request(connection, pose):
    """
    @params: connection (rtde.RTDE) -> communication chanel
             pose (float[]) -> pose to move/joints
    @descrption: Send new pose with servoJ
    """

    print("-------Executing ServoJ -----------\n")
    list_to_setp(setp, pose)
    connection.send(setp)


# -------- Communication vars init -------- #
conf = rtde_config.ConfigFile(CONFIG_FILENAME)
state_names, state_types = conf.get_recipe('state')  # Define recipe for access to robot output ex. joints,tcp etc.
setp_names, setp_types = conf.get_recipe('setp')  # Define recipe for access to robot input
watchdog_names, watchdog_types= conf.get_recipe('watchdog')

# -------- Establish connection -------- #
con = connect_robot()


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

#-- Mapper setup
map_gamepad_input_into_pos = interp1d([-35768,35768],[-0.135,0.091])

def main():

    # ====================mode 0(Stop)===================
    stop_mode_wait(con)

    # ====================mode 1(MoveJ)===================

    change_mode(con, MOVEJ)
    moveJ_request(con, START_POSE)
    print("Start Pose reached")
    
    # ====================mode 2(ServoJ)===================
    print("-------Executing servoJ  -----------\n")
    change_mode(con, SERVOJ)
    
    state = con.receive()

    while True:
        
        #-- Current pos
        state = con.receive()
        pos = state.actual_TCP_pose

        #-- Gamepad input
        events = inputs.get_gamepad()
        for event in events:
            if(event.code == "ABS_RX"):
                print("Gamepad input: ", event.state)

                #-- Map input into TCP pos
                #print(map_gamepad_input_into_pos(event.state))
                pos_0 = map_gamepad_input_into_pos(event.state)
                pos[0] = pos_0

                #-- Send pos
                list_to_setp(setp, pos)
                con.send(setp)
                print(pos)
            
            

if __name__ == "__main__":
    main()