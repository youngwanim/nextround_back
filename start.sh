#!/bin/bash

echo "Start running server for rana..."
source ../venv/bin/activate
./manage.py runserver 0:8010 --settings=config.development.settings

