#!/usr/bin/env python
# export PYTHONPATH=$PYTHONPATH:/opt/ros/noetic/lib/python3/dist-packages

import rospy
import sys, select, termios, tty

from geometry_msgs.msg import Twist
from sensor_msgs.msg import JointState
from message_transformer.msg import SimpleCMD
from open_manipulator_msgs.srv import SetJointPosition

# ===============================
# CONFIG
# ===============================
last_arm_cmd_time = 0.0
ARM_CMD_INTERVAL = 0.15  # seconds

BASE_LINEAR_X  = 0.3
BASE_LINEAR_Y  = 0.2
BASE_ANGULAR_Z = 0.5

ARM_STEP = 0.02
ARM_TIME = 0.6
GRIPPER_STEP = 0.002

ARM_JOINTS = ['joint1','joint2','joint3','joint4']

# JOINT_LIMITS = {
#     'joint1': (-2.5, 2.5),
#     'joint2': (-2.0, 2.0),
#     'joint3': (-1.57, 1.57),
#     'joint4': (-3.14, 3.14),
# }

# ===============================
# INIT POSE
# ===============================
INIT_ARM_POS = [
    -0.0015339808305725455,
    -1.5769323110580444,
    1.1412817239761353,
    0.5599030256271362
]

INIT_GRIPPER_POS = -0.0


GRIPPER_MIN = -0.01
GRIPPER_MAX =  0.019

arm_pos = [0.0]*4
gripper_pos = 0.0
joint_ready = False

# ===============================
# LITE3 COMMANDS
# ===============================
CMD_STAND_SIT  = 0x21010202
CMD_STOP       = 0x21020C0E
CMD_NAV_MODE   = 0x21010C03
CMD_MOVE_MODE  = 0x21010D06
CMD_POSE_MODE  = 0x21010D05

# ===============================
# KEYBOARD
# ===============================
def getKey():
    tty.setraw(sys.stdin.fileno())
    rlist, _, _ = select.select([sys.stdin], [], [], 0.1)
    key = sys.stdin.read(1) if rlist else ''
    termios.tcsetattr(sys.stdin, termios.TCSADRAIN, settings)
    return key

# ===============================
# LITE3 CMD
# ===============================
def publish_command(pub, code):
    cmd = SimpleCMD()
    cmd.cmd_code = code
    cmd.cmd_value = 0
    cmd.type = 0
    pub.publish(cmd)

# ===============================
# JOINT STATE (INIT ONLY)
# ===============================
def joint_cb(msg):
    global joint_ready, arm_pos, gripper_pos
    if joint_ready:
        return

    if all(j in msg.name for j in ARM_JOINTS):
        for i,j in enumerate(ARM_JOINTS):
            arm_pos[i] = msg.position[msg.name.index(j)]

        if 'gripper' in msg.name:
            gripper_pos = msg.position[msg.name.index('gripper')]

        joint_ready = True
        rospy.loginfo("Manipulator joint state synced")

# ===============================
# ARM HELPERS
# ===============================
def move_to_init_pose():
    global arm_pos, gripper_pos

    rospy.loginfo("Moving to init pose...")

    # Arm
    arm_pos = INIT_ARM_POS[:]
    req = SetJointPosition._request_class()
    req.joint_position.joint_name = ARM_JOINTS
    req.joint_position.position = arm_pos
    req.path_time = 2.0
    arm_srv(req)

    rospy.sleep(2.1)

    # Gripper
    gripper_pos = INIT_GRIPPER_POS
    req = SetJointPosition._request_class()
    req.joint_position.joint_name = ['gripper']
    req.joint_position.position = [gripper_pos]
    req.path_time = 0.5
    gripper_srv(req)

    rospy.loginfo("Init pose reached")



def clamp(v, lo, hi):
    return max(min(v, hi), lo)

def send_arm():
    try:
        req = SetJointPosition._request_class()
        req.joint_position.joint_name = ARM_JOINTS
        req.joint_position.position = arm_pos
        req.path_time = ARM_TIME
        arm_srv(req)
    except rospy.ServiceException as e:
        rospy.logerr(f"Arm service failed: {e}")


def move_joint(joint, delta):
    global last_arm_cmd_time

    if not joint_ready:
        return

    now = rospy.get_time()
    if now - last_arm_cmd_time < ARM_CMD_INTERVAL:
        return

    last_arm_cmd_time = now

    i = ARM_JOINTS.index(joint)
    arm_pos[i] += delta
    send_arm()


def move_gripper(delta):
    global gripper_pos
    gripper_pos += delta

    try:
        req = SetJointPosition._request_class()
        req.joint_position.joint_name = ['gripper']
        req.joint_position.position = [gripper_pos]
        req.path_time = 0.2
        gripper_srv(req)
    except rospy.ServiceException as e:
        rospy.logerr(f"Gripper service failed: {e}")


# ===============================
# MAIN
# ===============================
if _name_ == "_main_":
    settings = termios.tcgetattr(sys.stdin)
    rospy.init_node("lite3_plus_openmanipulator")

    rospy.Subscriber('/joint_states', JointState, joint_cb)

    pub_vel = rospy.Publisher('/cmd_vel', Twist, queue_size=1)
    pub_cmd = rospy.Publisher('/simple_cmd', SimpleCMD, queue_size=1)

    rospy.wait_for_service('/goal_joint_space_path')
    rospy.wait_for_service('/goal_tool_control')

    arm_srv = rospy.ServiceProxy('/goal_joint_space_path', SetJointPosition)
    gripper_srv = rospy.ServiceProxy('/goal_tool_control', SetJointPosition)

    rospy.loginfo("Lite3 + OpenMANIPULATOR Teleop READY")

    # wait for joint_states
    rospy.loginfo("Waiting for joint_states...")
    while not joint_ready and not rospy.is_shutdown():
        rospy.sleep(0.05)

    move_to_init_pose()

    # flush any buffered key presses
    termios.tcflush(sys.stdin, termios.TCIFLUSH)


    try:
        while not rospy.is_shutdown():
            key = getKey()
            x=y=th=0.0

            # ----- LITE3 -----
            if key == '1': publish_command(pub_cmd, CMD_STAND_SIT)
            elif key == '2': publish_command(pub_cmd, CMD_STAND_SIT)
            elif key == 'n': publish_command(pub_cmd, CMD_NAV_MODE)
            elif key == 'm': publish_command(pub_cmd, CMD_MOVE_MODE)
            elif key == 'p': publish_command(pub_cmd, CMD_POSE_MODE)
            elif key == '0': publish_command(pub_cmd, CMD_STOP)

            elif key == 'w': x = BASE_LINEAR_X
            elif key == 'x': x = -BASE_LINEAR_X
            elif key == 'a': y = BASE_LINEAR_Y
            elif key == 'd': y = -BASE_LINEAR_Y
            elif key == 'q': th = BASE_ANGULAR_Z
            elif key == 'e': th = -BASE_ANGULAR_Z

            # ----- MANIPULATOR -----
            elif key == 'y': move_joint('joint1', +ARM_STEP)#kiri
            elif key == 'h': move_joint('joint1', -ARM_STEP)#kanan

            elif key == 'u': move_joint('joint2', +ARM_STEP)#maju
            elif key == 'j': move_joint('joint2', -ARM_STEP)#mundur

            elif key == 'i': move_joint('joint3', +ARM_STEP)#turun
            elif key == 'k': move_joint('joint3', -ARM_STEP)#naik

            elif key == 'o': move_joint('joint4', +ARM_STEP)#turun
            elif key == 'l': move_joint('joint4', -ARM_STEP)#naik

            elif key == '[': move_gripper(+GRIPPER_STEP)
            elif key == ']': move_gripper(-GRIPPER_STEP)

            elif key == '\x03':
                break

            twist = Twist()
            twist.linear.x = x
            twist.linear.y = y
            twist.angular.z = th
            pub_vel.publish(twist)

    finally:
        pub_vel.publish(Twist())
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, settings)