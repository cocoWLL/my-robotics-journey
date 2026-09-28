import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node


def generate_launch_description():
    pkg_share = get_package_share_directory('my_first_bot')
    urdf_file = os.path.join(pkg_share, 'urdf', 'my_robot.urdf')
    rviz_launch_path = os.path.join(pkg_share, 'launch', 'display.launch.py')
    world_file_name = 'my_first_room.world'
    world_path = os.path.join(get_package_share_directory('my_first_bot'), 'worlds', world_file_name)

    with open(urdf_file, 'r') as file:
        robot_description_content = file.read()
        
    include_rviz_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(rviz_launch_path)
    )
    
    gazebo = IncludeLaunchDescription(
    PythonLaunchDescriptionSource(
        os.path.join(get_package_share_directory('gazebo_ros'), 'launch', 'gazebo.launch.py')
    ), 
    launch_arguments={'world': world_path}.items()
)
    
    teleop_node = Node(
        package='teleop_twist_keyboard',
        executable='teleop_twist_keyboard',
        name='teleop',
        prefix='xterm -e',  
        output='screen'
    )

    robot_state_publisher_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        parameters=[{'robot_description': robot_description_content}]
    )

    spawn_entity_node = Node(
        package='gazebo_ros',
        executable='spawn_entity.py',
        arguments=['-topic', 'robot_description', '-entity', 'my_bot',],
        output='screen'
    )

    return LaunchDescription([
        gazebo,
        robot_state_publisher_node,
        spawn_entity_node,
        teleop_node,
        include_rviz_launch,
    ])
