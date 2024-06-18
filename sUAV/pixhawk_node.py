#!/usr/bin/env python
import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, QoSReliabilityPolicy, QoSHistoryPolicy
from std_msgs.msg import Int64
import threading
from px4_msgs.msg import VehicleStatus, OnboardComputerStatus

global test_data
test_data = 0

def callback(data):
    global test_data
    test_data = data
                
def main(args=None):
    global test_data

    rclpy.init(args=args)

    qos_profile = QoSProfile(
        reliability = QoSReliabilityPolicy.BEST_EFFORT,
        history = QoSHistoryPolicy.KEEP_LAST,
        depth = 5
    )

    node = Node("pixhawk_node")
    node.create_subscription(OnboardComputerStatus, "/fmu/in/onboard_computer_status", callback, qos_profile)

    thread = threading.Thread(target=rclpy.spin, args=(node, ), daemon=True)
    thread.start()

    rate = node.create_rate(20, node.get_clock())

    while rclpy.ok():
        print("Received data: " + str(test_data))
        rate.sleep()

    rclpy.spin(node)
    rclpy.shutdown()

if __name__ == '__main__':
    main()