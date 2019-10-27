#! /bin/bash

mkdir -p pkg/usr/local/sbin
mkdir -p pkg/etc/systemd/system

cp dist/coriolis pkg/usr/local/sbin
cp docker/coriolis-mongo.service pkg/etc/systemd/system

fpm -s dir -t deb -v ${VERSION} -n coriolis -C pkg -p dist .
