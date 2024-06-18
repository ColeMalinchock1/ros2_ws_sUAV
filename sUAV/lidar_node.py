import rclpy
from rclpy.node import Node
from sensor_msgs.msg import PointCloud2, Image, LaserScan
from cv_bridge import CvBridge
import cv2 as cv
import numpy as np
import threading
import csv

frame = None
br = CvBridge()
obstacle_location = "None detected"

def image_callback(msg):
    global frame
    data = msg.data
    width = msg.width
    height = msg.height
    steps = msg.point_step
    frame = 1
    print(data)

    

def process_frame(frame):
    pass
    #for data in len(frame.data):


def main(args = None):
    global frame

    rclpy.init(args = args)
    node = Node("lidar_node")
    img_subscription = node.create_subscription(PointCloud2, '/scan_3D', image_callback, 5)

    thread = threading.Thread(target=rclpy.spin, args=(node, ), daemon=True)
    thread.start()

    FREQ = 20
    rate = node.create_rate(FREQ, node.get_clock())

    while rclpy.ok():


        if frame is not None:
            continue
            #process_frame(frame)
        else:
            print("Frame is none")
        rate.sleep()

    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()