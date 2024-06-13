# LMNH Pipeline & Historical Data Migration

This repository contains the all the code, documentation and resources required for the ETL pipeline and the data migration to an s3 bucket for long-term storage for Liverpool Natural History Museum. 

The pipeline serves to monitor the health of the plants over time in the botanical wing of the museum and alerts the gardeners when there is a problem.

## Folders (Project Spice Rack)

| Folder Name | Description |
|---|---|
| **aws-infrastructure ️** | Cloud Castle! Code for provisioning and managing AWS resources. |
| **database ️** | The Data Vault! Stores all the project's information. |
| **Diagrams ️**  |  See the big picture! Images that map out the project for easy understanding. |
| **.github** |  Automation Station! Essential files for your GitHub repository. |
| **historical-data-migration** | Old but gold! Moves old data from the database to a safe and sound S3 bucket. |
| **pipeline**  | ETL magic! Code that brings data from the API to the database. |

## Installation
To install the required dependencies, use the following commands:

1. **Clone the repository**:
    ```bash
    git clone https://github.com/danfh00/vodnik-plant-health-monitor.git
    ```

2. **Create and activate a virtual environment (optional but recommended)**:
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    ```

3. **Install the dependencies**:
    ```bash
    pip3 install -r requirements.txt
    ```

## Architecture Diagram

For a visual representation of the project architecture, refer to the diagram below.

![Architecture Diagram](https://github.com/danfh00/vodnik-plant-health-monitor/blob/main/Diagrams/plant_monitor_architecture.png?raw=true)

## Database Schema

For a visual representation of the database schema, refer to the Entity-Relationship Diagram (ERD)

![ERD Diagram](https://github.com/danfh00/vodnik-plant-health-monitor/blob/main/Diagrams/plant_monitor_schema.drawio.png?raw=true)

## Database Seeding with .env configuration

- Create an .env file

- Edit the .env file to provide the following information:
    - Database Connection Details (DB_HOST,DB_PORT,DB_USER, DB_PASSWORD, DB_NAME, DB_SCHEMA)

| ✨ KEY | Placeholder |
|---|---|
|---|---|
|  DB_HOST | localhost |
|  DB_PORT  |  3306 |
|  DB_PASSWORD  |  *your_username*  |
|  DB_USER  |  *your_password*  |
|  DB_NAME  |  *your_db_name*  |
|  DB_SCHEMA  |  *your_db_schema*  |


> [!IMPORTANT]  
> To be able to run these scripts the following details must be provided in the `.env` file and should NOT be shared.

- Run these commands:
    ```bash
    cd database
    source .env
    sqlcmd -S $DB_HOST,$DB_PORT -d $DB_NAME -U $DB_USER -P $DB_PASSWORD -i schema.sql
    python3 seeding.py
    ```


    
    
