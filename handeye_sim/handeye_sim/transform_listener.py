"""
Author: Shengyang Zhuang
Date Created: 2024-09-07

Copyright © 2024 Shengyang Zhuang. All rights reserved.
This script is part of the "Multi-Robot System Prototyping for Cooperative Control in Robot-Assisted Spine Surgery" project and is authored solely by Shengyang Zhuang.

Project Website: https://shengyangzhuang.github.io/mres_thesis/
Shengyang Zhuang Personal Website: https://shengyangzhuang.github.io/

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at:
    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

# Note: Please retain this header in derivative works.

BibTeX:
@mastersthesis{zhuang2024multirobot,
  author    = {Zhuang, Shengyang},
  title     = {Multi-Robot System Prototyping for Cooperative Control in Robot-Assisted Spine Surgery},
  school    = {Imperial College London},
  year      = {2024},
}
"""

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import TransformStamped
from tf2_ros import TransformListener, Buffer
import tf_transformations

class TransformListenerNode(Node):
    def __init__(self):
        super().__init__('transform_listener')
        self.tf_buffer = Buffer()
        self.tf_listener = TransformListener(self.tf_buffer, self)
        self.timer = self.create_timer(1.0, self.timer_callback)

    def timer_callback(self):
        try:
            # Look up the transformation from lbr/camera_link_optical to lbr/link_ee
            transform = self.tf_buffer.lookup_transform(
                'lbr/link_ee',  # target frame
                'lbr/camera_link_optical',  # source frame
                rclpy.time.Time())  # get the latest available transform

            translation = transform.transform.translation
            rotation = transform.transform.rotation

            # Print the transformation (translation + rotation quaternion)
            self.get_logger().info('Translation: x={}, y={}, z={}'.format(translation.x, translation.y, translation.z))
            self.get_logger().info('Rotation (quaternion): x={}, y={}, z={}, w={}'.format(rotation.x, rotation.y, rotation.z, rotation.w))

        except Exception as e:
            self.get_logger().warn('Could not transform: {}'.format(str(e)))


def main(args=None):
    rclpy.init(args=args)
    node = TransformListenerNode()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass

    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
