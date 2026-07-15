# Docker usage

Everything from the [README](README.md) example (ROS 2 Humble, Gazebo Classic, MoveIt,
`lbr_fri_ros2_stack` humble-v2.0.0 with the camera description files already installed,
and the `handeye_sim` package pre-built) runs inside one container.

## Build

```bash
docker compose build
```

## Run

```bash
chmod +x docker/run.sh docker/entrypoint.sh   # first time only
./docker/run.sh
```

The script grants X11 access (`xhost +local:docker`) and drops you into a shell in
`/handeye_ws` with both workspaces sourced. Run it again from another terminal to open
additional shells in the same container.

## Workflow (matches README steps 2–5)

Terminal 1 — bring up the robot (Gazebo + MoveIt + RViz):

```bash
ros2 launch lbr_bringup bringup.launch.py moveit:=true sim:=true
```

Terminal 2 — take samples:

```bash
ros2 launch handeye_sim taking_sample_launch.py
```

Press `q` in the camera window to record a sample, `e` to exit. Samples and results are
written to `handeye_sim/resource/` — the package directory is bind-mounted, so they
persist on the host.

Compute calibration / visualize:

```bash
ros2 run handeye_sim handeye
ros2 run handeye_sim eye2hand
```

## Notes

- **Run nodes from `/handeye_ws`** (the default working directory): the `handeye_sim`
  nodes read `src/handeye_sim/config.yaml` and friends via relative paths.
- `handeye_sim` is bind-mounted and was built with `--symlink-install`, so Python edits
  on the host take effect without rebuilding. If you add new entry points or data files,
  rebuild inside the container: `colcon build --symlink-install` in `/handeye_ws`.
- The ArUco marker model still has to be added to the Gazebo scene, same as the README
  describes (see [gazebo_models](https://github.com/mikaelarguedas/gazebo_models/tree/master)).
  Marker side length must match `aruco_marker_side_length` in `handeye_sim/config.yaml`
  (0.150 m).
- NVIDIA GPU rendering is enabled (`runtime: nvidia`, `gpus: all`; requires
  nvidia-container-toolkit). On a machine without NVIDIA, remove those two lines —
  the `/dev/dri` passthrough covers Intel/AMD via Mesa. On hybrid (Optimus) laptops
  where GL still falls back to Mesa, uncomment the `__NV_PRIME_RENDER_OFFLOAD` /
  `__GLX_VENDOR_LIBRARY_NAME` lines.
