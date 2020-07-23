import time
import numpy as np
from math import pi, sin, cos
# import quadprog

from dqrobotics import *
from dqrobotics.utils import DQ_Geometry
from dqrobotics.robots import KukaYoubotRobot
from dqrobotics.robot_control import DQ_PseudoinverseController
from dqrobotics.robot_control import DQ_ClassicQPController
from dqrobotics.robot_control import ControlObjective
# from dqrobotics.solvers import DQ_QuadraticProgrammingSolver, DQ_QuadprogSolvers
from dqrobotics.interfaces.vrep import DQ_VrepInterface
from dqrobotics.interfaces.vrep.robots import LBR4pVrepRobot, YouBotVrepRobot


print('###############################################################')
print('In order for this example to run correctly, you have to')
print('open a scene in V-REP and drag a drop a "LBR_iiwa_14_R820" robot')
print('and remove or disable its child script')
print('before running this example.')
print('###############################################################')


## Creates a VrepInterface object
vi = DQ_VrepInterface()

## Always use a try-catch in case the connection with V-REP is lost
## otherwise your clientid will be locked for future use 
try:
    ## Connects to the localhost in port 19997 with timeout 100ms and 10 retries for each method call
    vi.connect(19997,100,10)

    ## Starts simulation in V-REP
    print("Starting V-REP simulation...")
    vi.start_simulation()
    # Initialize VREP robots
    youbot_vreprobot = YouBotVrepRobot("youBot", vi)

    ## Store joint names
    joint_names = ("youBotArmJoint0","youBotArmJoint1","youBotArmJoint2","youBotArmJoint3","youBotArmJoint4")

    ## Defining robot kinematic model
    robot = KukaYoubotRobot.kinematics()
    xd    = robot.fkm((0,0,0,pi,0,pi/2,0,0))
    
    ## Defining target joints
    vi.set_joint_positions(joint_names,((pi/2,0,pi/5,0,0)))
    theta = vi.get_joint_positions(joint_names)
    
    ## Define error as something big
    e = 1
    print("Starting control loop...")
    while np.linalg.norm(e)>0.01:
        theta = youbot_vreprobot.get_q_from_vrep()
        x     = robot.fkm(theta)
        e     = vec8(x-xd)
        J     = robot.pose_jacobian(theta)
        u     = -0.01*np.matmul(np.linalg.pinv(J),e)
        theta = theta+u
        vi.set_joint_positions(joint_names,((theta[3],theta[4],theta[5],theta[6],theta[7])))
        time.sleep(0.01)
    print("Control finished...")
        
    ## Stops simulation in V-REP
    print("Stopping V-REP simulation...")
    vi.stop_simulation()

    ## Disconnects V-REP
    vi.disconnect()

except Exception as exp:
    print(exp)
    print("There was an error connecting to V-REP, please check that it is open and that the Kuka Robot is in the scene.")
    vi.disconnect_all()