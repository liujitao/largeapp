#!/bin/sh

cd /root/largeapp
. .venv/bin/activate

celery worker -A tasks -q
celery beat -A tasks -q