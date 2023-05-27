#! /usr/bin/env python3
# -*- coding:utf-8 -*-


import rospy
from geometry_msgs.msg import Twist
from geometry_msgs.msg import Point
from geometry_msgs.msg import Pose
from geometry_msgs.msg import Quaternion
from nav_msgs.msg import Odometry

# it turns out that we actually should not track orientation, as the orientation tracks itself pretty precisely
# however, we need to track position in order to integrate it with data from the camera.

def odometry_callback(odometry):
    print("odometry was received")
    orientation_quaternion = odometry
    print(orientation_quaternion)

def bebop_odometry():
	rate = rospy.Rate(10)
	while not rospy.is_shutdown():
            rate.sleep()

if __name__ == '__main__':
    try:
        rospy.init_node('bebop_odometry', anonymous = True)
        rospy.Subscriber("bebop/odom", Odometry, odometry_callback)
        bebop_odometry()
    except rospy.ROSInterruptException:
        pass