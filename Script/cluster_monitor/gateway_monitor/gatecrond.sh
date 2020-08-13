#!/bin/sh

for(( i = 1; i <= 11; i++)); do
    /root/miniconda3/bin/python3 /data/cluster_monitor/gateway_monitor/agent_push.py
    sleep 5
done
