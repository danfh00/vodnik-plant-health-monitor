## Installation
To install the required dependencies, use the following commands:

1. Clone the repository:
    ```bash
    git clone https://github.com/danfh00/vodnik-plant-health-monitor.git
    ```

2. Create and activate a virtual environment (optional but recommended):
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    ```

3. Install the dependencies:
    ```bash
    pip3 install -r requirements.txt
    ```

## Database Schema

For a visual representation of the database schema, refer to the Entity-Relationship Diagram (ERD) [here](https://drive.google.com/file/d/18e4ZKe5SESNqgFOiJLxeg7m3RrWLn0S6/view?usp=sharing "ERD Link").

## Database Seeding with .env configuration
1. Create a .env file:
    - Edit the .env file to provide the following information:
        - Database Connection Details (DB_HOST,DB_PORT,DB_USER, DB_PASSWORD, DB_NAME, DB_SCHEMA)
    - Here is a common structure for .env:
    ```bash
    # .env: An example for environment variables

    # Database connection details (replace with your actual credentials)
    DB_HOST=localhost
    DB_PORT=3306
    DB_USERNAME=your_username
    DB_PASSWORD=your_password
    DB_NAME=your_database_name

    # Don't commit this file to version control
    ```

2. Run these commands:
    ```bash
    cd database
    source .env
    sqlcmd -S $DB_HOST,$DB_PORT -d $DB_NAME -U $DB_USER -P $DB_PASSWORD -i schema.sql
    python3 seeding.py
    ```


    
    
