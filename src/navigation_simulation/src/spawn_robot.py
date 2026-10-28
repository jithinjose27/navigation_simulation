#!/usr/bin/env python3
"""
Entity spawner for Gazebo Sim (Harmonic / Fortress).
Takes robot URDF/SDF and calls Gazebo Sim's /world/<world>/create service.
"""

import argparse
import os
import subprocess
import sys
import tempfile
import time


def main():
    parser = argparse.ArgumentParser(description='Spawn a robot model into Gazebo Sim.')
    parser.add_argument('-name', default='navigation_bot', help='Name of the spawned entity')
    parser.add_argument('-world', default='', help='Name of the Gazebo world (e.g. empty, obstacles)')
    parser.add_argument('-file', default='', help='Path to URDF or SDF file')
    parser.add_argument('-topic', default='', help='Topic name containing robot_description')
    parser.add_argument('-x', type=float, default=0.0, help='Initial X position')
    parser.add_argument('-y', type=float, default=0.0, help='Initial Y position')
    parser.add_argument('-z', type=float, default=0.1, help='Initial Z position')
    parser.add_argument('-Y', type=float, default=0.0, help='Initial Yaw angle in radians')
    parser.add_argument('-timeout', type=int, default=15, help='Timeout in seconds')
    args, unknown = parser.parse_known_args()

    # Discover world name if not provided
    world_name = args.world.strip()
    gz_env = os.environ.copy()
    gz_config = gz_env.get('GZ_CONFIG_PATH', '')
    if '/usr/share/gz' not in gz_config:
        gz_env['GZ_CONFIG_PATH'] = f"/usr/share/gz:{gz_config}".strip(':')

    if not world_name:
        # Find active world from gz service -l
        start_time = time.time()
        while time.time() - start_time < args.timeout:
            try:
                res = subprocess.run(['gz', 'service', '-l'], env=gz_env, capture_output=True, text=True, check=True)
                for line in res.stdout.splitlines():
                    line = line.strip()
                    if line.startswith('/world/') and line.endswith('/create'):
                        # /world/<world_name>/create
                        parts = line.split('/')
                        world_name = parts[2]
                        break
                if world_name:
                    break
            except Exception:
                pass
            time.sleep(0.5)

    if not world_name:
        world_name = 'obstacles'
        print(f"[spawn_robot] Could not detect world service, defaulting to world '{world_name}'")
    else:
        print(f"[spawn_robot] Detected Gazebo world: '{world_name}'")

    # If file is given and is .xacro or .urdf, convert to SDF
    sdf_path = None
    if args.file:
        if args.file.endswith('.xacro'):
            tmp_urdf = tempfile.NamedTemporaryFile(suffix='.urdf', delete=False)
            subprocess.run(['xacro', args.file], stdout=tmp_urdf, check=True)
            tmp_urdf.close()
            tmp_sdf = tempfile.NamedTemporaryFile(suffix='.sdf', delete=False)
            subprocess.run(['gz', 'sdf', '-p', tmp_urdf.name], stdout=tmp_sdf, env=gz_env, check=True)
            tmp_sdf.close()
            os.remove(tmp_urdf.name)
            sdf_path = tmp_sdf.name
        elif args.file.endswith('.urdf'):
            tmp_sdf = tempfile.NamedTemporaryFile(suffix='.sdf', delete=False)
            subprocess.run(['gz', 'sdf', '-p', args.file], stdout=tmp_sdf, env=gz_env, check=True)
            tmp_sdf.close()
            sdf_path = tmp_sdf.name
        else:
            sdf_path = args.file
    elif args.topic:
        # Read from ROS topic
        try:
            import rclpy
            from rclpy.node import Node
            from std_msgs.msg import String

            rclpy.init()
            node = Node('temp_urdf_listener')
            urdf_text = None

            def sub_cb(msg):
                nonlocal urdf_text
                urdf_text = msg.data

            sub = node.create_subscription(String, args.topic, sub_cb, 1)
            start_t = time.time()
            while rclpy.ok() and urdf_text is None and (time.time() - start_t < 10):
                rclpy.spin_once(node, timeout_sec=0.2)
            node.destroy_node()
            rclpy.shutdown()

            if urdf_text:
                tmp_urdf = tempfile.NamedTemporaryFile(suffix='.urdf', delete=False, mode='w')
                tmp_urdf.write(urdf_text)
                tmp_urdf.close()
                tmp_sdf = tempfile.NamedTemporaryFile(suffix='.sdf', delete=False)
                subprocess.run(['gz', 'sdf', '-p', tmp_urdf.name], stdout=tmp_sdf, env=gz_env, check=True)
                tmp_sdf.close()
                os.remove(tmp_urdf.name)
                sdf_path = tmp_sdf.name
        except Exception as e:
            print(f"[spawn_robot] Failed to read topic {args.topic}: {e}")

    if not sdf_path or not os.path.exists(sdf_path):
        print("[spawn_robot] Error: No valid SDF model file could be generated for spawning.")
        sys.exit(1)

    service_name = f"/world/{world_name}/create"
    req_body = (
        f'sdf_filename: "{sdf_path}", '
        f'name: "{args.name}", '
        f'pose: {{position: {{x: {args.x}, y: {args.y}, z: {args.z}}}, orientation: {{z: {args.Y}}}}}'
    )

    print(f"[spawn_robot] Spawning model '{args.name}' into '{service_name}'...")
    success = False
    start_time = time.time()
    while time.time() - start_time < args.timeout:
        cmd = [
            'gz', 'service',
            '-s', service_name,
            '--reqtype', 'gz.msgs.EntityFactory',
            '--reptype', 'gz.msgs.Boolean',
            '--timeout', '3000',
            '--req', req_body
        ]
        res = subprocess.run(cmd, env=gz_env, capture_output=True, text=True)
        if 'data: true' in res.stdout:
            print(f"[spawn_robot] Successfully spawned '{args.name}'!")
            success = True
            break
        time.sleep(1.0)

    if not success:
        print(f"[spawn_robot] Warning: Spawn service timed out or returned failure.")
        sys.exit(1)


if __name__ == '__main__':
    main()
