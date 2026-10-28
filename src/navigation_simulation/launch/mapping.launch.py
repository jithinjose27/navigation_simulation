import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    pkg_share = get_package_share_directory('navigation_simulation')

    use_sim_time = LaunchConfiguration('use_sim_time')
    slam_params_file = LaunchConfiguration('slam_params_file')
    launch_rviz = LaunchConfiguration('rviz')

    default_params = os.path.join(pkg_share, 'config', 'mapper_params_online_async.yaml')
    default_rviz = os.path.join(pkg_share, 'config', 'mapping.rviz')

    start_slam_node = Node(
        package='slam_toolbox',
        executable='async_slam_toolbox_node',
        name='slam_toolbox',
        output='screen',
        parameters=[
            slam_params_file,
            {'use_sim_time': use_sim_time}
        ]
    )

    start_rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        arguments=['-d', default_rviz],
        parameters=[{'use_sim_time': use_sim_time}],
        output='screen',
        condition=IfCondition(launch_rviz)
    )

    return LaunchDescription([
        DeclareLaunchArgument(
            'use_sim_time',
            default_value='true',
            description='Use simulation clock source (/clock topic)'
        ),
        DeclareLaunchArgument(
            'slam_params_file',
            default_value=default_params,
            description='Full path to SLAM Toolbox configuration yaml file'
        ),
        DeclareLaunchArgument(
            'rviz',
            default_value='true',
            description='Launch RViz2 configured for SLAM mapping visualization'
        ),
        start_slam_node,
        start_rviz_node
    ])
