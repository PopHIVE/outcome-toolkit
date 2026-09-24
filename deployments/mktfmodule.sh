#!/bin/bash

TARGET_DIR=$1

mkdir -p ${TARGET_DIR}
touch ${TARGET_DIR}/main.tf ${TARGET_DIR}/outputs.tf ${TARGET_DIR}/variables.tf
