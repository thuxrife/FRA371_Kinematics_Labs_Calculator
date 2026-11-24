import numpy as np
import roboticstoolbox as rtb
from roboticstoolbox.robot.ERobot import ERobot
import spatialmath as sm
import spatialgeometry as sg
from swift.Swift import Swift
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from pathlib import Path
import builtins, re, time
import swift.SwiftRoute as _route
from roboticstoolbox.robot.Robot import Robot

# Swift's file server passes "/D:/..." to open(), which is invalid on Windows
_route.open = lambda p, *a, **k: builtins.open(p[1:] if re.match(r"^/[A-Za-z]:", p) else p, *a, **k)
"""
Please do not modify this file!!! This file contains utility functions for Lab3.
"""

def DefindeRobot(urdf_file_name:str):
    """
    Define the robot from the URDF file.

    Parameters:
    - urdf_file_name: The name of the URDF file (string).

    Returns:
    - robot: The defined robot object (instance of ERobot class).
    """
    # 1. Get the current working directory using pathlib
    HERE = Path.cwd()
    # 2. Read the URDF with tld=HERE so package://my_robot/meshes/... resolves to the local meshes
    links, name, _, _ = Robot.URDF_read(f'my_robot/{urdf_file_name}', tld=HERE)
    # 3. Build the ERobot from the links
    robot = rtb.ERobot(links, name=name)
        
    return robot

def SetupSimulation(robot: ERobot, start_position: list[float])-> Swift:
    """
    Move the robot to its start position and open it in a Swift simulator.

    Parameters:
    - robot: The robot object (instance of Robot class).
    - start_position: Starting [x, y, z] position of the end-effector [m] (list).

    Returns:
    - env: The Swift environment object.
    """
    position_only_mask = [1, 1, 1, 0, 0, 0]
    sol = robot.ikine_LM(
        sm.SE3(*start_position),
        mask=position_only_mask,
        q0=[0.0, 0.0, 0.0],
        joint_limits=True,
    )
    robot.q = sol.q

    env = Swift()
    env.launch(realtime=True, browser="notebook")
    env.add(robot)
    time.sleep(1)   # Give the simulator time to load before the motion starts

    return env


def UpdateBoxPosition(box, P_current, V, dt):
    """
    Update the position of the box in the environment.

    Parameters:
    - box: The box object (instance of Cuboid class).
    - V: Velocity of the box (numpy array).
    - dt: Time step (float).
    """
    
    P_new = P_current + V * dt
    box.T = sm.SE3(P_new[0], P_new[1], P_new[2])  # Update the pose of the box
