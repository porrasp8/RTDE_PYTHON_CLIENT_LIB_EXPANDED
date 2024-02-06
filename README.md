# Move UR with python scripts

## Index
* [Introduction](#introduction)
* [External Control](#external-control)
* [Python Scripts(external computer)](#python-scripts)
    * [Set Up](#set-up)
    * [Communication](#communication)
* [URP Script(Robot)](#urp-script)
    * [MoveJ and ServoJ](#movej-and-servoj)
* [URsim](#ursim)
* [URrobots Backup](#urrobots-backup)

### Introduction

RTDE client library API for Universal Robots RTDE realtime interface.
You can see basic information for this library and her behavior in the following pages:

- [RTDE client library github repo](https://github.com/UniversalRobots/RTDE_Python_Client_Library)
- [UR RTDE guide](https://www.universal-robots.com/download/manuals-e-seriesur20ur30/script/script-manual-e-series-sw-511/)
- [URScript API Reference](https://s3-eu-west-1.amazonaws.com/ur-support-site/50689/scriptManual.pdf)
- [YouTube Tutorial](https://www.youtube.com/playlist?list=PLnJ9fSRnDN3B1wEuxQY4thTWyGoT2N0yd)

### External Control

To communicate your external computer with the robot once, the recommend and easisest method is the direct Ethernet connection. For this we only need to follow two steps:
1. Configure the Ip address and communication port(in robot): In my case I use the following parameters:

<p align="center">
<img src="" alt="external control pic" width="400" height="400"/>
</p>

2. Set up a static IP in the external computer: In my case I use the following parameters:

<p align="center">
<img src="https://github.com/porrasp8/RTDE_PYTHON_CLIENT_LIB_EXPANDED/assets/72991722/88f9169b-bd60-44fc-9a77-89422fee5cad" alt="external control pc pic" width="500" height="250"/>
</p>


### Python Scripts

#### Set up

In order to communicate with the robot we need to set some variables in our python script:
- ROBOT_HOST = '192.168.1.102' -> Ip previously configured in our robot
- ROBOT_PORT = 30004 -> Communication port, 30004 is used for RTDE communication
- CONFIG_FILENAME = 'config/servoJ_movemnet_conf.xml' -> Configuration file that indicates the variables that will be transmitted in the communication, both from the client and the robot side
- SEND_FREQUENCY = 500 -> Number of messages sended per second

#### Communication

The communication is configured following the following snippet:

``` py
# -------- Communication vars init -------- #
conf = rtde_config.ConfigFile(CONFIG_FILENAME)
state_names, state_types = conf.get_recipe('state')  # Define recipe for access to robot output ex. joints,tcp etc.
setp_names, setp_types = conf.get_recipe('setp')  # Define recipe for access to robot input
watchdog_names, watchdog_types= conf.get_recipe('watchdog')

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
```

To send data to the robot we will use:
``` py
con.send(setp)
con.send(watchdog)
```

And to send information to the external computer we will use:
``` py
state = con.receive()
```

The information sent in each case is defined in the previously mentioned configuration file "config/servoJ_movemnet_conf.xml", among the possible types of data that we can find in the guide.

servoJ_movemnet_conf.xml:
``` xml
<?xml version="1.0"?>
<rtde_config>
	<recipe key="state">
		<field name="output_bit_registers0_to_31" type="UINT32"/>
		<field name="output_int_register_0" type="INT32"/>
		<field name="output_double_register_0" type="DOUBLE"/>
		<field name="output_double_register_1" type="DOUBLE"/>
		<field name="output_double_register_2" type="DOUBLE"/>
		<field name="output_double_register_3" type="DOUBLE"/>
		<field name="output_double_register_4" type="DOUBLE"/>
		<field name="output_double_register_5" type="DOUBLE"/>
		<field name="actual_q" type="VECTOR6D"/>
		<field name="actual_TCP_pose" type="VECTOR6D"/>
		
	</recipe>

	<recipe key="setp">
		<field name="input_double_register_0" type="DOUBLE"/>
		<field name="input_double_register_1" type="DOUBLE"/>
		<field name="input_double_register_2" type="DOUBLE"/>
		<field name="input_double_register_3" type="DOUBLE"/>
		<field name="input_double_register_4" type="DOUBLE"/>
		<field name="input_double_register_5" type="DOUBLE"/>
	</recipe>

	<recipe key="watchdog">
		<field name="input_int_register_0" type="INT32"/>
	</recipe>
</rtde_config>
```

In this case, the **setp** values are used to send target positions to the robot, the **watchdog** is used to indicate operating modes (Stop, moveJ, servoJ) and the **state** values to receive information of interest to the script.




### URP Script

The program loaded on the robot follows the ".urp" extension and will have to be composed of a thread that is responsible for reading the information sent by the computer and the main thread that will be responsible for carrying out the appropriate operations for each of the situations. and send the feedback to the external computer


#### MoveJ and ServoJ

The main difference between these two is that MoveJ is blocking while ServoJ is not, and the second can also operate at 500Hz, which results in a very fast response. For more information consult the URScript Api.


### URsim

The same code also can be runned and tested into the Universal Robots simulator(URsim), to configure it we need to follow some steps. You can also learn more about it [here](https://www.universal-robots.com/download/software-cb-series/simulator-non-linux/offline-simulator-cb-series-non-linux-ursim-3158/):


It is advisable to install it in a linux virtual machine using a non-linux/offline-simulator image. This image can be downloaded in the official universal robots site. [Link to the last current version](https://www.universal-robots.com/download/software-cb-series/simulator-non-linux/offline-simulator-cb-series-non-linux-ursim-3158/).


Once we have the virtual machine configured as indicated in the tutorial we need to set up a ethernet connection between the VM and our host computer(like, Real UR - Host computer connection). In my case I modify the VM Network settings(Select the desired VM -> Settings -> Network) as can be seen in the image below: 


<p align="center">
<img src="https://github.com/porrasp8/RTDE_PYTHON_CLIENT_LIB_EXPANDED/assets/72991722/0844c097-6576-49c5-ac12-e85c196d697d" alt="external control pc pic" width="750" height="500"/>
</p>


Now we can power on the VM and use the command **ifconfig** in a terminal window to see the configured IP address and send a ping signal from our computer to check the connection between the two, such as:

``` sh
ping 10.198.15.8
```

Now we will only need to modify the IP address of the robot in our code and we can run it the same as in the real robot.



### URrobots Backup

In order to make a backup copy of any of the UR robots, there are mainly two ways:

1. Using Ur magci files: Universal robots allows as to introduce some scripts(.sh) in a USB, plug it in the robot and it automatically extract some intereseting files(like programas, logs...) but it can`t extrcat the full systmem. You can see more infromation about this script [here](https://www.universal-robots.com/download/software-e-series/support/magic-files/magic-file-backup-all-programs/).

2. Extracting the memory USB of the robot(it can be found in the controller case) and pluging in our computer to make a raw copy of the files.








