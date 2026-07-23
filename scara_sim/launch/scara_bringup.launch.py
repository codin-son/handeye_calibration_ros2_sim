import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import (DeclareLaunchArgument, IncludeLaunchDescription,
                            RegisterEventHandler, TimerAction)
from launch.conditions import IfCondition
from launch.event_handlers import OnProcessExit
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import Command, LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description():
    pkg_share = get_package_share_directory('scara_sim')
    xacro_file = os.path.join(pkg_share, 'urdf', 'scara.urdf.xacro')

    robot_description = ParameterValue(
        Command(['xacro ', xacro_file]), value_type=str)

    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(
            get_package_share_directory('gazebo_ros'), 'launch', 'gazebo.launch.py')),
        launch_arguments={
            'world': os.path.join(pkg_share, 'worlds', 'scara_grass.world'),
        }.items(),
    )

    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        parameters=[{'robot_description': robot_description}],
        output='screen',
    )

    spawn_robot = Node(
        package='gazebo_ros',
        executable='spawn_entity.py',
        arguments=['-topic', 'robot_description', '-entity', 'scara'],
        output='screen',
    )

    jsb_spawner = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['joint_state_broadcaster'],
        output='screen',
    )

    jtc_spawner = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['joint_trajectory_controller'],
        output='screen',
    )

    rviz = Node(
        package='rviz2',
        executable='rviz2',
        arguments=['-d', os.path.join(pkg_share, 'rviz', 'scara.rviz')],
        output='screen',
        condition=IfCondition(LaunchConfiguration('rviz')),
    )

    actions = [
        DeclareLaunchArgument('rviz', default_value='true'),
        gazebo,
        robot_state_publisher,
        spawn_robot,
        rviz,
        RegisterEventHandler(OnProcessExit(
            target_action=spawn_robot, on_exit=[jsb_spawner])),
        RegisterEventHandler(OnProcessExit(
            target_action=jsb_spawner, on_exit=[jtc_spawner])),
    ]

    # Spawn the ArUco marker flat on the ground inside the SCARA workspace,
    # if the generated model exists (~/.gazebo/models/marker0).
    marker_sdf = os.path.expanduser('~/.gazebo/models/marker0/model.sdf')
    if os.path.isfile(marker_sdf):
        spawn_marker = Node(
            package='gazebo_ros',
            executable='spawn_entity.py',
            arguments=['-entity', 'aruco_marker', '-file', marker_sdf,
                       '-x', '0.35', '-y', '0.0', '-z', '0.001'],
            output='screen',
        )
        actions.append(TimerAction(period=6.0, actions=[spawn_marker]))

    return LaunchDescription(actions)
