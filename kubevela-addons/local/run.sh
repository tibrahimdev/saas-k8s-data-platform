#!/bin/sh
ADDON=./lalala/

vela addon enable $ADDON \
  jupyterhub.enabled=true \
  -V 2 --dry-run
