################################################################################
# Set minimum required version of cmake, project name and compile options
################################################################################
cmake_minimum_required(VERSION 2.8.3)
project(bb_data_recording)

################################################################################
# Find catkin packages and libraries for catkin and system dependencies
################################################################################
find_package(catkin REQUIRED COMPONENTS
  roscpp
  std_msgs
  sensor_msgs
  diagnostic_msgs
  message_generation
)

################################################################################
# Setup for python modules and scripts
################################################################################
catkin_python_setup()

################################################################################
# Declare ROS messages, services and actions
################################################################################
add_service_files(
   FILES
   bb_rosbag_recorder.srv
   bb_rosbag_player.srv
)

generate_messages(
    DEPENDENCIES
    std_msgs
)

################################################################################
# Declare ROS dynamic reconfigure parameters
################################################################################

################################################################################
# Declare catkin specific configuration to be passed to dependent projects
################################################################################
catkin_package(
  CATKIN_DEPENDS roscpp std_msgs sensor_msgs diagnostic_msgs message_runtime message_generation
)

################################################################################
# Build
################################################################################

################################################################################
# Install
################################################################################

install(DIRECTORY launch 
  DESTINATION ${CATKIN_PACKAGE_SHARE_DESTINATION}
)

install(DIRECTORY config
  DESTINATION ${CATKIN_PACKAGE_SHARE_DESTINATION}
)

catkin_install_python(
  PROGRAMS 
  scripts/bb_rosbag_record.py
  scripts/bb_rosbag_replay.py
  DESTINATION ${CATKIN_PACKAGE_BIN_DESTINATION}
)
