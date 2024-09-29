#!/bin/bash

# Define environment variable
export FLASK_APP=run.py
export FLASK_DB_TYPE=sqlite
export FLASK_DB_PATH=/db/app.db
# Run app.py when the container launches
flask run --host=0.0.0.0