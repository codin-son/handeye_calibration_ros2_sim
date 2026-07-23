"""Send the SCARA to a joint configuration.

Usage:
    ros2 run scara_sim move <j1> <j2> <j3> <j4> [duration]

    j1, j2  shoulder / elbow  [rad]   (-2.62 .. 2.62)
    j3      quill Z            [m]    (-0.12 .. 0.0, negative = down)
    j4      wrist roll         [rad]  (-3.14 .. 3.14)
    duration  motion time      [s]    (default 3.0)

Example sampling poses (marker at x=0.35, y=0):
    ros2 run scara_sim move  0.0  -0.6  -0.02  0.0
    ros2 run scara_sim move  0.3  -1.0  -0.05  0.5
    ros2 run scara_sim move -0.3  -0.4  -0.08 -0.7
    ros2 run scara_sim move  0.15 -0.8  -0.10  1.2
"""
import sys

import rclpy
from rclpy.node import Node
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint
from builtin_interfaces.msg import Duration

JOINTS = ['joint1', 'joint2', 'joint3', 'joint4']
LIMITS = [(-2.62, 2.62), (-2.62, 2.62), (-0.12, 0.0), (-3.14, 3.14)]


class ScaraMover(Node):
    def __init__(self, positions, duration):
        super().__init__('scara_mover')
        self.pub = self.create_publisher(
            JointTrajectory, '/joint_trajectory_controller/joint_trajectory', 10)
        self.positions = positions
        self.duration = duration
        self.sent = False
        self.timer = self.create_timer(0.2, self.try_send)

    def try_send(self):
        if self.pub.get_subscription_count() == 0:
            self.get_logger().info('Waiting for joint_trajectory_controller...')
            return
        msg = JointTrajectory()
        msg.joint_names = JOINTS
        point = JointTrajectoryPoint()
        point.positions = self.positions
        point.time_from_start = Duration(
            sec=int(self.duration), nanosec=int((self.duration % 1) * 1e9))
        msg.points = [point]
        self.pub.publish(msg)
        self.get_logger().info(f'Sent {dict(zip(JOINTS, self.positions))}')
        self.sent = True
        self.timer.cancel()


def main(args=None):
    argv = sys.argv[1:]
    if len(argv) < 4:
        print(__doc__)
        sys.exit(1)

    positions = [float(v) for v in argv[:4]]
    duration = float(argv[4]) if len(argv) > 4 else 3.0

    for value, (lo, hi), name in zip(positions, LIMITS, JOINTS):
        if not lo <= value <= hi:
            print(f'{name}={value} outside limits [{lo}, {hi}]')
            sys.exit(1)

    rclpy.init(args=args)
    node = ScaraMover(positions, duration)
    try:
        while rclpy.ok() and not node.sent:
            rclpy.spin_once(node, timeout_sec=0.5)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
