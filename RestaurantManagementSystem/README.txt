====================================================
  Restaurant Management System - Setup Guide
====================================================

REQUIREMENTS
------------
- Python 3.8 or newer (https://www.python.org/downloads/)
- Microsoft ODBC Driver 17 for SQL Server
  Download: https://learn.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server
- SQL Server (SSMS) with RestaurantDB already created


STEP 1 — Install Python package
--------------------------------
Open a terminal / command prompt and run:

    pip install pyodbc


STEP 2 — Open in Visual Studio
--------------------------------
1. Open Visual Studio
2. Go to File > Open > File...
3. Select:  restaurant_management.py
4. Press F5 (or click Run) to start the application


STEP 3 — Connect to your database
-----------------------------------
When the app starts, a connection dialog appears:

  Server     →  Enter your SQL Server name
                Examples:
                  localhost
                  localhost\SQLEXPRESS
                  .\SQLEXPRESS
                  DESKTOP-ABC123\SQLEXPRESS

  Database   →  RestaurantDB   (leave as default)

  Auth Type  →  Windows Authentication   (if logged in with Windows)
             OR  SQL Server Authentication (enter username/password)

Click "Connect" — the main app will open.


FEATURES
--------
  Dashboard        — Live stats + recent orders
  Customers        — Add / Edit / Delete customers
  Employees        — Manage staff with roles & departments
  Departments      — Organizational units
  Roles            — Employee role definitions
  Menu Categories  — Food category management
  Menu Items       — Full menu with pricing
  Orders           — Place orders, update status, view items
  Tables           — Restaurant table management
  Reservations     — Table booking system
  Inventory        — Ingredient stock tracking + stock adjustment
  Suppliers        — Supplier directory
  Payments         — Create invoices & record payments
  Reports          — 8 built-in business analytics reports


TROUBLESHOOTING
---------------
"pyodbc not found"
  → Run:  pip install pyodbc

"ODBC Driver not found"
  → Download and install "ODBC Driver 17 for SQL Server" from Microsoft
    https://learn.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server

"Login failed"
  → Make sure SQL Server is running in SSMS
  → Try server name:  localhost\SQLEXPRESS  or  .\SQLEXPRESS
  → If using Windows Auth, make sure your Windows user has DB access

"Cannot connect to server"
  → Open SSMS and verify the server name shown at the top of Object Explorer
  → Copy that exact server name into the connection dialog
====================================================
