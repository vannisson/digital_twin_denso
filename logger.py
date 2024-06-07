from paho.mqtt import client as mqtt
import numpy as np
import pandas as pd
import os

MAX_NUM = 100

targetPos = list()
flag = False
flag_start = False
cnt = 0
q_log = np.zeros((MAX_NUM, 6))

def on_connect(client, userdata, flags, reason_code, properties):
        if reason_code == 0:
            print("connected to MQTT Broker!")
            # Subscribing to topics of interest
            client.subscribe("denso01/target_positions")
            #client.subscribe("denso01/tool_move")
            client.subscribe("denso01/joint_states")
            
            client.on_message = on_message
        else:
            print("Failed to connect, return code %d\n", reason_code)

def on_disconnect(client, userdata, flags, reason_code, properties):
    if reason_code == 0:
        print("Disconnected to MQTT Broker!")
    if reason_code > 0:
        print("Failed to disconnect, return code %d\n", reason_code)

def on_message(client, userdata, msg):
    global targetPos
    global flag
    global flag_start
    global cnt
    global q_log

    decoded_msg = msg.payload.decode()
    if msg.topic == "denso01/target_positions":
        print(f"Received new target_positions command: {decoded_msg}")
        targetPos = list(map(float, decoded_msg.split(',')))
        flag_start = True
    elif msg.topic == "denso01/joint_states":
        if flag_start:
            print(f"Received new tool move command: {decoded_msg}")
            q_current = np.array(list(map(float, decoded_msg.split(','))))

            for i in range(6):
                q_log[cnt, i] = q_current[i]
            
            cnt += 1

            if cnt >= MAX_NUM:
                flag = True


client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, "logger")
client.on_connect = on_connect
client.on_disconnect = on_disconnect

client.connect("localhost", 1883)
client.loop(0.01) # For the on_connect callback function to run, it needs a mqtt client loop


while flag == False:
    client.loop(0.05)

dataframe = pd.DataFrame(data = {'targetPos0': targetPos[0], 'targetPos1': targetPos[1], 'targetPos2': targetPos[2],'targetPos3': targetPos[3], 'targetPos4': targetPos[4], 'targetPos5': targetPos[5],
                                 'q_log0': q_log[:, 0], 'q_log1': q_log[:, 1], 'q_log2': q_log[:, 2],'q_log3': q_log[:, 3], 'q_log4': q_log[:, 4], 'q_log5': q_log[:, 5]})

dataframe.to_csv('results.csv', mode='a', index=False)