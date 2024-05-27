import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import cv2 as cv
import numpy as np
import threading

frame = None
br = CvBridge()

def image_callback(msg):
    print("Callback reached")
    global frame
    frame = br.imgmsg_to_cv2(msg)

def process_image(frame):
    img = frame

    cv.imshow("Frame", img)
    cv.waitKey(1)

def main(args = None):
    global frame

    rclpy.init(args = args)
    node = Node("lidar_node")
    zed_img_subscription = node.create_subscription(Image, '~/cyglidar_ws/scan_image', image_callback, 5)

    

    thread = threading.Thread(target=rclpy.spin, args=(node, ), daemon=True)
    thread.start()

    FREQ = 20
    rate = node.create_rate(FREQ, node.get_clock())

    while rclpy.ok():


        if frame is not None:
            print("Frame received")
            process_image(frame)
        else:
            print("Frame is none")
        rate.sleep()

    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()