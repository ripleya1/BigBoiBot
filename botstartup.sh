#!/bin/bash

# Change directory to the specified path
cd /home/rey/bbbot/BigBoiBot

# Pull the latest changes from the Git repository
git pull

# Activate the Python virtual environment (assuming it exists)
source .venv/bin/activate

# Delete the previous instance of the Python script
pm2 delete bot

# Make sure that the venv has time to start before running the Python script
sleep 3

# Start the Python script using pm2
pm2 start bot.py --interpreter python3.10

# Exit the script
exit 0
