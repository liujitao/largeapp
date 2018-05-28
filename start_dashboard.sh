#!/bin/bash

source venv/bin/activate

echo "Starting dashboard"
venv/bin/gunicorn -w 2 -b 0.0.0.0:5001 -D run:app 

exit 0
