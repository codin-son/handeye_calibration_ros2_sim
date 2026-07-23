import os
from glob import glob

from setuptools import setup

package_name = 'scara_sim'

setup(
    name=package_name,
    version='0.0.1',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob('launch/*.launch.py')),
        (os.path.join('share', package_name, 'urdf'), glob('urdf/*.xacro')),
        (os.path.join('share', package_name, 'config'),
            glob('config/*.yaml') + glob('config/*.srdf')),
        (os.path.join('share', package_name, 'rviz'), glob('rviz/*.rviz')),
        (os.path.join('share', package_name, 'worlds'), glob('worlds/*.world')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='a2tech',
    maintainer_email='izzuddin.ruslan00@gmail.com',
    description='Simple-geometry 4-DOF SCARA Gazebo simulation for hand-eye calibration testing',
    license='Apache-2.0',
    entry_points={
        'console_scripts': [
            'move = scara_sim.move:main',
        ],
    },
)
