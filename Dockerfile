# Hand-eye calibration simulation (ROS 2 Humble + Gazebo Classic + MoveIt + KUKA LBR)
#
# Build:  docker compose build        (or: docker build -t handeye_sim .)
# Run:    ./docker/run.sh             (X11 GUI: Gazebo, RViz, OpenCV windows)
FROM osrf/ros:humble-desktop-full

SHELL ["/bin/bash", "-c"]
ENV DEBIAN_FRONTEND=noninteractive

# ---------------------------------------------------------------------------
# System + Python dependencies
# ---------------------------------------------------------------------------
RUN apt-get update && apt-get install -y --no-install-recommends \
        git \
        wget \
        python3-pip \
        python3-vcstool \
        python3-opencv \
        python3-scipy \
        python3-pandas \
        python3-matplotlib \
        ros-humble-tf-transformations \
        ros-humble-cv-bridge \
        ros-humble-gazebo-ros-pkgs \
    && rm -rf /var/lib/apt/lists/*

# ---------------------------------------------------------------------------
# lbr_fri_ros2_stack (KUKA LBR driver + sim), pinned to humble-v2.0.0
# as referenced in the project README
# ---------------------------------------------------------------------------
ARG LBR_STACK_TAG=humble-v2.0.0
# fri pinned by commit, not branch: humble-v2.0.0 includes friVersion.h with
# FRICLIENT_VERSION_* macros, which later fri commits renamed
# (friClientVersion.h / FRI_CLIENT_VERSION_*), breaking the tag
ARG FRI_COMMIT=acac2f221f1c4f573c91c4ae35f903a6f4d696b7
WORKDIR /lbr-stack/src
RUN git clone --depth 1 -b ${LBR_STACK_TAG} https://github.com/lbr-stack/lbr_fri_ros2_stack.git \
    && git clone --depth 1 -b fri-1 https://github.com/lbr-stack/lbr_fri_idl.git \
    && mkdir fri && cd fri && git init -q \
    && git remote add origin https://github.com/lbr-stack/fri.git \
    && git fetch -q --depth 1 origin ${FRI_COMMIT} \
    && git checkout -q FETCH_HEAD

# Replace the iiwa7 description with the camera-equipped version from this repo
COPY camera_descriptions_example/iiwa7_description/ \
     /lbr-stack/src/lbr_fri_ros2_stack/lbr_description/urdf/iiwa7/
COPY camera_descriptions_example/iiwa7_mesh/ \
     /lbr-stack/src/lbr_fri_ros2_stack/lbr_description/meshes/iiwa7/

WORKDIR /lbr-stack
RUN apt-get update \
    && rosdep update --rosdistro humble \
    && rosdep install --from-paths src -i -y --rosdistro humble \
    && rm -rf /var/lib/apt/lists/*
RUN source /opt/ros/humble/setup.bash \
    && colcon build --cmake-args -DCMAKE_BUILD_TYPE=Release

# ---------------------------------------------------------------------------
# handeye_sim workspace
# ---------------------------------------------------------------------------
WORKDIR /handeye_ws/src
COPY handeye_sim/ /handeye_ws/src/handeye_sim/

WORKDIR /handeye_ws
RUN apt-get update \
    && rosdep install --from-paths src -i -y --rosdistro humble \
    && rm -rf /var/lib/apt/lists/*
# --symlink-install so a bind-mounted src/handeye_sim (see docker-compose.yml)
# is picked up without rebuilding
RUN source /opt/ros/humble/setup.bash \
    && source /lbr-stack/install/setup.bash \
    && colcon build --symlink-install

COPY docker/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# handeye_sim nodes read config via relative path "src/handeye_sim/..." —
# they must be run from /handeye_ws
WORKDIR /handeye_ws
ENTRYPOINT ["/entrypoint.sh"]
CMD ["bash"]
