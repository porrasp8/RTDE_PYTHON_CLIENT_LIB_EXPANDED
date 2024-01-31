# Move UR with python scripts

## Index
* [Introduction](#introduction)
* [External Control](#external-control)
* [Python Scripts(external computer)](#python-scripts)
    * [Set Up](#set-up)
    * [Communication](#communication)
    * [MoveJ](#movej)
    * [ServoJ](#servoj)
* [URP Script(Robot)](#urp-script-(robot))

### Introduction

RTDE client library API for Universal Robots RTDE realtime interface.
You can see basic information for this library and her behavior in the following pages:

- [RTDE client library github repo](https://github.com/UniversalRobots/RTDE_Python_Client_Library)
- [UR RTDE guide](https://www.universal-robots.com/download/manuals-e-seriesur20ur30/script/script-manual-e-series-sw-511/)
- [URScript API Reference](https://s3-eu-west-1.amazonaws.com/ur-support-site/50689/scriptManual.pdf)

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



```















