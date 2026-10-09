# Revature-In-Training-Project-Alt-1
A web application built in a similar fashion to the one built in "Revature-In-Training-Project" repository.

This web application is a management system for monitoring farm-related assets, such as farm facilities, equipments, hands, field jobs, service reports, and supervisors. It runs using a React frontend made in JavaScript that displays data points by sending HTTP requests to a Python backend that then communicates with a PostgresSQL database, where the actual data points are stored, and then sends the requested data back to the frontend.

This application was designed to be run using cloud services like AWS.

## Setup
Open the ".env" file in the "\backend" directory. Fill in whatever is missing.

Observe the "setup.sh" and "seed.sh". Run "setup.sh" in whatever directory you wish to contain this application. Then run "seed.sh {local|rds}". Pick either "local" or "rds" to tell the script where you want the database to be located.