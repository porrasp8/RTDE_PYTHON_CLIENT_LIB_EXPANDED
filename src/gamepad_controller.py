import inputs
import time

print(inputs.devices.gamepads)

while True:

    events = inputs.devices.gamepads[0]._do_iter()
    if events == None:
        time.sleep(0.0001)
        #print("None")

    else:
        for event in events:
            print(event)
            print(event.ev_type, event.code, event.state)

            if(event.code == "ABS_RX"):
                print(event.state)


    #print("Step")