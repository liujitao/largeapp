#!/bin/bash

source venv/bin/activate

echo "Starting graph api"
venv/bin/gunicorn -w 4 -b 0.0.0.0:5002 -D graph:app 

exit 0