#!/bin/bash

echo "Starting graph api"

source venv/bin/activate
exec venv/bin/gunicorn -w 4 -b 0.0.0.0:5001 -D run:app 
exec venv/bin/gunicorn -w 4 -b 0.0.0.0:5002 -D graph:app 

exit 0