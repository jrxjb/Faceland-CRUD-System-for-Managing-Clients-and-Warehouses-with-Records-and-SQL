## Project Description

This project is a CRUD system for managing clients and warehouses, where each client is assigned a warehouse and each warehouse has associated records. Data is stored in a SQL database.

- **Administrators**: Administrators manage the entire system. They have the ability to create, delete, and modify clients, warehouses, and records.
- **Client**: Represents a client associated with a custom user. Clients can only view their warehouses and records.
- **Warehouse**: Each client has a warehouse, represented with its name and address, managed through a CRUD interface.
- **Record**: Each warehouse has entry and exit records, stored in a model that handles the quantity and type of record.
- **Database**: All data is stored and managed in a SQL database.
