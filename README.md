# Faceland: CRUD System for Managing Clients and Warehouses with Records and SQL

## Project Description

This project is a CRUD system for managing clients and warehouses, where each client is assigned a warehouse and each warehouse has associated records. Data is stored in a SQL database.

- **Administrators**: Administrators manage the entire system. They have the ability to create, delete, and modify clients, warehouses, and records.
- **Client**: Represents a client associated with a custom user. Clients can only view their warehouses and records.
- **Warehouse**: Each client can have multiple warehouses, each represented with its name and address, managed through a CRUD interface.
- **Record**: Each warehouse can have multiple entry and exit records, stored in a model that handles the quantity and type of record.
- **Database**: All data is stored and managed in a SQLite3 database.



## Installation

### Clone the Repository

Clone the GitHub repository using HTTPS with the following command:

```bash
git clone https://github.com/jrxjb/Faceland-CRUD-System-for-Managing-Clients-and-Warehouses-with-Records-and-SQL.git
```

## Django Project Setup

### 1. Create the Migrations Folder and __init__.py

```bash
To ensure that your `app` application has the following structure:

├── __init__.py
├── admin.py
├── apps.py
├── models.py
├── migrations/
│   └── __init__.py
├── tests.py
└── views.py
```

### 2. Create and Apply Migrations

Run the following commands to create and apply the migrations for your `app` application:

```bash
python manage.py makemigrations app
python manage.py migrate

python manage.py createsuperuser

Name: your_name
Email: your_email
Password: tyour_password
```

## Acknowledgment

This project was developed as part of my work at Faceland. I acknowledge the company's ownership of the intellectual property contained within this repository. Special thanks to Faceland for allowing me to share this project publicly.
