#!/bin/bash

cmake . && make VERBOSE=1
./tp1 --config ./config/config.json