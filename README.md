# Hand-Eye Calibration Simulation (ROS 2 + Gazebo Classic)

Simulation environment for eye-in-hand calibration — a camera mounted on a robot arm observes an ArUco marker, sample pose pairs are collected, and `cv2.calibrateHandEye` computes the camera-to-gripper transform, which can be compared against the simulation's known ground truth.

Two robots are supported:

| Robot | Package | Control | Notes |
|---|---|---|---|
| **4-DOF SCARA** (igus-style, RRPR) | `scara_sim` (this repo) | MoveIt 2 (position-only IK) or direct joint commands | Simple box/cylinder geometry, camera looks straight down, marker flat on grass ground with scattered "loose fruit" cubes |
| **KUKA LBR iiwa7** (7-DOF) | [lbr_fri_ros2_stack](https://github.com/lbr-stack/lbr_fri_ros2_stack) + camera files from this repo | MoveIt 2 | Original setup from [handeye_calibration_ros2](https://github.com/shengyangzhuang/handeye_calibration_ros2) |

Docker users: see [Dockerfile](Dockerfile) and `docker/` — the rest of this page covers the **native** setup.

---

## Requirements

- Ubuntu 22.04 with ROS 2 Humble (`ros-humble-desktop-full`)
- Gazebo **Classic** 11 (not the new "gz/Ignition" Gazebo — they conflict, see below)
- Python: OpenCV, SciPy (`python3-opencv python3-scipy`)

## Installation

### 1. System dependencies

```bash
sudo apt install python3-pip python3-vcstool python3-opencv python3-scipy \
  ros-humble-tf-transformations ros-humble-cv-bridge \
  ros-humble-gazebo-ros-pkgs ros-humble-gazebo-ros2-control \
  ros-humble-moveit
```

> **Gazebo conflict:** `ros-humble-gazebo-ros-pkgs` requires Gazebo Classic, which cannot coexist with the new Gazebo (`gz-*`/Ignition packages). If apt reports `gz-tools2 : Conflicts: gazebo`, purge the new stack first:
> ```bash
> sudo apt purge 'gz-*' 'libgz-*' 'python3-gz-*' 'ros-humble-gz-*' 'ros-humble-ros-gz-*'
> sudo apt autoremove
> sudo apt install ros-humble-gazebo-ros-pkgs
> ```

### 2. Build the workspace

```bash
mkdir -p ~/handeye_ws/src
cp -r <this_repo>/handeye_sim <this_repo>/scara_sim ~/handeye_ws/src/
cd ~/handeye_ws
source /opt/ros/humble/setup.bash
rosdep install --from-paths src -i -y --rosdistro humble
colcon build --symlink-install
```

For the KUKA variant, additionally build the [lbr-stack (humble-v2.0.0)](https://github.com/lbr-stack/lbr_fri_ros2_stack/releases/tag/humble-v2.0.0) with this repo's `camera_descriptions_example/` files copied over its iiwa7 description — see the [Dockerfile](Dockerfile) for the exact pinned clone/copy/build steps.

### 3. Generate ArUco marker models

The handeye config uses `DICT_ARUCO_ORIGINAL`, 0.150 m side length. Generate matching Gazebo models:

```bash
git clone --depth 1 https://github.com/mikaelarguedas/gazebo_models.git /tmp/gazebo_models
cd /tmp/gazebo_models/ar_tags/scripts
python3 generate_markers_model.py -i ../images -g ~/.gazebo/models -s 150

# IMPORTANT: the PNG images in that repo are NOT valid ArUco patterns
# (OpenCV cannot detect them). Overwrite the textures with real ones:
python3 - <<'EOF'
import cv2, os
dic = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_ARUCO_ORIGINAL)
for i in range(18):
    img = cv2.aruco.drawMarker(dic, i, 500)
    p = os.path.expanduser(f'~/.gazebo/models/marker{i}/materials/textures/Marker{i}.png')
    if os.path.exists(os.path.dirname(p)):
        cv2.imwrite(p, img)
EOF
```

Models must sit **directly** under `~/.gazebo/models/marker<N>/` (not nested in subfolders) or Gazebo's `model://marker<N>` URIs will not resolve and the marker will be invisible.

---

## Usage — SCARA

Every terminal needs this environment (note: Gazebo's own `setup.sh` is required for shaders; the empty model DB URI prevents a multi-minute startup hang):

```bash
cd ~/handeye_ws        # nodes read config via relative path src/handeye_sim/config.yaml
source /opt/ros/humble/setup.zsh          # or setup.bash
source /usr/share/gazebo/setup.sh
source ~/handeye_ws/install/setup.zsh
export GAZEBO_MODEL_DATABASE_URI=""
```

### 1. Select the SCARA handeye config

```bash
cp ~/handeye_ws/src/handeye_sim/config_scara.yaml ~/handeye_ws/src/handeye_sim/config.yaml
```

(The KUKA variant is preserved in `config_kuka_backup.yaml`; swap back anytime. No rebuild needed — config is read at runtime.)

### 2. Launch the simulation

```bash
ros2 launch scara_sim scara_moveit.launch.py
```

Starts Gazebo (grass world, sun lighting, fruit cubes, ArUco marker auto-spawned at `(0.35, 0)`), the controllers, `move_group`, and RViz with the MotionPlanning plugin. Without MoveIt: `ros2 launch scara_sim scara_bringup.launch.py`.

### 3. Move the arm

- **RViz:** MotionPlanning panel → drag the interactive marker (position only — 4 DOF cannot satisfy full 6-D pose goals; IK is configured position-only) → *Plan & Execute*. Named states `home` and `sample` are available under Goal State.
- **CLI:** `ros2 run scara_sim move <j1> <j2> <j3> <j4>` — j1/j2 shoulder/elbow (rad, ±2.62), j3 quill Z (m, −0.12…0, negative = down), j4 wrist yaw (rad, ±3.14). Example: `ros2 run scara_sim move 0.3 -1.0 -0.05 0.5`

### 4. Collect samples

In a second (sourced, `cd ~/handeye_ws`) terminal:

```bash
ros2 launch handeye_sim taking_sample_launch.py
```

An OpenCV window shows the downward camera view with detection overlay. Repeat 10–15×:

1. Move the arm to a new pose (keep the marker detected — axes drawn on it).
2. Focus the OpenCV window, press **`q`** to record the marker + robot pose pair.

Vary all four joints between samples. Press **`e`** to exit. Samples land in `src/handeye_sim/resource/{marker,robot}_data_simulation.yaml`.

### 5. Compute and visualize

```bash
ros2 run handeye_sim handeye     # writes resource/handeye_result_simulation.yaml
ros2 run handeye_sim eye2hand    # publishes result frames for RViz comparison
```

Ground truth from the URDF: camera at `xyz=(0.05, 0, 0.01)`, `rpy=(0, π/2, 0)` relative to `link_ee`.

> **SCARA caveat:** all rotation axes are parallel (vertical), so rotation between samples is yaw-only. The hand-eye Z-offset is weakly observable and will show larger error than a 6/7-DOF arm — that is the known SCARA degeneracy, not a bug.

## Usage — KUKA LBR iiwa7

```bash
# terminal 1 (lbr-stack + handeye_ws sourced)
ros2 launch lbr_bringup bringup.launch.py moveit:=true sim:=true
# spawn the marker upright facing the camera, e.g.:
ros2 run gazebo_ros spawn_entity.py -entity aruco_marker \
  -file ~/.gazebo/models/marker0/model.sdf -x 0.5 -y 0 -z 0.3 -R 0 -P 0 -Y 0

# terminal 2: swap in the KUKA config, then sample/compute exactly as above
cp ~/handeye_ws/src/handeye_sim/config_kuka_backup.yaml ~/handeye_ws/src/handeye_sim/config.yaml
ros2 launch handeye_sim taking_sample_launch.py
```

> The KUKA driver publishes frames as `lbrlink_0`…`lbrlink_ee` (**no slash** after `lbr`) — the config must match these names exactly. Verify with `ros2 topic echo /tf` if sampling raises *"Could not find link"*.

## Configuration reference (`handeye_sim/config.yaml`)

| Key | Meaning |
|---|---|
| `aruco_dictionary_name` / `aruco_marker_side_length` | Must match the spawned marker model exactly — wrong side length scales all translations |
| `image_topic` / `camera_calibration_parameters_filename` | Camera feed + intrinsics (sim camera: fx=fy=500, 640×480) |
| `base_link` / `ee_link` | Endpoints of the TF chain walked when saving robot poses |
| `link_order_publish_*` | Explicit frame chains used by the visualization nodes |

## Troubleshooting

| Symptom | Cause / fix |
|---|---|
| Gazebo takes minutes to open | Fetching from the dead online model DB — `export GAZEBO_MODEL_DATABASE_URI=""` |
| Robot invisible, `RTShaderSystem` errors | Gazebo env not sourced — `source /usr/share/gazebo/setup.sh` |
| `gzserver died, exit code 255` on launch | Orphan gzserver holding port 11345 — `killall -9 gzserver gzclient` |
| Spawners loop `waiting for service /controller_manager/...` | `gazebo_ros2_control` plugin failed: package not installed, **or** the URDF contains `": "` (colon+space, e.g. in comments) which breaks Humble's parameter parsing — check gzserver output for `parser error` |
| MoveIt plans but execution aborts, "Didn't receive robot state" | Controllers not running (above), or `use_sim_time` mismatch |
| Marker entity exists but invisible | Model folder nested wrongly — must be `~/.gazebo/models/marker<N>/` directly |
| Camera window shows marker but no detection | Marker texture isn't a real ArUco pattern (regenerate — step 3), or dictionary/side-length mismatch with config |
| `FileNotFoundError: src/handeye_sim/config.yaml` | Nodes use a relative path — always run from `~/handeye_ws` |
| `ros2 run scara_sim move` → "No executable found" | Stale overlay — re-`source ~/handeye_ws/install/setup.zsh` after building |
| Sampling crashes `Could not find link ...` | Config frame names don't match `/tf` — echo `/tf` and `/tf_static`, fix config |

## Credits

Based on [shengyangzhuang/handeye_calibration_ros2](https://github.com/shengyangzhuang/handeye_calibration_ros2) and its simulation companion. KUKA driver: [lbr-stack](https://github.com/lbr-stack/lbr_fri_ros2_stack). Marker model template: [mikaelarguedas/gazebo_models](https://github.com/mikaelarguedas/gazebo_models).
