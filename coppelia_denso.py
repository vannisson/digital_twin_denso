from paho.mqtt import client as mqtt

class DensoSimul():
    def __init__(self, joints_handles):
        self.joints_handles = joints_handles

    def setJoints(self, joint_pos):
        for i in range(6):
            sim.setJointTargetPosition(self.joints_handles[i], joint_pos[i])
    
    def getJoints(self):
        # Filling the lists of joints variables
        joints_pos = []
        for i in range(6):
            joints_pos.append(str(sim.getJointPosition(self.joints_handles[i])))
            
        msg = ','.join(joints_pos)
        return msg

def on_connect(client, userdata, flags, reason_code, properties):
        if reason_code == 0:
            print(f"{self.client_name} connected to MQTT Broker!")
            # Subscribing to topics of interest
            self.client.subscribe(f"{self.client_name}/target_positions")
            self.client.subscribe(self.client_name+"/joint_states")
            
            print("Subscribed to " + self.client_name+"/target_positions")
            print("Subscribed to " + self.client_name+"/joint_states")
            self.client.on_message = on_message
        else:
            print("Failed to connect, return code %d\n", reason_code)

def on_disconnect(client, userdata, flags, reason_code, properties):
    if reason_code == 0:
        print(f"{self.client_name} disconnected to MQTT Broker!")
    if reason_code > 0:
        print("Failed to disconnect, return code %d\n", reason_code)

def on_message(client, userdata, msg):
    decoded_msg = msg.payload.decode()
    if msg.topic == self.client_name+"/target_positions":
      print(f"Received new target_positions command: {decoded_msg}")
      self.targetPos = list(map(float, decoded_msg.split(',')))
          

def sysCall_init():
    sim = require('sim')

    # Setting up denso configs
    joints_handle = []
    joints_handle.append(sim.getObject('./joint1'))
    joints_handle.append(sim.getObject('./joint2'))
    joints_handle.append(sim.getObject('./joint3'))
    joints_handle.append(sim.getObject('./joint4'))
    joints_handle.append(sim.getObject('./joint5'))
    joints_handle.append(sim.getObject('./joint6'))

    robot_handle = sim.getObject('.')
    
    self.client_name = sim.getObjectAlias(robot_handle)
    self.targetPos = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
    self.denso = DensoSimul(joints_handle)
    
    # Setting mqtt client and starting connection
    self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, self.client_name)
    self.client.on_connect = on_connect
    self.client.on_disconnect = on_disconnect
    
    # Getting broker and port from global values that are shared across all simulation objects
    broker = sim.getStringSignal("mqtt_broker")
    port = sim.getInt32Signal("mqtt_port")
    
    self.client.connect(broker, port)
    self.client.loop(0.01) # For the on_connect callback function to run, it needs a mqtt client loop
    
def sysCall_sensing():
    self.client.publish(self.client_name+"/joint_states", self.denso.getJoints())
    
def sysCall_actuation():
    self.client.loop(0.01) # Taking time to mqtt client rapidly fetch some messages from subscribed topics
    self.denso.setJoints(self.targetPos)
    
def sysCall_cleanup():
    # Clean disconnect of MQTT client
    self.client.disconnect()