#!/bin/zsh

BLENDER_VERSION=2.82
BASE_DIR=~/.config/blender/${BLENDER_VERSION}/scripts/addons

rm -r $BASE_DIR/kiritanify
cp -r ./kiritanify $BASE_DIR/
