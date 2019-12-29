#!/bin/bash -x
#http://fabiorehm.com/blog/2014/09/11/running-gui-apps-with-docker/
X11_HOST_IP=$(ifconfig en0 | grep inet | awk ‘$1==”inet” {print $2}’)
xhost + $ip