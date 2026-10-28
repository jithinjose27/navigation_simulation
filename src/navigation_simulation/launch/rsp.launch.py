import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
import xacro


def generate_launch_description():
    use_sim_time = LaunchConfiguration('use_sim_time')
    use_jsp = LaunchConfiguration('use_jsp')

    # Locate package and xacro file
    pkg_path = get_package_share_directory('navigation_simulation')
    xacro_file = os.path.join(pkg_path, 'description', 'robot.urdf.xacro')

    # Process the URDF / Xacro file
    robot_description_config = xacro.process_file(xacro_file).toxml()

    # Robot State Publisher node
    node_robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='screen',
        parameters=[{
            'robot_description': robot_description_config,
            'use_sim_time': use_sim_time
        }]
    )

    # Optional Joint State Publisher (used when viewing in RViz without Gazebo)
    node_joint_state_publisher = Node(
        package='joint_state_publisher',
        executable='joint_state_publisher',
        name='joint_state_publisher',
        output='screen',
        parameters=[{
            'use_sim_time': use_sim_time
        }],
        condition=IfCondition(use_jsp)
    )

    return LaunchDescription([
        DeclareLaunchArgument(
            'use_sim_time',
            default_value='false',
            description='Use simulation (Gazebo) clock if true'
        ),
        DeclareLaunchArgument(
            'use_jsp',
            default_value='false',
            description='Launch joint_state_publisher (for standalone RViz inspection)'
        ),
        node_robot_state_publisher,
        node_joint_state_publisher
    ])
