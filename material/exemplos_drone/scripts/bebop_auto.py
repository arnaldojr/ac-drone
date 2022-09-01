#! /usr/bin/env python3
# -*- coding:utf-8 -*-


import rospy
import threading
import sys, select, tty, termios

import numpy as np

from std_msgs.msg import String
from std_msgs.msg import Empty
from std_msgs.msg import Bool

from geometry_msgs.msg import Vector3
from geometry_msgs.msg import Twist
from geometry_msgs.msg import PoseStamped
from geometry_msgs.msg import Point
from geometry_msgs.msg import Pose

from bebop_control.msg import Path

from mpl_toolkits.mplot3d import Axes3D
from pid_controller import pd_controller
from copy import deepcopy
from transform_enhanced import get_yaw_from_quaternion

import state_manager
from route_manager import RouteManager

ERROR_THRESHOLD = 0.1

bebop_pose = None
bebop_yaw = 0.0
was_input_updated = False

controller_z = pd_controller(0.4, 10.0, 1.0) # global z, for copter looking at the shelf it is -x
#controller_z = pd_controller(0.13, 0.0, 0.1) # global z, for copter looking at the shelf it is -x
controller_x = pd_controller(0.4, 12.0, 0.1) # global x, for copter looking at the shelf it is y (or -y) 
#controller_x = pd_controller(0.4, 0.0, 0.1) # global x, for copter looking at the shelf it is y (or -y) 
controller_y = pd_controller(1.0, 3.0, 0.7) # global y, for copter looking at the shelf it is z
#controller_y = pd_controller(1.0, 0.0, 1.0) # global y, for copter looking at the shelf it is z
controller_yaw = pd_controller(0.02, 0.0, 1.0) # global y, for copter looking at the shelf it is z

was_position_initial_set = False

copter_state_manager = state_manager.StateManager()
route_manager = RouteManager()

class NonBlockingConsole(object):
    def __enter__(self):
        self.old_settings = termios.tcgetattr(sys.stdin)
        tty.setcbreak(sys.stdin.fileno())
        return self

    def __exit__(self, type, value, traceback):
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, self.old_settings)

    def get_data(self):
        try:
            if select.select([sys.stdin], [], [], 0) == ([sys.stdin], [], []):
                return sys.stdin.read(1)
        except:
            return '[CTRL-C]'
        return False

def pathCallback(path_new):
    global route_manager
    global copter_state_manager
    time_current = rospy.get_time()
    route_manager.set_route(path_new)
    copter_state_manager.set_state(state_manager.COPTER_STATE_APPROVING_PATH, time_current)

def poseCallback(pose):
    global route_manager
    global bebop_pose, was_input_updated
    global bebop_yaw

    time_current = rospy.get_time()

    bebop_pose = deepcopy(pose)
    was_input_updated = True
    bebop_yaw = get_yaw_from_quaternion(bebop_pose.orientation)

    route_manager.set_current_position(bebop_pose.position, time_current)

    position_error = route_manager.get_current_error()
    current_waypoint = route_manager.get_current_waypoint()

    position_error_publisher.publish(position_error)
    if not current_waypoint is None:
        current_waypoint_publisher.publish(current_waypoint)
    else:
        current_waypoint_publisher.publish(Point(0, 0, 0))

def key_reader():
    global is_running
    global copter_state_manager
    global controller_y
    global is_keyreader_finished
    global speed_x, speed_y, speed_z, speed_yaw
    global pub_takeoff, pub_landing

    pub_image_saver = rospy.Publisher('bebop_control/enable_image_saver', Bool, queue_size=10)
    message_empty = Empty()
    with NonBlockingConsole() as nbc:
        while is_running:
            c = nbc.get_data()
            time_current = rospy.get_time()
            if c == '\x1b': # x1b is ESC
                is_keyreader_finished = True
                pub_landing.publish(message_empty)
                break
            elif c == '5':
                speed_x = 0.0
                speed_y = 0.0
                speed_z = 0.0
                speed_yaw = 0.0
                print("zero position")
            elif c == 'l':
                copter_state_manager.set_state(state_manager.COPTER_STATE_LANDING, time_current)
                speed_x = 0.0
                speed_y = 0.0
                speed_z = 0.0
                speed_yaw = 0.0
                pub_landing.publish(message_empty)
                print("land")
            elif c == 'n':
                print("navigate")
                current_state = copter_state_manager.get_state(time_current)
                if current_state == state_manager.COPTER_STATE_HOVERING:
                    copter_state_manager.set_state(state_manager.COPTER_STATE_NAVIGATING, time_current)
            elif c == 't':
                copter_state_manager.set_state(state_manager.COPTER_STATE_TAKING_OFF, time_current)
                pub_takeoff.publish(message_empty)
                print("take off")
            elif c == 's':
                pub_image_saver.publish(Bool(True))
                print("saving images")
            elif c == 'f':
                pub_image_saver.publish(Bool(False))
                print("not saving images")

def bebop_auto():
    global route_manager
    global copter_state_manager
    global is_keyreader_finished, is_landing
    global bebop_position, was_input_updated
    global speed_x, speed_y, speed_z, speed_yaw
    global pub_takeoff, pub_landing

    pub = rospy.Publisher('bebop/cmd_vel', Twist, queue_size = 10)
    pub_path_received = rospy.Publisher('bebop_control/path_received', Empty, queue_size = 10)
    rate = rospy.Rate(30)
    not_update_counter = 0
    message_empty = Empty()
    while not rospy.is_shutdown() and not is_keyreader_finished:
            time_current = rospy.get_time()
            if was_input_updated: # if the input was updated, then we can do smth. what?
                                    # for all the controllers we can set new , and new current goal
                was_input_updated = False
                not_update_counter = 0

                if route_manager.is_route_finished() and \
                    copter_state_manager.get_state(time_current) == state_manager.COPTER_STATE_NAVIGATING:
                    copter_state_manager.set_state(state_manager.COPTER_STATE_LANDING, time_current)
                    print("copter came to landing state")
                else:
                    position_error = route_manager.get_current_error()
                    speed_x = controller_z.set_current_error(position_error.z)
                    speed_y = controller_x.set_current_error(position_error.x)
                    speed_z = -controller_y.set_current_error(position_error.y)
                    speed_yaw = controller_yaw.set_current_error(bebop_yaw)

            else:
                not_update_counter = not_update_counter + 1
                if not_update_counter >= 10:
                    speed_x = 0.0
                    speed_y = 0.0
                    speed_z = 0.0
                    speed_yaw = 0.0

            current_state = copter_state_manager.get_state(time_current)
            if current_state == state_manager.COPTER_STATE_NAVIGATING:
                twist_current = Twist(Vector3(speed_x, speed_y, speed_z), Vector3(0.0, 0.0, speed_yaw))
            elif current_state == state_manager.COPTER_STATE_TAKING_OFF:
                twist_current = Twist(Vector3(0.0, 0.0, 0.0), Vector3(0.0, 0.0, 0.0))
                pub_takeoff.publish(message_empty)
            elif current_state == state_manager.COPTER_STATE_LANDING:
                twist_current = Twist(Vector3(0.0, 0.0, 0.0), Vector3(0.0, 0.0, 0.0))
                pub_landing.publish(message_empty)
            elif current_state == state_manager.COPTER_STATE_APPROVING_PATH:
                twist_current = Twist(Vector3(0.0, 0.0, 0.0), Vector3(0.0, 0.0, 0.0))
                pub_path_received.publish(message_empty)
            else:
                twist_current = Twist(Vector3(0.0, 0.0, 0.0), Vector3(0.0, 0.0, 0.0))

            pub.publish(twist_current)
            rate.sleep()

if __name__ == '__main__':
    try:
        speed_x = 0.0
        speed_y = 0.0
        speed_z = 0.0
        speed_yaw = 0.0

        rospy.init_node('bebop_auto', anonymous = True)
        position_error_publisher = rospy.Publisher('bebop_position_error', Point, queue_size = 10)
        current_waypoint_publisher = rospy.Publisher('bebop_current_waypoint', Point, queue_size = 10)
        pub_takeoff = rospy.Publisher('bebop/takeoff', Empty, queue_size=10)
        pub_landing = rospy.Publisher('bebop/land', Empty, queue_size=10)
        rospy.Subscriber("bebop_pose", Pose, poseCallback)
        rospy.Subscriber("bebop_control/path", Path, pathCallback)
        is_running = True
        is_keyreader_finished = False
        is_landing = False
        thread_reader = threading.Thread(target = key_reader)
        thread_reader.start()
        bebop_auto()
        is_running = False
    except rospy.ROSInterruptException:
        pass