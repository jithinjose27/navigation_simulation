import os
import shutil

from ament_index_python.packages import get_package_share_directory, PackageNotFoundError
from launch import LaunchDescription
from launch.actions import (
    DeclareLaunchArgument,
    ExecuteProcess,
    IncludeLaunchDescription,
    OpaqueFunction,
    SetEnvironmentVariable,
)
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def _launch_setup(context, *args, **kwargs):
    pkg_name = 'navigation_simulation'
    try:
        pkg_share = get_package_share_directory(pkg_name)
    except PackageNotFoundError:
        # Fallback to local directory if running uninstalled
        pkg_share = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

    world_arg = context.launch_configurations.get('world', 'obstacles.world').strip()
    use_sim_time_arg = context.launch_configurations.get('use_sim_time', 'true')
    use_sim = use_sim_time_arg.lower() in ('true', '1')
    headless_arg = context.launch_configurations.get('headless', 'false').lower() in ('true', '1')
    launch_rviz = context.launch_configurations.get('rviz', 'false').lower() in ('true', '1')

    x_pos = context.launch_configurations.get('x', '0.0')
    y_pos = context.launch_configurations.get('y', '0.0')
    z_pos = context.launch_configurations.get('z', '0.1')
    yaw_rot = context.launch_configurations.get('yaw', '0.0')

    # Resolve world path
    if os.path.isabs(world_arg):
        world_path = world_arg
    else:
        world_path = os.path.join(pkg_share, 'worlds', world_arg)

    if not os.path.exists(world_path):
        world_path = os.path.join(pkg_share, 'worlds', 'empty.world')

    # Ensure Gazebo configuration paths
    existing_gz_config = os.environ.get('GZ_CONFIG_PATH', '')
    new_gz_config = f"/usr/share/gz:{existing_gz_config}".strip(':')

    existing_resource = os.environ.get('GZ_SIM_RESOURCE_PATH', '')
    models_path = os.path.join(pkg_share, 'models')
    worlds_dir = os.path.join(pkg_share, 'worlds')
    new_resource = f"{pkg_share}:{models_path}:{worlds_dir}:{existing_resource}".strip(':')

    env_actions = [
        SetEnvironmentVariable('GZ_CONFIG_PATH', new_gz_config),
        SetEnvironmentVariable('GZ_SIM_RESOURCE_PATH', new_resource),
    ]

    # Include robot_state_publisher
    rsp_launch_path = os.path.join(pkg_share, 'launch', 'rsp.launch.py')
    rsp_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(rsp_launch_path),
        launch_arguments={'use_sim_time': use_sim_time_arg, 'use_jsp': 'false'}.items()
    )

    # Launch Gazebo Sim
    gz_args = ['-r', world_path]
    if headless_arg:
        gz_args.insert(0, '-s')

    gz_sim_process = ExecuteProcess(
        cmd=['gz', 'sim'] + gz_args,
        output='screen'
    )

    # Robot spawner
    xacro_file = os.path.join(pkg_share, 'description', 'robot.urdf.xacro')
    spawn_robot_node = Node(
        package='navigation_simulation',
        executable='spawn_robot.py',
        arguments=[
            '-file', xacro_file,
            '-name', 'navigation_bot',
            '-x', x_pos,
            '-y', y_pos,
            '-z', z_pos,
            '-Y', yaw_rot
        ],
        output='screen'
    )

    # ROS-Gazebo parameter bridge
    bridge_node = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        name='ros_gz_bridge',
        output='screen',
        parameters=[{'use_sim_time': use_sim}],
        arguments=[
            '/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock',
            '/cmd_vel@geometry_msgs/msg/Twist]gz.msgs.Twist',
            '/odom@nav_msgs/msg/Odometry[gz.msgs.Odometry',
            '/scan@sensor_msgs/msg/LaserScan[gz.msgs.LaserScan',
            '/tf@tf2_msgs/msg/TFMessage[gz.msgs.Pose_V',
            '/joint_states@sensor_msgs/msg/JointState[gz.msgs.Model',
        ]
    )

    actions = env_actions + [
        rsp_launch,
        gz_sim_process,
        spawn_robot_node,
        bridge_node,
    ]

    # Optional RViz
    if launch_rviz:
        rviz_config = os.path.join(pkg_share, 'config', 'view_robot.rviz')
        actions.append(
            Node(
                package='rviz2',
                executable='rviz2',
                name='rviz2',
                arguments=['-d', rviz_config],
                parameters=[{'use_sim_time': use_sim}],
                output='screen'
            )
        )

    return actions


def generate_launch_description():
    return LaunchDescription([
        DeclareLaunchArgument(
            'world',
            default_value='obstacles.world',
            description='World file name or path (e.g. obstacles.world, empty.world, lab.world)'
        ),
        DeclareLaunchArgument(
            'use_sim_time',
            default_value='true',
            description='Use simulation (Gazebo) clock if true'
        ),
        DeclareLaunchArgument(
            'headless',
            default_value='false',
            description='Run Gazebo Sim without GUI if true'
        ),
        DeclareLaunchArgument(
            'rviz',
            default_value='false',
            description='Launch RViz2 alongside simulation'
        ),
        DeclareLaunchArgument(
            'x',
            default_value='0.0',
            description='Initial robot X coordinate'
        ),
        DeclareLaunchArgument(
            'y',
            default_value='0.0',
            description='Initial robot Y coordinate'
        ),
        DeclareLaunchArgument(
            'z',
            default_value='0.1',
            description='Initial robot Z coordinate'
        ),
        DeclareLaunchArgument(
            'yaw',
            default_value='0.0',
            description='Initial robot Yaw heading in radians'
        ),
        OpaqueFunction(function=_launch_setup)
    ])
