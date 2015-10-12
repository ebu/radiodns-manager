#!/usr/bin/env bash

# This script starts the RadioVis Server using supervisord

echo "This script starts the RadioVis Server using supervisord"
read -p "RadioVis Server folder is: (~/gitrepo-radiovis/RadioVisServer) " vis_path
vis_path=${vis_path:-~/gitrepo-radiovis/RadioVisServer/}

echo "Starting RadioVIS Server in $vis_path"

cd $vis_path
supervisord -c supervisord-radiovis.conf
