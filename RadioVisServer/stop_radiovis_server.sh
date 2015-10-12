#!/usr/bin/env bash

# This script stops the RadioVis Server using supervisord

echo "This script stops the RadioVis Server using supervisord"
read -p "RadioVis Server folder is: (~/gitrepo-radiovis/RadioVisServer) " vis_path
vis_path=${vis_path:-~/gitrepo-radiovis/RadioVisServer/}

echo "Stopping RadioVIS Server in $vis_path..."

cd $vis_path
supervisorctl -c supervisord-radiovis.conf stop radiovisserver
supervisorctl -c supervisord-radiovis.conf shutdown