# handeye_calibration_ros2_sim

This is a simulation tool for [handeye_calibration_ros2](https://github.com/shengyangzhuang/handeye_calibration_ros2) which you can try out offline without any hardware. 

Follow these instructions to install a virtual camera in ROS2 Gazebo, place an ArUco marker, and use MoveIt or custom joint-/Cartesian-space control code to move the robot and collect samples for the hand-eye calibration process. This setup allows you to analyze hand-eye calibration errors across different robot poses and sample points, as the simulation environment provides known ground truth data. 

By replicating the same robot and marker poses in real-world experiments, you may reduce calibration errors.

To get yourself started, please prepare
  1. A ROS 2 driver for the robot of your choice.
  2. Add camera description files into your ROS 2 driver.
  3. Add an ArUco marker with proper side length corresponding to the configuration file, or modify it to match your length

## Example usage

Here we provide an example usage with KUKA LBR robot. We used the [lbr_fri_ros2_stack](https://github.com/lbr-stack/lbr_fri_ros2_stack). 

***At the time of development, we used [Humble v2.0.0](https://github.com/lbr-stack/lbr_fri_ros2_stack/releases/tag/humble-v2.0.0) of the driver. We are just aware that the commands to run the KUKA simulation have changed. Please adapt the command lines wherever necessary.***

### 1. Add the camera description files

  Download the `camera_descriptions_example` in this repo, and replace the description files under `lbr-stack/src/lbr_fri_ros2_stack/lbr_description/urdf/iiwa7`

### 2. Bring up the robot
  Please refer to the newest **lbr-stack** instruction [here](https://lbr-stack.readthedocs.io/en/latest/lbr_fri_ros2_stack/lbr_fri_ros2_stack/doc/lbr_fri_ros2_stack.html)
  ```
  cd lbr-stack
  colcon build
  source install/setup.bash
  ros2 launch lbr_bringup bringup.launch.py moveit:=true sim:=true
  ```
### 3. Verify the camera
  In Gazebo, you should be able to see the camera with image capture:

  <p align="left">
    <img src="https://github.com/user-attachments/assets/160aea8d-c1d6-4e97-8d65-008863f81158" alt="Screenshot from 2024-10-15 09-22-00" width="650"/>
  </p>

  In rviz, add the image topic and choose  `/camera/image_raw`, you should be able to see the camera image:

  <p align="left">
    <img src="https://github.com/user-attachments/assets/18c6dcc2-dd06-4b0e-a4c1-7fbe3859a826" alt="Screenshot from 2024-10-15 09-22-25" width="650"/>
  </p>

### 4. Taking samples and simulate the hand-eye calibration process
  Open a new terminal, go to your handeye calibration workspace
  ```
  cd handeye_calibration_ws
  colcon build --packages-select handeye_sim
  source install/setup.bash
  ros2 launch handeye_sim taking_sample_launch.py
  ```
  You should be able to see a new camera window popping up:
  <p align="left">
    <img src="https://github.com/user-attachments/assets/683e0c62-b23e-4bf6-8c24-d6cc88135cd3" alt="Screenshot from 2024-10-15 09-24-04" width="650"/>
  </p>

  Press key `q` to record both robot and sample pose, and press key `e` to exit. You should be able to see the marker image, robot_data_simulation.yaml, marker_data_simulation.yaml being saved under `handeye_sim/resource`
  <p align="left">
    <img src="https://github.com/user-attachments/assets/84f75b4f-d020-4a05-ba59-64d2e7223f37" alt="Screenshot from 2024-10-15 09-34-49" width="650"/>
  </p>

### 5. Compute handeye calibration and compare with the ground truth
  When you take enough distinctive samples, you can compute the handeye calibration and publish the visualization in rviz.

  To compute the hand-eye calibration result:
  ```
  ros2 run handeye_sim handeye
  ```

  To publish the visualization in rviz:
  ```
  ros2 run handeye_sim eye2hand
  ```
