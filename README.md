
---

# Lite3 Robot Dog + OpenMANIPULATOR Teleoperation

This repository contains the teleoperation program to control the **Lite3 Robot Dog** equipped with an **OpenMANIPULATOR arm** using keyboard input. The system runs directly on the onboard **Jetson Xavier NX** computer via an SSH connection.

## 1. Prerequisites

Ensure the following systems are available and configured on the Jetson Xavier NX:

* **OS:** Ubuntu + ROS Noetic
* **Python Environment:** Conda environment named `robotdog`
* **ROS Workspace:** `lite_cog/camera` (already built)
* **Hardware:** Lite3 Robot and OpenMANIPULATOR are powered on and ready for use.

## 2. Accessing Jetson Xavier NX

Connect to the Jetson Xavier NX from the operator's computer using SSH:

```bash
ssh <user>@<ip_jetson>

```

---

## 3. Setting Up the Environment

Once logged into the Jetson, execute the following steps in order.

### 3.1 Activate Conda Environment

```bash
srconda
conda activate robotdog

```

### 3.2 Source ROS Workspace

```bash
cd ~/lite_cog/camera/
source devel/setup.bash

```

*This step ensures all ROS packages, topics, and services are recognized by the system.*

---

## 4. Running the Teleoperation Program

Navigate to the directory containing the teleoperation file:

```bash
cd ~/Document/Test
python3 teleop_w_arm.py

```

**Once the program starts:**

1. The system will wait for data from the `/joint_states` topic.
2. The manipulator will move to its **initial pose**.
3. Teleoperation is ready for input.

---

## 5. Keyboard Controls

### 5.1 Lite3 Robot Mode Control

| Key | Function |
| --- | --- |
| `1` / `2` | Set robot to Stand / Sit mode |
| `n` | Activate Navigation mode |
| `m` | Activate Manual Movement mode |
| `p` | Activate Pose mode |
| `0` | Stop all robot movements (Emergency) |

### 5.2 Robot Dog (Base) Movement

* **w**: Move Forward
* **x**: Move Backward
* **a**: Strafe Left
* **d**: Strafe Right
* **q**: Rotate Left
* **e**: Rotate Right

### 5.3 Manipulator Arm Control

Each key moves a specific joint incrementally:

* **Joint 1 (Base Rotation):** `y` (Left) / `h` (Right)
* **Joint 2 (Forward/Back):** `u` (Forward) / `j` (Backward)
* **Joint 3 (Up/Down):** `i` (Down) / `k` (Up)
* **Joint 4 (Wrist Pitch):** `o` (Down) / `l` (Up)

### 5.4 Gripper Control

* `[` : Open Gripper
* `]` : Close Gripper

---

## 6. Stopping the Program

To stop the teleoperation, press:
`Ctrl + C`

The robot will stop moving, and the terminal will return to the normal prompt.

---

## 7. Important Notes

> [!CAUTION]
> * **Active Window:** Ensure the terminal window is active/focused when using keyboard commands.
> * **Input Frequency:** Avoid pressing keys rapidly or repeatedly (spamming) to prevent command lag.
> * **Safety:** Ensure the robot's surrounding area is clear of obstacles before starting teleoperation.
> 
> 

## 8. System Architecture Summary

1. **Operator:** Provides input via keyboard commands.
2. **Jetson Xavier NX:** Runs ROS Noetic and the teleoperation node.
3. **Lite3 Robot Dog:** Controlled via ROS Topics.
4. **OpenMANIPULATOR Arm:** Controlled via ROS Services for joints and the gripper.

---
