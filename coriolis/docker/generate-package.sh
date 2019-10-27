#! /bin/bash

mkdir -p pkg/usr/local/sbin
cp dist/coriolis pkg/usr/local/sbin

fpm -s dir -t deb --deb-systemd docker/coriolis-mongo.service -v ${VERSION} -n coriolis -C pkg -p dist .
