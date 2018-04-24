#!/bin/bash

source venv/bin/activate

echo "Starting dashboard"
venv/bin/gunicorn -w 4 -b 0.0.0.0:5001 -D run:app 

echo "Starting graph api"
venv/bin/gunicorn -w 4 -b 0.0.0.0:5002 -D graph:app 

exit 0
