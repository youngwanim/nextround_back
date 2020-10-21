#!/bin/bash

echo "Start running server for rana..."
source ../venv/bin/activate
PYTHONIOENCODING=UTF-8 ./manage.py runserver 0:8010 --settings=config.development.settings

