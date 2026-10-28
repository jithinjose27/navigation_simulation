# Navigation Simulation: Beginner's Guide to Mobile Robotics in ROS 2

Welcome to the Mobile Robot Navigation Simulation tutorial. This repository is specifically designed for students and newcomers who are in their beginning stage of learning ROS 2 (Robot Operating System 2) and want to learn how autonomous mobile robots work through simulation.

This guide assumes no prior experience with mobile robotics simulation. Every concept, terminal command, and visualization setting is explained from scratch in a simple, human way.

---

## Table of Contents

1. Essential Concepts for Beginners
2. System Requirements
3. Step 1: Installing ROS 2 and Simulation Dependencies
4. Step 2: Understanding the Workspace and Where to Run colcon build
5. Step 3: Cloning and Compiling the Project
6. Repository Directory Structure
7. Hands-on Tutorial 1: Inspecting the Robot Model in RViz
8. Hands-on Tutorial 2: Launching the Physics Simulation in Gazebo
9. Hands-on Tutorial 3: Driving the Robot with Keyboard Teleop
10. Hands-on Tutorial 4: Creating a Map with SLAM Toolbox
11. Hands-on Tutorial 5: Autonomous Navigation with Nav2
12. Beginner Guide to RViz: Displays, Options, and What to Click
13. Common Beginner Mistakes and How to Fix Them

---

## 1. Essential Concepts for Beginners

Before typing commands, let us understand what each tool does and how they connect with one another:

- **ROS 2 (Robot Operating System 2)**: A software framework that lets different programs (called "nodes") communicate with each other using messages sent over "topics".
- **Node**: A single program performing a specific task. For example, one node reads sensor data, another node plans a path, and a third node controls motor speeds.
- **Topic**: A named channel through which nodes exchange messages. For example, LiDAR publishes distance data on `/scan`, and motor controllers listen for velocity commands on `/cmd_vel`.
- **URDF and Xacro**: Unified Robot Description Format. It is an XML file defining the physical layout of your robot: its chassis box, wheels, joints, mass, and where sensors are mounted. Xacro is a macro extension of URDF that makes writing robot models cleaner.
- **Gazebo Sim (Harmonic)**: The 3D physics simulator. It simulates gravity, friction, motor torque, wheel traction on the ground, and ray-tracing LiDAR laser beams hitting obstacle walls.
- **ros_gz_bridge**: A bridge program that translates messages between Gazebo's internal communication system and standard ROS 2 topics.
- **RViz2 (ROS Visualization)**: A 3D graphical visualization tool. Gazebo shows what the robot looks like in the virtual world; RViz shows what the robot "thinks" (its sensor rays, estimated position, occupancy grid map, and planned navigation path).
- **TF2 (Transform Library)**: Tracks the spatial relationship (position and rotation) between different parts of the robot (such as the base, the wheels, the LiDAR sensor) and the global world.
- **SLAM (Simultaneous Localization and Mapping)**: A software algorithm (using SLAM Toolbox) that allows a robot to enter an unknown environment, map the surroundings using LiDAR, and calculate its own location inside that map simultaneously.
- **Nav2 (Navigation 2)**: The autonomous navigation stack. Given a target goal on a map, Nav2 calculates the shortest path, steers the wheels, avoids obstacles, and handles recoveries if the robot gets stuck.

---

## 2. System Requirements

This project is built and tested for standard Ubuntu Linux systems:

- Recommended: Ubuntu 24.04 LTS (Noble Numbat) with ROS 2 Jazzy Jalisco.
- Also Supported: Ubuntu 22.04 LTS (Jammy Jellyfish) with ROS 2 Humble Hawksbill.
- RAM: Minimum 4 GB (8 GB or more recommended for smooth 3D rendering).
- Graphics: Standard Intel/AMD integrated graphics or dedicated NVIDIA GPU with OpenGL support.

---

## 3. Step 1: Installing ROS 2 and Simulation Dependencies

Open your terminal by pressing `Ctrl + Alt + T`. Copy and paste the following commands to install all required packages:

### For Ubuntu 24.04 (ROS 2 Jazzy):

```bash
sudo apt update
sudo apt install -y \
  ros-jazzy-desktop \
  ros-jazzy-ros-gz \
  ros-jazzy-ros-gz-sim \
  ros-jazzy-ros-gz-bridge \
  ros-jazzy-ros-gz-interfaces \
  ros-jazzy-navigation2 \
  ros-jazzy-nav2-bringup \
  ros-jazzy-slam-toolbox \
  ros-jazzy-robot-state-publisher \
  ros-jazzy-joint-state-publisher \
  ros-jazzy-joint-state-publisher-gui \
  ros-jazzy-xacro \
  ros-jazzy-teleop-twist-keyboard \
  python3-colcon-common-extensions
```

### For Ubuntu 22.04 (ROS 2 Humble):

```bash
sudo apt update
sudo apt install -y \
  ros-humble-desktop \
  ros-humble-ros-gz \
  ros-humble-ros-gz-sim \
  ros-humble-ros-gz-bridge \
  ros-humble-ros-gz-interfaces \
  ros-humble-navigation2 \
  ros-humble-nav2-bringup \
  ros-humble-slam-toolbox \
  ros-humble-robot-state-publisher \
  ros-humble-joint-state-publisher \
  ros-humble-joint-state-publisher-gui \
  ros-humble-xacro \
  ros-humble-teleop-twist-keyboard \
  python3-colcon-common-extensions
```

---

## 4. Step 2: Understanding the Workspace and Where to Run colcon build

This is one of the most critical concepts for beginners in ROS 2. Please read this carefully.

### What is a Workspace?

A ROS 2 workspace is simply a folder on your computer with a specific directory structure. A standard workspace has four folders:

```
workspace_folder/
├── src/          <-- YOUR CODE GOES HERE. All ROS 2 packages must be inside src.
├── build/        <-- Created automatically by colcon. Stores temporary compilation files.
├── install/      <-- Created automatically by colcon. Contains the built, runnable code.
└── log/          <-- Created automatically by colcon. Stores build and error logs.
```

### The Golden Rule: Where Do You Run colcon build?

- **CORRECT**: Run `colcon build` in the **root of your workspace directory** (`workspace_folder`).
- **WRONG**: Never run `colcon build` inside the `src/` directory.
- **WRONG**: Never run `colcon build` inside a package folder (like `src/navigation_simulation`).

Why? If you run `colcon build` inside `src/`, colcon will generate `build/`, `install/`, and `log/` inside your source tree, which will corrupt your ROS environment and cause errors when sourcing.

Always make sure your terminal's current path is the workspace root before running `colcon build`. You can check your current folder anytime by typing:

```bash
pwd
```

---

## 5. Step 3: Cloning and Compiling the Project

You have two easy ways to set up this project. Choose the option that fits your current workflow:

### Option A: Use This Repository Directly as Your Workspace (Simplest for Beginners)

Because this repository already has the `src/` directory properly structured inside it, you can treat this cloned repository directly as your ROS 2 workspace!

```bash
# 1. Clone the repository into your home directory
cd ~
git clone https://github.com/jithinjose27/navigation_simulation.git

# 2. Go into the workspace root (where src/ is located)
cd ~/navigation_simulation

# 3. Build the project from this workspace root
colcon build --symlink-install

# 4. Source your workspace so ROS 2 knows where your packages are
source install/setup.bash
```

### Option B: Clone into an Existing Workspace (`~/ros2_ws`)

If you already have a workspace named `~/ros2_ws`, clone the repository into its `src/` folder:

```bash
# 1. Navigate to your workspace src folder
cd ~/ros2_ws/src

# 2. Clone the repository here
git clone https://github.com/jithinjose27/navigation_simulation.git

# 3. Navigate back to the ROOT of your workspace (NOT in src)
cd ~/ros2_ws

# 4. Build from the workspace root
colcon build --symlink-install

# 5. Source your workspace
source install/setup.bash
```

### What Does the --symlink-install Flag Do?

By default, `colcon build` copies your launch files, python scripts, and configuration files into the `install/` directory. If you modify a launch file or RViz config, you would normally need to run `colcon build` again.

When you add `--symlink-install`, colcon creates symbolic links (shortcuts) to your files in `src/`. This means whenever you edit a launch file, a world file, or an RViz config, your changes take effect immediately without needing to recompile!

### Sourcing in Every Terminal

Whenever you open a new terminal window to run ROS 2 commands, you must tell that terminal about your workspace by running:

```bash
source /opt/ros/$ROS_DISTRO/setup.bash
source install/setup.bash
```

To make this automatic so you never have to type it again, run:

```bash
echo "source /opt/ros/jazzy/setup.bash" >> ~/.bashrc
echo "source ~/navigation_simulation/install/setup.bash" >> ~/.bashrc
```

---

## 6. Repository Directory Structure

Here is how the repository is organized:

```
navigation_simulation/                <-- Root of repository / Workspace root
├── src/                              <-- Source directory where packages live
│   └── navigation_simulation/        <-- The ROS 2 package
│       ├── CMakeLists.txt            <-- Build and installation rules
│       ├── package.xml               <-- Package metadata and dependencies
│       ├── config/                   <-- Parameter files and RViz setups
│       │   ├── mapper_params_online_async.yaml <-- SLAM Toolbox settings
│       │   ├── nav2_params.yaml      <-- Nav2 navigation stack parameters
│       │   ├── view_robot.rviz       <-- RViz config: Inspect robot model
│       │   ├── mapping.rviz          <-- RViz config: Real-time SLAM mapping
│       │   └── navigation.rviz       <-- RViz config: Autonomous navigation
│       ├── description/              <-- 3D Robot Description (URDF / Xacro)
│       │   ├── robot.urdf.xacro      <-- Main robot file (combines all components)
│       │   ├── robot_core.xacro      <-- Chassis, wheels, caster wheel, joints
│       │   ├── gazebo_control.xacro  <-- Differential drive controller plugin
│       │   ├── lidar.xacro           <-- LiDAR sensor link and simulation plugin
│       │   └── inertial_macros.xacro <-- Math formulas for inertia calculations
│       ├── launch/                   <-- Python launch files
│       │   ├── rsp.launch.py         <-- Robot State Publisher
│       │   ├── sim.launch.py         <-- Gazebo simulation, robot spawn, and bridge
│       │   ├── mapping.launch.py     <-- SLAM Toolbox mapping and RViz
│       │   ├── localization.launch.py<-- Map server, AMCL, and lifecycle manager
│       │   ├── navigation.launch.py  <-- Full Nav2 autonomous navigation stack
│       │   └── rviz.launch.py        <-- Quick RViz viewer helper
│       ├── maps/                     <-- Saved 2D occupancy grid maps
│       │   ├── obstacles_world.pgm   <-- 2D map image of the obstacle course
│       │   └── obstacles_world.yaml  <-- Map metadata (origin and resolution)
│       ├── models/                   <-- Gazebo models (lab walls, furniture)
│       ├── scripts/                  <-- Executable scripts (spawner helper)
│       ├── src/                      <-- Python node source files
│       └── worlds/                   <-- Virtual simulation environments
│           ├── obstacles.world       <-- Arena with walls, boxes, and cylinders
│           ├── empty.world           <-- Clean empty ground plane
│           └── lab.world             <-- Detailed indoor robotics lab
├── README.md                         <-- This beginner tutorial guide
├── LICENSE.md                        <-- License terms (Apache 2.0)
└── .gitignore                        <-- Ignores build/, install/, log/ from git
```

---

## 7. Hands-on Tutorial 1: Inspecting the Robot Model in RViz

Let us first check the robot model in RViz without starting any physics simulator. This verifies that our links, joints, and visual materials are configured correctly.

Open Terminal 1:

```bash
cd ~/navigation_simulation
source install/setup.bash
ros2 launch navigation_simulation rsp.launch.py use_jsp:=true
```

Open Terminal 2:

```bash
cd ~/navigation_simulation
source install/setup.bash
ros2 launch navigation_simulation rviz.launch.py mode:=robot
```

What you will see:
1. RViz opens with a dark gray background and a 10x10 meter reference grid.
2. The differential drive robot is displayed in the center:
   - An orange main chassis box.
   - Two blue drive wheels on the sides.
   - A black caster support wheel in the front.
   - A red LiDAR cylinder mounted on top of the chassis.
3. Coordinate axes (Red=X forward, Green=Y left, Blue=Z up) appear at each joint, showing how the robot links connect together.

When you are done inspecting, press `Ctrl + C` in both terminals to stop them.

---

## 8. Hands-on Tutorial 2: Launching the Physics Simulation in Gazebo

Now let us start the full physics simulation inside Gazebo Sim.

Open a terminal and run:

```bash
cd ~/navigation_simulation
source install/setup.bash
ros2 launch navigation_simulation sim.launch.py
```

What happens automatically:
1. Gazebo Sim Harmonic opens with the enclosed obstacle arena.
2. The robot model is automatically converted to SDF and spawned at `x=0, y=0, z=0.1`.
3. The robot drops gently onto the ground plane and rests on its two drive wheels and front caster wheel.
4. The ROS-Gazebo bridge starts forwarding simulated time (`/clock`), laser scans (`/scan`), odometry (`/odom`), and joint states (`/joint_states`) to standard ROS 2 topics.

To verify the sensor topics are working, open a new terminal and run:

```bash
source /opt/ros/$ROS_DISTRO/setup.bash
ros2 topic list
```

You should see:
```
/clock
/cmd_vel
/joint_states
/odom
/parameter_events
/robot_description
/rosout
/scan
/tf
/tf_static
```

To see actual distance measurements coming from the virtual LiDAR sensor, run:

```bash
ros2 topic echo /scan --once
```

You will see distance numbers in meters corresponding to the obstacles around the robot.

---

## 9. Hands-on Tutorial 3: Driving the Robot with Keyboard Teleop

Leave the Gazebo simulation running from Tutorial 2. Open a new terminal and launch the keyboard teleoperation tool:

```bash
source /opt/ros/$ROS_DISTRO/setup.bash
ros2 run teleop_twist_keyboard teleop_twist_keyboard
```

Make sure this terminal window is active (clicked). Use these keys to drive the robot:

```
   u    i    o
   j    k    l
   m    ,    .
```

- `i`: Drive straight forward
- `,`: Drive straight backward
- `j`: Turn left in place (spins around its center)
- `l`: Turn right in place
- `u`: Drive forward in an arc to the left
- `o`: Drive forward in an arc to the right
- `k`: Emergency Stop (sets speed to 0)
- `q` / `z`: Increase / decrease maximum speed by 10%

As you press `i` or `j`, look at the Gazebo window: the wheels turn and the robot moves smoothly through the obstacle course!

---

## 10. Hands-on Tutorial 4: Creating a Map with SLAM Toolbox

Now comes the exciting part: mapping an unknown environment.

### Step 1: Start Simulation, SLAM, and Teleop

Open three separate terminals:

Terminal 1 (Simulation):
```bash
cd ~/navigation_simulation
source install/setup.bash
ros2 launch navigation_simulation sim.launch.py
```

Terminal 2 (SLAM Toolbox and Mapping RViz):
```bash
cd ~/navigation_simulation
source install/setup.bash
ros2 launch navigation_simulation mapping.launch.py
```

Terminal 3 (Keyboard Control):
```bash
source /opt/ros/$ROS_DISTRO/setup.bash
ros2 run teleop_twist_keyboard teleop_twist_keyboard
```

### Step 2: Drive and Map the Arena

Select Terminal 3 so your keystrokes are registered. Drive the robot slowly around the obstacle course.

Watch the RViz window:
- As the robot explores, unknown gray space turns into white free space.
- Walls and obstacle boundaries are drawn as clean black lines.
- Red dots show current LiDAR ray hits in real time.
- Drive into all corners and around the obstacle boxes until the full perimeter is clearly mapped.

### Step 3: Save Your Map

Once the map looks clean and complete in RViz, open a fourth terminal and save the map using the `map_saver` command:

```bash
cd ~/navigation_simulation
source install/setup.bash
cd ~/navigation_simulation/src/navigation_simulation/maps
ros2 run nav2_map_server map_saver_cli -f my_new_map
```

You will see:
```
[INFO] [map_saver_cli]: Saving map to 'my_new_map'
[INFO] [map_saver_cli]: Map saved successfully!
```

This creates two files in your `maps` directory:
- `my_new_map.pgm`: The image file of the map.
- `my_new_map.yaml`: The metadata file containing the resolution (0.05 meters per pixel) and map origin coordinates.

---

## 11. Hands-on Tutorial 5: Autonomous Navigation with Nav2

In this tutorial, you do not need to drive manually. You will command the robot to drive itself to any destination on the map, and it will compute the path and avoid obstacles automatically.

### Step 1: Launch Simulation and Nav2

Open Terminal 1 (Simulation):
```bash
cd ~/navigation_simulation
source install/setup.bash
ros2 launch navigation_simulation sim.launch.py
```

Open Terminal 2 (Nav2 Navigation Stack):
```bash
cd ~/navigation_simulation
source install/setup.bash
ros2 launch navigation_simulation navigation.launch.py
```

This launch file automatically loads the pre-packaged map of the arena, starts AMCL localization, initializes the costmaps, and opens RViz in navigation view.

### Step 2: Set the Initial Pose (Localize the Robot)

When Nav2 first starts, the robot does not know where it is located on the map. You must give it an initial estimate:

1. Look at the top toolbar in RViz. Click the button named **2D Pose Estimate**.
2. Move your mouse to the center of the arena where the robot was spawned (near coordinates 0, 0).
3. Click and hold the left mouse button, drag the green arrow in the direction the robot is facing (forward along the X axis), and release the mouse.
4. You will see a cloud of yellow arrows (AMCL particle cloud) appear around the robot, and the red LiDAR scan points will snap onto the black map walls.

### Step 3: Send an Autonomous Navigation Goal

1. On the top toolbar in RViz, click the button named **Nav2 Goal** (or **2D Goal Pose**).
2. Click anywhere inside the white free space of the map where you want the robot to go.
3. Drag the arrow in the direction you want the robot to face when it stops, and release the mouse.

What happens next:
- A green line appears representing the global path planned by Nav2.
- A cyan/blue line shows the local trajectory computed by the controller to avoid collisions.
- The robot accelerates smoothly, navigates around boxes and walls, reaches the destination, and rotates to face the commanded direction.

---

## 12. Beginner Guide to RViz: Displays, Options, and What to Click

RViz is your window into the robot's mind. When you open RViz, you will see a panel on the left called **Displays**. Here is what every option does:

### Fixed Frame (The Most Important Setting)
- **Where to find it**: Displays panel -> Global Options -> Fixed Frame.
- **What it does**: Defines the anchor frame for all graphics.
- **What to set it to**:
  - Use `base_footprint` when inspecting the URDF robot model alone.
  - Use `odom` when running wheel odometry without a map.
  - Use `map` whenever you are running SLAM or Nav2.
- **Rule of thumb**: If everything in RViz turns red with errors saying "Transform does not exist", check your Fixed Frame first!

### RobotModel
- **What it does**: Renders the physical 3D robot body.
- **Key setting**: Description Topic must be set to `/robot_description`.
- **Tip**: You can expand the Links list to hide or show individual parts (like the chassis, wheels, or LiDAR).

### TF (Transform Frames)
- **What it does**: Shows coordinate axes for every joint on the robot.
- **Colors**:
  - Red Axis = X (Forward)
  - Green Axis = Y (Left)
  - Blue Axis = Z (Up)
  - Easy way to remember: RGB = XYZ!
- **Key setting**: Set **Marker Scale** to `0.3` so the axes do not block your view of the robot.

### LaserScan
- **What it does**: Displays the laser beams reflecting off obstacles.
- **Key settings**:
  - Topic: `/scan`
  - Size (m): `0.03` to `0.04` (makes scan dots easy to see).
  - Color Transformer: Set to `FlatColor` and pick bright Red (`255; 0; 0`).
  - Decay Time: Leave at `0.0` so old beams disappear as soon as new ones arrive.

### Map
- **What it does**: Shows the static occupancy grid map.
- **Colors**:
  - White = Free space (safe to drive).
  - Black = Obstacle or wall (do not drive here).
  - Gray = Unknown space (unexplored).
- **Critical setting**: Under Topic, the **Durability Policy** MUST be set to `Transient Local`. Maps are published once; `Transient Local` ensures that when RViz opens, it still receives the already-published map.

### Global and Local Costmaps
- **What it does**: Adds safety buffers around obstacles.
- **Colors**:
  - Dark Purple/Black: Lethal obstacle boundary.
  - Red / Yellow / Cyan gradient: Inflation zone. The path planner avoids these areas to prevent the robot from brushing against walls.
- **Key setting**: Set **Alpha** to `0.4` so the costmap is semi-transparent and you can still see the map beneath it.

### Path (Global Plan and Local Plan)
- **What it does**: Shows the navigation routes.
  - `/plan` (Green line): The full path from current position to the goal.
  - `/local_plan` (Blue/Cyan line): The short 1 to 2 second trajectory the robot is actively executing.
- **Key setting**: Set Line Width to `0.04` meters for clean visibility.

### PoseArray (AMCL Particles)
- **What it does**: Shows the cloud of yellow arrows representing where the robot thinks it might be.
- **Topic**: `/particlecloud`.
- **How to read it**: When you first set a 2D Pose Estimate, the cloud is spread out. As you drive, the algorithm compares laser scans to the map, and the particles collapse into a single tight cluster on the robot's true position.

---

## 13. Common Beginner Mistakes and How to Fix Them

### 1. "I ran colcon build inside src/ and now everything is broken"
- Why it happens: You were inside `src/` or a package folder when you ran `colcon build`.
- How to fix:
  ```bash
  # Delete the accidental folders created in src
  cd ~/navigation_simulation
  rm -rf src/build src/install src/log
  
  # Go to the workspace root and build properly
  cd ~/navigation_simulation
  colcon build --symlink-install
  source install/setup.bash
  ```

### 2. "RViz shows: No map received"
- Check that the Map display's **Durability Policy** is set to `Transient Local` (not `Volatile`).
- Check that the topic name is `/map`.

### 3. "The robot is not moving in Gazebo when I press keys in teleop"
- Check whether Gazebo is paused: look at the bottom toolbar in Gazebo and make sure the orange Play button is active (simulation time is running).
- Make sure you clicked inside the teleop terminal so your keystrokes are received.

### 4. "AMCL particle cloud is not converging"
- Drive the robot in place: press `j` or `l` in teleop to spin in a circle. Turning in place gives the LiDAR distinct corner measurements, allowing AMCL to rapidly eliminate wrong positions.

### 5. "Nav2 says: Failed to create plan"
- The goal you clicked might be inside a black obstacle or inside the dark purple inflation zone. Click a goal in wide, open white space.

---

## License

This project is open-source under the Apache 2.0 License. See [LICENSE.md](LICENSE.md) for details.