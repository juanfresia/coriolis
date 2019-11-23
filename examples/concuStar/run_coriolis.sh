#!/bin/bash

cargo build
cp config.txt target/
cd target/debug/
./concu-star