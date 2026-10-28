import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, OpaqueFunction
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def _launch_setup(context, *args, **kwargs):
    pkg_share = get_package_share_directory('navigation_simulation')
    mode = context.launch_configurations.get('mode', 'robot').lower().strip()
    use_sim_time = context.launch_configurations.get('use_sim_time', 'true').lower() in ('true', '1')

    if mode in ('view', 'robot', 'urdf'):
        rviz_file = os.path.join(pkg_share, 'config', 'view_robot.rviz')
    elif mode in ('map', 'mapping', 'slam'):
        rviz_file = os.path.join(pkg_share, 'config', 'mapping.rviz')
    elif mode in ('nav', 'navigation', 'nav2'):
        rviz_file = os.path.join(pkg_share, 'config', 'navigation.rviz')
    else:
        rviz_file = os.path.join(pkg_share, 'config', 'view_robot.rviz')

    return [
        Node(
            package='rviz2',
            executable='rviz2',
            name='rviz2',
            arguments=['-d', rviz_file],
            parameters=[{'use_sim_time': use_sim_time}],
            output='screen'
        )
    ]


def generate_launch_description():
    return LaunchDescription([
        DeclareLaunchArgument(
            'mode',
            default_value='robot',
            description='Visualization mode: robot, mapping, or navigation'
        ),
        DeclareLaunchArgument(
            'use_sim_time',
            default_value='true',
            description='Use simulation clock source (/clock topic)'
        ),
        OpaqueFunction(function=_launch_setup)
    ])
