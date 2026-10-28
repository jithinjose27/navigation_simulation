import os
from ament_index_python.packages import get_package_share_directory, PackageNotFoundError
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, LogInfo
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    pkg_share = get_package_share_directory('navigation_simulation')

    use_sim_time = LaunchConfiguration('use_sim_time')
    map_yaml_file = LaunchConfiguration('map')
    params_file = LaunchConfiguration('params_file')
    autostart = LaunchConfiguration('autostart')
    launch_rviz = LaunchConfiguration('rviz')

    default_map = os.path.join(pkg_share, 'maps', 'obstacles_world.yaml')
    default_params = os.path.join(pkg_share, 'config', 'nav2_params.yaml')
    default_rviz = os.path.join(pkg_share, 'config', 'navigation.rviz')

    # Try to locate nav2_bringup
    try:
        nav2_bringup_dir = get_package_share_directory('nav2_bringup')
        nav2_launch_path = os.path.join(nav2_bringup_dir, 'launch', 'bringup_launch.py')
        nav2_bringup = IncludeLaunchDescription(
            PythonLaunchDescriptionSource(nav2_launch_path),
            launch_arguments={
                'map': map_yaml_file,
                'use_sim_time': use_sim_time,
                'params_file': params_file,
                'autostart': autostart,
            }.items()
        )
    except PackageNotFoundError:
        nav2_bringup = LogInfo(
            msg=(
                "\n=======================================================\n"
                "[ERROR] 'nav2_bringup' package is not installed.\n"
                "Install it using:\n"
                "    sudo apt install ros-jazzy-navigation2 ros-jazzy-nav2-bringup\n"
                "=======================================================\n"
            )
        )

    rviz_node = Node(
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
            'map',
            default_value=default_map,
            description='Full path to map YAML file to load for navigation'
        ),
        DeclareLaunchArgument(
            'params_file',
            default_value=default_params,
            description='Full path to Nav2 parameter file'
        ),
        DeclareLaunchArgument(
            'autostart',
            default_value='true',
            description='Automatically start up lifecycle nodes'
        ),
        DeclareLaunchArgument(
            'rviz',
            default_value='true',
            description='Launch RViz2 configured for navigation visualization'
        ),
        nav2_bringup,
        rviz_node
    ])
