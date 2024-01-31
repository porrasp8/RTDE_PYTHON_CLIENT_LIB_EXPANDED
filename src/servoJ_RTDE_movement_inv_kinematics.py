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
#START_POSE = [-0.042, 0.351, 0.61, 1.08, 1.3, -1.16]
START_POSE = [0.0232, -0.34, 0.523, -0.72, -1.83, 2.38]
POSE1 = [0, -0.34, 0.69, 0.23, 1.41, -2.54]

### Test positions
POSE2_1 = [0.57, 0.11, 0.3, -1.83, 1.84, -0.59]
POSE2_2 = [0.07, -0.57, 0.297, 0.114, 2.96, -1.0]
POSE2_3 = [0.47, -0.506, 0.124, 0.186, 2.22, -1.26]


## Modes
STOP = 0
MOVEJ = 1
SERVOJ = 2


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

def stop_mode_wait(connection, next_mode):
    """
    @params: connection (rtde.RTDE) -> communication chanel
    @descrption: Send new mode and wait until popup, blocking function
    """

    while True:
        print('Stop mode, please click CONTINUE on the Polyscope')
        state = connection.receive()
        change_mode(connection, next_mode)
        if state.output_bit_registers0_to_31 == True:
                print('Stop mode finish, Robot Program can proceed to mode: ', next_mode)
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
        print('Waiting for movej() to finish')
        state = connection.receive()
        if state.output_bit_registers0_to_31 == True:
            print('ModeJ Finished\n')
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

current_mode = STOP

if not con.send_start():
    print("--------------- Server start error -------------\n")
    sys.exit()


def main():

    # ====================mode 0(Stop)===================
    stop_mode_wait(con, MOVEJ)

    # ====================mode 1(MoveJ)===================

    moveJ_request(con, START_POSE)
    print("Start Pose reached")
    moveJ_request(con, POSE1)
    print("Start Pose1")
    moveJ_request(con, START_POSE)
    print("Start Pose reached")
    
    # ====================mode 2(ServoJ)===================
    print("-------Executing servoJ  -----------\n")
    current_mode = SERVOJ
    change_mode(con, current_mode)
    
    state = con.receive()

    #-- Current pose
    state = con.receive()
    current_joints = state.actual_q
    current_tcp_pose = state.actual_TCP_pose

    print("Joints: ", current_joints)
    print("Actual TCP pose : ", current_tcp_pose)

    # Send positions
    servoJ_request(con, POSE2_1)
    time.sleep(10)
    servoJ_request(con, POSE2_2)
    time.sleep(1)
    servoJ_request(con, POSE2_3)
    time.sleep(10)

    if state.output_bit_registers0_to_31 == True:
        print('Proceeding to mode 3 --- Exit...\n')    

    # ====================mode 3(Disconnect)===================
    watchdog.input_int_register_0 = 3
    con.send(watchdog)

    con.send_pause()
    con.disconnect()


if __name__ == "__main__":
    main()