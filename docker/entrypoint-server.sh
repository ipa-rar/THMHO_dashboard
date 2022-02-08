#!/bin/bash
source "/opt/ros/noetic/setup.bash" && source "$CATKIN_WS/devel/setup.bash"
export ROS_MASTER_URI=http://192.168.0.54:11311
export ROS_IP="$(hostname -I | cut -f1 -d' ')"

roslaunch heatmap_gen heatmap_generator.launch 
#roslaunch thmho_ngsi_converter_bringup ngsi_bringup.launch
#rosrun thmho_ngsi_converter_bringup heatmap_to_ngsi.py
