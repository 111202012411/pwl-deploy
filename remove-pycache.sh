#!/usr/bin/env bash


while IFS= read -r line; do

  rm -rvf "$line"
done<<<$(find . -type d | grep -i pycache)
