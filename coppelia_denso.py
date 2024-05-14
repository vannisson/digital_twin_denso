from paho.mqtt import client as mqtt
import numpy as np

class DensoSimul():
    def __init__(self, joints_handles):
        self.joints_handles = joints_handles

        # Define DH parameters
        self.dh_params = [
            {'theta': 'theta1', 'd': 0.280, 'a': 0, 'alpha': -np.pi / 2},
            {'theta': 'theta2 - np.pi/2', 'd': 0, 'a': 0.210, 'alpha': 0},
            {'theta': 'theta3 + np.pi', 'd': 0, 'a': -0.075, 'alpha': np.pi / 2},
            {'theta': 'theta4', 'd': 0.210, 'a': 0, 'alpha': -np.pi / 2},
            {'theta': 'theta5', 'd': 0, 'a': 0, 'alpha': np.pi / 2},
            {'theta': 'theta6', 'd': 0.070, 'a': 0, 'alpha': 0}
        ]

    def setJoints(self, joint_pos):
        for i in range(6):
            sim.setJointTargetPosition(self.joints_handles[i], joint_pos[i])
    
    def getJoints(self):
        # Filling the lists of joints variables
        joints_pos = []
        for i in range(6):
            joints_pos.append(sim.getJointPosition(self.joints_handles[i]))

        return joints_pos
    
    def get_transformation_matrices(self, joint_angles):
        T = np.eye(4)
        transformations = []
        
        for i, params in enumerate(self.dh_params):
            theta = eval(params['theta'], {'theta1': joint_angles[0], 'theta2': joint_angles[1], 'theta3': joint_angles[2],
                                        'theta4': joint_angles[3], 'theta5': joint_angles[4], 'theta6': joint_angles[5],
                                        'np': np})
            d = params['d']
            a = params['a']
            alpha = params['alpha']
            T_i = np.array([
                [np.cos(theta), -np.sin(theta)*np.cos(alpha), np.sin(theta)*np.sin(alpha), a*np.cos(theta)],
                [np.sin(theta), np.cos(theta)*np.cos(alpha), -np.cos(theta)*np.sin(alpha), a*np.sin(theta)],
                [0, np.sin(alpha), np.cos(alpha), d],
                [0, 0, 0, 1]
            ])
            T = np.dot(T, T_i)
            transformations.append(T)
        
        return transformations
    
    def compute_jacobian(self, joint_angles):
        transformations = self.get_transformation_matrices(joint_angles)
        T_end_effector = transformations[-1]
        p_end_effector = T_end_effector[:3, 3]
        
        J = np.zeros((6, 6))
        
        for i in range(6):
            T_i = transformations[i]
            z_i = T_i[:3, 2]
            p_i = T_i[:3, 3]
            
            Jp = np.cross(z_i, p_end_effector - p_i)
            Jo = z_i
            
            J[:3, i] = Jp
            J[3:, i] = Jo
        
        return J


def on_connect(client, userdata, flags, reason_code, properties):
        if reason_code == 0:
            print(f"{self.client_name} connected to MQTT Broker!")
            # Subscribing to topics of interest
            self.client.subscribe(f"{self.client_name}/target_positions")
            self.client.subscribe(f"{self.client_name}/tool_move")
            self.client.subscribe(self.client_name+"/joint_states")
            
            print("Subscribed to " + self.client_name+"/target_positions")
            print("Subscribed to " + self.client_name+"/tool_move")
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
    elif msg.topic == self.client_name+"/tool_move":
        print(f"Received new tool move command: {decoded_msg}")
        # How the tool should move (vertical vector)
        move_vector = np.array(list(map(float, decoded_msg.split(',')))).reshape(-1, 1)
        print(self.curr_joints)
        # Getting jacobian for the current configuration
        J = self.denso.compute_jacobian(self.curr_joints)

        # Regularized inverse jacobian (to avoid singular values)
        J_inv = np.linalg.inv(J + 0.001**2 * np.eye(6))

        # Computing the joints velocities
        q_dot = J_inv @ move_vector

        q_new = np.array(self.curr_joints) + q_dot.flatten() * 0.05
        self.targetPos = q_new.tolist()

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
    self.curr_joints = self.denso.getJoints()
    
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
    self.denso.curr_joints = self.denso.getJoints()
    joint_str = list(map(str, self.denso.curr_joints))
    msg = ','.join(joint_str)
    self.client.publish(self.client_name+"/joint_states", msg)
    
def sysCall_actuation():
    self.client.loop(0.01) # Taking time to mqtt client rapidly fetch some messages from subscribed topics
    self.denso.setJoints(self.targetPos)
    
def sysCall_cleanup():
    # Clean disconnect of MQTT client
    self.client.disconnect()