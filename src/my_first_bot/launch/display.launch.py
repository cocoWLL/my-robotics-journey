import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    pkg_share = get_package_share_directory('my_first_bot')
    urdf_file = os.path.join(pkg_share, 'urdf', 'my_robot.urdf')
    rviz_config_file = os.path.join(pkg_share, 'rviz', 'display.rviz')

    with open(urdf_file, 'r') as file:
        robot_description_content = file.read()

    return LaunchDescription([
        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            parameters=[{'robot_description': robot_description_content}]
        ),
        Node(
            package='joint_state_publisher_gui',
            executable='joint_state_publisher_gui'
        ),
        Node(
            package='rviz2',
            executable='rviz2',
            arguments=['-d', rviz_config_file]
        )
    ])
