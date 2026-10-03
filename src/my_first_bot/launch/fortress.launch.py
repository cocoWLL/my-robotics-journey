import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node


def generate_launch_description():
    pkg_share = get_package_share_directory('my_first_bot')
    urdf_file = os.path.join(pkg_share, 'urdf', 'my_robot_fortress.urdf')
    world_file = os.path.join(pkg_share, 'worlds', 'my_first_room.world')

    with open(urdf_file, 'r') as file:
        robot_description_content = file.read()

    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(
                get_package_share_directory('ros_gz_sim'),
                'launch',
                'gz_sim.launch.py',
            )
        ),
        launch_arguments={
            'gz_args': f'-s -r {world_file}'
        }.items(),
    )
    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        parameters=[
            {
                'robot_description': robot_description_content,
                'use_sim_time': True,
            }
        ],
        output='screen',
    )

    clock_bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=[
            '/world/default/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock'
        ],
        remappings=[
            ('/world/default/clock', '/clock')
        ],
        output='screen',
    )

    cmd_vel_bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=[
            '/model/my_bot/cmd_vel@geometry_msgs/msg/Twist]gz.msgs.Twist'
        ],
        remappings=[
            ('/model/my_bot/cmd_vel', '/cmd_vel')
        ],
        output='screen',
    )

    odom_bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=[
            '/model/my_bot/odometry@nav_msgs/msg/Odometry[gz.msgs.Odometry'
        ],
        remappings=[
            ('/model/my_bot/odometry', '/odom')
        ],
        output='screen',
    )

    tf_bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=[
            '/model/my_bot/tf@tf2_msgs/msg/TFMessage[gz.msgs.Pose_V'
        ],
        remappings=[
            ('/model/my_bot/tf', '/tf')
        ],
        output='screen',
    )

    scan_bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=[
            '/scan@sensor_msgs/msg/LaserScan[gz.msgs.LaserScan'
        ],
        output='screen',
    )

    spawn_robot = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=[
            '-name',
            'my_bot',
            '-topic',
            'robot_description',
            '-z',
            '0.2',
        ],
        output='screen',
    )

    return LaunchDescription(
        [gazebo, clock_bridge, robot_state_publisher, cmd_vel_bridge, odom_bridge, tf_bridge, scan_bridge, spawn_robot]
    )
