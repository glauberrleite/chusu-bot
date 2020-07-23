import time
import numpy as np
from math import pi, sin, cos
import quadprog

from dqrobotics import *
from dqrobotics.utils import DQ_Geometry
from dqrobotics.robots import KukaYoubotRobot
from dqrobotics.robot_control import DQ_PseudoinverseController
from dqrobotics.robot_control import DQ_ClassicQPController
from dqrobotics.robot_control import ControlObjective
from dqrobotics.solvers import DQ_QuadraticProgrammingSolver, DQ_QuadprogSolver
from dqrobotics.interfaces.vrep import DQ_VrepInterface
from dqrobotics.interfaces.vrep.robots import LBR4pVrepRobot, YouBotVrepRobot


def get_plane_from_vrep(vrep_interface, plane_name, normal):
    plane_object_pose = vrep_interface.get_object_pose(plane_name)
    p = translation(plane_object_pose)
    r = rotation(plane_object_pose)
    n = Ad(r, normal)
    d = dot(p, n)
    return n + E_ * d


def get_line_from_vrep(vrep_interface, line_name, direction):
    line_object_pose = vrep_interface.get_object_pose(line_name)
    p = translation(line_object_pose)
    r = rotation(line_object_pose)
    l = Ad(r, direction)
    m = cross(p, l)
    return l + E_ * m


def compute_lbr4p_reference(simulation_parameters_inner, x0, t_inner):
    dispz = simulation_parameters_inner.dispz
    wd = simulation_parameters_inner.wd
    wn = simulation_parameters_inner.wn

    phi = (pi / 2.0) * sin(wn * t_inner)
    r = cos(phi / 2.0) + k_ * sin(phi / 2.0)

    z = dispz * cos(wd * t_inner) * k_
    p = 1 + E_ * 0.5 * z

    # Return pose
    xd = r * x0 * p

    # Return time derivative
    phidot = (pi / 2.0) * cos(wn * t_inner) * wn
    rdot = 0.5 * (-sin(phi / 2.0) + k_ * cos(phi / 2.0)) * phidot
    pdot = -E_ * 0.5 * dispz * wd * sin(wd * t_inner) * k_
    xd_dot = rdot * x0 * p + r * x0 * pdot

    xd = lbr4p.get_reference_frame() * xd
    xd_dot = lbr4p.get_reference_frame() * xd_dot

    return xd, xd_dot


def compute_youbot_reference(simulation_parameters, controller, lbr4p_xd, lbr4p_ff):
    circle_radius = 0.1
    tcircle = 1 + E_ * 0.5 * circle_radius * j_

    # Youbot trajectory
    # Those are the trajectory components to track the whiteboard
    youbot_xd = lbr4p_xd * (1 + 0.5 * E_ * 0.015 * k_) * j_
    youbot_ff = lbr4p_ff * (1 + 0.5 * E_ * 0.015 * k_) * j_
    # Now we modify the trajectory in order to draw a circle, but we do it
    # only if the whiteboard pen tip is on the whiteboard surface.
    if simulation_parameters.first_iteration:
        simulation_parameters.first_iteration = False
        simulation_parameters.tc = 0
        simulation_parameters.rcircle = DQ([1])
    elif np.linalg.norm(controller.get_last_error_signal()) < 0.002:
        simulation_parameters.tc = simulation_parameters.tc + 0.1  # Increment around 0.5 deg.
        simulation_parameters.rcircle = cos(simulation_parameters.tc / 2.0) + k_ * sin(simulation_parameters.tc / 2.0)
    youbot_xd = youbot_xd * simulation_parameters.rcircle * tcircle
    youbot_ff = youbot_ff * simulation_parameters.rcircle * tcircle

    return youbot_xd, youbot_ff


def compute_constraints(youbot, plane_inner, cylinder1_inner, cylinder2_inner):
    robot_radius = 0.35
    radius_cylinder1 = 0.1
    radius_cylinder2 = 0.1

    youbot_base = youbot.get_chain_as_holonomic_base(0)
    youbot_base_pose = youbot_base.raw_fkm(youbot_q)
    youbot__base_Jx = youbot_base.raw_pose_jacobian(youbot_q, 2)

    t_inner = translation(youbot_base_pose)
    base_jt = youbot.translation_jacobian(youbot__base_Jx, youbot_base_pose)
    Jt = np.concatenate((base_jt, np.zeros((4, 5))), axis=1)

    j_dist_plane = youbot.point_to_plane_distance_jacobian(Jt, t_inner, plane_inner)
    dist_plane = DQ_Geometry.point_to_plane_distance(t_inner, plane_inner) - robot_radius

    j_dist_cylinder_1 = youbot.point_to_line_distance_jacobian(Jt, t_inner, cylinder1_inner)
    dist_cylinder1 = DQ_Geometry.point_to_line_squared_distance(t_inner, cylinder1_inner) - (
                radius_cylinder1 + robot_radius) ** 2

    j_dist_cylinder_2 = youbot.point_to_line_distance_jacobian(Jt, t_inner, cylinder2_inner)
    dist_cylinder2 = DQ_Geometry.point_to_line_squared_distance(t_inner, cylinder2_inner) - (
                radius_cylinder2 + robot_radius) ** 2

    j_constraint = np.concatenate((j_dist_plane, j_dist_cylinder_1, j_dist_cylinder_2), axis=0)
    b_constraint = np.array([dist_plane, dist_cylinder1, dist_cylinder2])

    return j_constraint, b_constraint


class SimulationParameters():
    def __init__(self, move_manipulator, first_iteration, wd, wn, total_time, dispz, tc, rcircle):
        self.move_manipulator = move_manipulator
        self.first_iteration = first_iteration
        self.wd = wd
        self.wn = wn
        self.total_time = total_time
        self.dispz = dispz
        self.tc = tc
        self.rcircle = rcircle


# Creates a VrepInterface object
vi = DQ_VrepInterface()

# Always use a try-catch in case the connection with V-REP is lost
# otherwise your clientid will be locked for future use
try:
    # Connects to the localhost in port 19997 with timeout 100ms and 10 retries for each method call
    if not vi.connect(19997, 100, 5):
        raise Exception("Unable to connect to vrep!")

    simulation_parameters = SimulationParameters(
        first_iteration=True,
        tc=0.0,
        rcircle=DQ([1]),
        move_manipulator=True,
        wd=0.5,
        wn=0.1,
        total_time=40.0,
        dispz=0.1)

    # Starts simulation in V-REP
    print("Starting V-REP simulation...")
    vi.start_simulation()
    
    #Joints Names
    joint_names = ("youBotArmJoint0","youBotArmJoint1","youBotArmJoint2","youBotArmJoint3","youBotArmJoint4","youBotGripperJoint1","youBotGripperJoint2")
    print(vi.get_joint_positions(joint_names))

    # Initialize VREP robots
    youbot_vreprobot = YouBotVrepRobot("youBot", vi)
    # Initialize KukaYoubot
    robot = KukaYoubotRobot.kinematics()
    vi.set_joint_positions(joint_names,((0,0,0,0,0,0,0)))
    # Load DQ_robotics Kinematics
    # youbot = youbot_vreprobot.kinematics()
    xd = robot.fkm((0,0,0,0,0,pi/2,0,0))
    print(xd)
    
    # Initialize controllers

    # qp_solver = DQ_QuadprogSolver()
    # youbot_controller = DQ_ClassicQPController(youbot, qp_solver)
    # youbot_controller.set_control_objective(ControlObjective.Pose)
    # youbot_controller.set_gain(10.0)
    # youbot_controller.set_damping(0.01)

    sampling_time = 0.05

    # Get initial robot information
    youbot_q = youbot_vreprobot.get_q_from_vrep()

    # Defining target joints
    theta = youbot_vreprobot.get_q_from_vrep()

    # Define error as something big
    e = 1

    print("Starting control loop...")
    first_iteration = True
    while np.linalg.norm(e)>0.01:
        theta = youbot_vreprobot.get_q_from_vrep()
        x     = robot.fkm(theta)
        e     = vec8(x-xd)
        print(theta)
        J     = robot.pose_jacobian(theta)
        print(J)
        u     = -0.01*np.matmul(np.linalg(J),e) 

        theta = theta+u
        vi.set_joint_positions(joint_names,((theta[3],theta[4],theta[5],theta[6],theta[7],0,0)))
        time.sleep(0.01)
    print("Control finished...")

    # for t in np.arange(0.0, simulation_parameters.total_time, sampling_time):

    #     vi.set_joint_positions(joint_names,((0,0,0,pi/2,0,0,0)))
    #     # Send desired values
    #     # youbot_vreprobot.send_q_to_vrep(youbot_q)

    #     time.sleep(sampling_time)
    # print("Control finished...")

    # Stops simulation in V-REP
    print("Stopping V-REP simulation...")
    vi.stop_simulation()

    # Disconnects V-REP
    vi.disconnect()

except Exception as exp:
    print(exp)
    print(
        "There was an error connecting to V-REP, please check that it is open and that the Kuka Robot is in the scene.")
    vi.stop_simulation()
    vi.disconnect_all()
