#!/bin/bash
set -e

source /opt/ros/humble/setup.bash
source /lbr-stack/install/setup.bash
source /handeye_ws/install/setup.bash

exec "$@"
