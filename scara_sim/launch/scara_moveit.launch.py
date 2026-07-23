import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import Command
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue

JOINTS = ['joint1', 'joint2', 'joint3', 'joint4']


def generate_launch_description():
    pkg_share = get_package_share_directory('scara_sim')
    xacro_file = os.path.join(pkg_share, 'urdf', 'scara.urdf.xacro')

    robot_description = {'robot_description': ParameterValue(
        Command(['xacro ', xacro_file]), value_type=str)}

    with open(os.path.join(pkg_share, 'config', 'scara.srdf')) as f:
        robot_description_semantic = {'robot_description_semantic': f.read()}

    # 4-DOF arm cannot satisfy full 6D pose goals; solve position only.
    kinematics = {'robot_description_kinematics': {'arm': {
        'kinematics_solver': 'kdl_kinematics_plugin/KDLKinematicsPlugin',
        'kinematics_solver_search_resolution': 0.005,
        'kinematics_solver_timeout': 0.05,
        'position_only_ik': True,
    }}}

    joint_limits = {'robot_description_planning': {'joint_limits': {
        'joint1': {'has_velocity_limits': True, 'max_velocity': 1.5,
                   'has_acceleration_limits': True, 'max_acceleration': 3.0},
        'joint2': {'has_velocity_limits': True, 'max_velocity': 1.5,
                   'has_acceleration_limits': True, 'max_acceleration': 3.0},
        'joint3': {'has_velocity_limits': True, 'max_velocity': 0.5,
                   'has_acceleration_limits': True, 'max_acceleration': 1.0},
        'joint4': {'has_velocity_limits': True, 'max_velocity': 3.0,
                   'has_acceleration_limits': True, 'max_acceleration': 6.0},
    }}}

    ompl = {
        'planning_pipelines': ['ompl'],
        'default_planning_pipeline': 'ompl',
        'ompl': {
            'planning_plugin': 'ompl_interface/OMPLPlanner',
            'request_adapters': 'default_planner_request_adapters/AddTimeOptimalParameterization '
                                'default_planner_request_adapters/ResolveConstraintFrames '
                                'default_planner_request_adapters/FixWorkspaceBounds '
                                'default_planner_request_adapters/FixStartStateBounds '
                                'default_planner_request_adapters/FixStartStateCollision '
                                'default_planner_request_adapters/FixStartStatePathConstraints',
            'start_state_max_bounds_error': 0.1,
        },
    }

    controllers = {
        'moveit_controller_manager':
            'moveit_simple_controller_manager/MoveItSimpleControllerManager',
        'moveit_manage_controllers': True,
        'moveit_simple_controller_manager': {
            'controller_names': ['joint_trajectory_controller'],
            'joint_trajectory_controller': {
                'type': 'FollowJointTrajectory',
                'action_ns': 'follow_joint_trajectory',
                'default': True,
                'joints': JOINTS,
            },
        },
    }

    planning_scene_monitor = {
        'publish_planning_scene': True,
        'publish_geometry_updates': True,
        'publish_state_updates': True,
        'publish_transforms_updates': True,
        'publish_robot_description': True,
        'publish_robot_description_semantic': True,
    }

    use_sim_time = {'use_sim_time': True}

    bringup = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(
            pkg_share, 'launch', 'scara_bringup.launch.py')),
        launch_arguments={'rviz': 'false'}.items(),
    )

    move_group = Node(
        package='moveit_ros_move_group',
        executable='move_group',
        output='screen',
        parameters=[
            robot_description,
            robot_description_semantic,
            kinematics,
            joint_limits,
            ompl,
            controllers,
            planning_scene_monitor,
            use_sim_time,
        ],
    )

    rviz = Node(
        package='rviz2',
        executable='rviz2',
        arguments=['-d', os.path.join(pkg_share, 'rviz', 'scara_moveit.rviz')],
        output='screen',
        parameters=[
            robot_description,
            robot_description_semantic,
            kinematics,
            use_sim_time,
        ],
    )

    return LaunchDescription([bringup, move_group, rviz])
