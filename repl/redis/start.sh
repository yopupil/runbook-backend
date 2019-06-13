#!/bin/bash

pip install tornado==5.0.0
pip install flask-socketio==3.3.2
pip install redis==2.10.6

python /opt/current/redis_server.py
