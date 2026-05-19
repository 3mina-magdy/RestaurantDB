-- ═══════════════════════════════════════════════════════════════════════════
-- RESTAURANT MANAGEMENT SYSTEM - SQL SERVER DATABASE SCHEMA
-- ═══════════════════════════════════════════════════════════════════════════
-- Database: RestaurantDB
-- DBMS: Microsoft SQL Server (SSMS)
-- Version: 2019+
-- Created: 2024
-- ═══════════════════════════════════════════════════════════════════════════

-- Drop database if exists and create new
USE master;
GO

IF EXISTS (SELECT name FROM sys.databases WHERE name = N'RestaurantDB')
BEGIN
    ALTER DATABASE RestaurantDB SET SINGLE_USER WITH ROLLBACK IMMEDIATE;
    DROP DATABASE RestaurantDB;
END
GO

CREATE DATABASE RestaurantDB;
GO

USE RestaurantDB;
GO

-- ═══════════════════════════════════════════════════════════════════════════
-- DOMAIN: PEOPLE
-- ═══════════════════════════════════════════════════════════════════════════

-- ───────────────────────────────────────────────────────────────────────────
-- Table: Customers
-- Description: Stores customer information with atomized address fields
-- ───────────────────────────────────────────────────────────────────────────
CREATE TABLE Customers (
    customer_id INT IDENTITY(1,1) PRIMARY KEY,
    first_name NVARCHAR(80) NOT NULL,
    last_name NVARCHAR(80) NOT NULL,
    email NVARCHAR(150) NOT NULL UNIQUE,
    address_street NVARCHAR(150) NULL,
    address_city NVARCHAR(80) NULL,
    address_postal NVARCHAR(20) NULL
);
GO

-- Indexes for Customers
CREATE INDEX IX_Customers_Email ON Customers(email);
CREATE INDEX IX_Customers_Name ON Customers(last_name, first_name);
GO

-- ───────────────────────────────────────────────────────────────────────────
-- Table: CustomerPhones
-- Description: Multi-valued phone numbers for customers (1NF compliance)
-- ───────────────────────────────────────────────────────────────────────────
CREATE TABLE CustomerPhones (
    phone_id INT IDENTITY(1,1) PRIMARY KEY,
    customer_id INT NOT NULL,
    phone_number NVARCHAR(25) NOT NULL,
    phone_type NVARCHAR(10) NOT NULL DEFAULT 'mobile' CHECK (phone_type IN ('mobile', 'home', 'work')),
    is_primary BIT NOT NULL DEFAULT 0,
    CONSTRAINT FK_CustomerPhones_Customer FOREIGN KEY (customer_id) 
        REFERENCES Customers(customer_id) ON DELETE CASCADE ON UPDATE CASCADE
);
GO

-- Indexes for CustomerPhones
CREATE INDEX IX_CustomerPhones_Customer ON CustomerPhones(customer_id);
CREATE INDEX IX_CustomerPhones_PhoneNumber ON CustomerPhones(phone_number);
GO

-- ───────────────────────────────────────────────────────────────────────────
-- Table: Departments
-- Description: Restaurant departments (Kitchen, Service, Management, etc.)
-- ───────────────────────────────────────────────────────────────────────────
CREATE TABLE Departments (
    department_id INT IDENTITY(1,1) PRIMARY KEY,
    name NVARCHAR(100) NOT NULL UNIQUE,
    description NVARCHAR(MAX) NULL
);
GO

-- Indexes for Departments
CREATE INDEX IX_Departments_Name ON Departments(name);
GO

-- ───────────────────────────────────────────────────────────────────────────
-- Table: Roles
-- Description: Employee roles (Manager, Waiter, Chef, Cashier, etc.)
-- ───────────────────────────────────────────────────────────────────────────
CREATE TABLE Roles (
    role_id INT IDENTITY(1,1) PRIMARY KEY,
    role_name NVARCHAR(60) NOT NULL UNIQUE,
    description NVARCHAR(MAX) NULL
);
GO

-- ───────────────────────────────────────────────────────────────────────────
-- Table: Employees
-- Description: Employee information with role and department assignments
-- ───────────────────────────────────────────────────────────────────────────
CREATE TABLE Employees (
    employee_id INT IDENTITY(1,1) PRIMARY KEY,
    department_id INT NOT NULL,
    role_id INT NOT NULL,
    reports_to_employee_id INT NULL, -- Self-referencing FK for hierarchy
    first_name NVARCHAR(80) NOT NULL,
    last_name NVARCHAR(80) NOT NULL,
    email NVARCHAR(150) NOT NULL UNIQUE,
    phone NVARCHAR(25) NULL,
    address_street NVARCHAR(150) NULL,
    address_city NVARCHAR(80) NULL,
    date_of_birth DATE NOT NULL,
    hire_date DATE NOT NULL,
    salary DECIMAL(10,2) NOT NULL CHECK (salary >= 0),
    is_active BIT NOT NULL DEFAULT 1,
    CONSTRAINT FK_Employees_Department FOREIGN KEY (department_id) 
        REFERENCES Departments(department_id) ON DELETE NO ACTION ON UPDATE CASCADE,
    CONSTRAINT FK_Employees_Role FOREIGN KEY (role_id) 
        REFERENCES Roles(role_id) ON DELETE NO ACTION ON UPDATE CASCADE,
    CONSTRAINT FK_Employees_Manager FOREIGN KEY (reports_to_employee_id) 
        REFERENCES Employees(employee_id) ON DELETE NO ACTION ON UPDATE NO ACTION
);
GO

-- Indexes for Employees
CREATE INDEX IX_Employees_Department ON Employees(department_id);
CREATE INDEX IX_Employees_Role ON Employees(role_id);
CREATE INDEX IX_Employees_Email ON Employees(email);
CREATE INDEX IX_Employees_Manager ON Employees(reports_to_employee_id);
GO

-- ═══════════════════════════════════════════════════════════════════════════
-- DOMAIN: MENU
-- ═══════════════════════════════════════════════════════════════════════════

-- ───────────────────────────────────────────────────────────────────────────
-- Table: MenuCategories
-- Description: Menu item categories (Burgers, Pizza, Beverages, etc.)
-- ───────────────────────────────────────────────────────────────────────────
CREATE TABLE MenuCategories (
    category_id INT IDENTITY(1,1) PRIMARY KEY,
    name NVARCHAR(100) NOT NULL UNIQUE,
    description NVARCHAR(MAX) NULL,
    display_order INT NOT NULL DEFAULT 0,
    is_active BIT NOT NULL DEFAULT 1
);
GO

-- Indexes for MenuCategories
CREATE INDEX IX_MenuCategories_Name ON MenuCategories(name);
GO

-- ───────────────────────────────────────────────────────────────────────────
-- Table: MenuItems
-- Description: Individual menu items with pricing and availability
-- ───────────────────────────────────────────────────────────────────────────
CREATE TABLE MenuItems (
    item_id INT IDENTITY(1,1) PRIMARY KEY,
    category_id INT NOT NULL,
    managed_by_employee_id INT NULL,
    name NVARCHAR(150) NOT NULL,
    description NVARCHAR(MAX) NULL,
    price DECIMAL(10,2) NOT NULL CHECK (price >= 0),
    is_available BIT NOT NULL DEFAULT 1,
    preparation_time_min INT NULL, -- Estimated prep time in minutes
    CONSTRAINT FK_MenuItems_Category FOREIGN KEY (category_id) 
        REFERENCES MenuCategories(category_id) ON DELETE NO ACTION ON UPDATE CASCADE,
    CONSTRAINT FK_MenuItems_Manager FOREIGN KEY (managed_by_employee_id) 
        REFERENCES Employees(employee_id) ON DELETE SET NULL ON UPDATE CASCADE
);
GO

-- Indexes for MenuItems
CREATE INDEX IX_MenuItems_Category ON MenuItems(category_id);
CREATE INDEX IX_MenuItems_Available ON MenuItems(is_available);
CREATE INDEX IX_MenuItems_Name ON MenuItems(name);
CREATE INDEX IX_MenuItems_Manager ON MenuItems(managed_by_employee_id);
GO

-- ───────────────────────────────────────────────────────────────────────────
-- Table: Ingredients
-- Description: Inventory of ingredients with stock tracking
-- ───────────────────────────────────────────────────────────────────────────
CREATE TABLE Ingredients (
    ingredient_id INT IDENTITY(1,1) PRIMARY KEY,
    name NVARCHAR(100) NOT NULL UNIQUE,
    unit NVARCHAR(30) NOT NULL, -- kg, litre, piece, etc.
    stock_quantity DECIMAL(10,3) NOT NULL DEFAULT 0.000 CHECK (stock_quantity >= 0),
    reorder_level DECIMAL(10,3) NOT NULL DEFAULT 0.000
);
GO

-- Indexes for Ingredients
CREATE INDEX IX_Ingredients_Name ON Ingredients(name);
GO

-- ───────────────────────────────────────────────────────────────────────────
-- Table: MenuItemIngredients
-- Description: Junction table - Recipe ingredients for menu items (M:N)
-- ───────────────────────────────────────────────────────────────────────────
CREATE TABLE MenuItemIngredients (
    item_id INT NOT NULL,
    ingredient_id INT NOT NULL,
    quantity_required DECIMAL(10,3) NOT NULL CHECK (quantity_required > 0),
    PRIMARY KEY (item_id, ingredient_id),
    CONSTRAINT FK_MenuItemIngredients_Item FOREIGN KEY (item_id) 
        REFERENCES MenuItems(item_id) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT FK_MenuItemIngredients_Ingredient FOREIGN KEY (ingredient_id) 
        REFERENCES Ingredients(ingredient_id) ON DELETE NO ACTION ON UPDATE CASCADE
);
GO

-- Indexes for MenuItemIngredients
CREATE INDEX IX_MenuItemIngredients_Item ON MenuItemIngredients(item_id);
CREATE INDEX IX_MenuItemIngredients_Ingredient ON MenuItemIngredients(ingredient_id);
GO

-- ═══════════════════════════════════════════════════════════════════════════
-- DOMAIN: ORDERING
-- ═══════════════════════════════════════════════════════════════════════════

-- ───────────────────────────────────────────────────────────────────────────
-- Table: Tables
-- Description: Restaurant table management
-- ───────────────────────────────────────────────────────────────────────────
CREATE TABLE Tables (
    table_id INT IDENTITY(1,1) PRIMARY KEY,
    table_number NVARCHAR(10) NOT NULL UNIQUE,
    capacity INT NOT NULL CHECK (capacity > 0),
    location NVARCHAR(60) NULL, -- e.g., indoor, outdoor, private room
    status NVARCHAR(20) NOT NULL DEFAULT 'available' 
        CHECK (status IN ('available', 'occupied', 'reserved', 'maintenance'))
);
GO

-- Indexes for Tables
CREATE INDEX IX_Tables_Status ON Tables(status);
GO

-- ───────────────────────────────────────────────────────────────────────────
-- Table: Reservations
-- Description: Customer table reservations
-- ───────────────────────────────────────────────────────────────────────────
CREATE TABLE Reservations (
    reservation_id INT IDENTITY(1,1) PRIMARY KEY,
    customer_id INT NOT NULL,
    table_id INT NOT NULL,
    reservation_date DATE NOT NULL,
    reservation_time TIME NOT NULL,
    party_size INT NOT NULL CHECK (party_size > 0),
    status NVARCHAR(20) NOT NULL DEFAULT 'pending' 
        CHECK (status IN ('pending', 'confirmed', 'seated', 'cancelled', 'no_show')),
    notes NVARCHAR(MAX) NULL,
    CONSTRAINT FK_Reservations_Customer FOREIGN KEY (customer_id) 
        REFERENCES Customers(customer_id) ON DELETE NO ACTION ON UPDATE CASCADE,
    CONSTRAINT FK_Reservations_Table FOREIGN KEY (table_id) 
        REFERENCES Tables(table_id) ON DELETE NO ACTION ON UPDATE CASCADE
);
GO

-- Indexes for Reservations
CREATE INDEX IX_Reservations_Customer ON Reservations(customer_id);
CREATE INDEX IX_Reservations_Table_Date ON Reservations(table_id, reservation_date);
CREATE INDEX IX_Reservations_Date_Status ON Reservations(reservation_date, status);
GO

-- ───────────────────────────────────────────────────────────────────────────
-- Table: Orders
-- Description: Customer orders (dine-in, takeaway, delivery)
-- ───────────────────────────────────────────────────────────────────────────
CREATE TABLE Orders (
    order_id INT IDENTITY(1,1) PRIMARY KEY,
    customer_id INT NOT NULL,
    employee_id INT NULL, -- Waiter/staff who took the order
    table_id INT NULL, -- NULL for takeaway/delivery
    order_type NVARCHAR(20) NOT NULL DEFAULT 'dine_in' 
        CHECK (order_type IN ('dine_in', 'takeaway', 'delivery')),
    status NVARCHAR(20) NOT NULL DEFAULT 'pending' 
        CHECK (status IN ('pending', 'confirmed', 'preparing', 'ready', 'delivered', 'cancelled')),
    total_price DECIMAL(10,2) NOT NULL DEFAULT 0.00, -- Denormalized for performance
    notes NVARCHAR(MAX) NULL,
    order_date DATETIME2 NOT NULL DEFAULT GETDATE(),
    CONSTRAINT FK_Orders_Customer FOREIGN KEY (customer_id) 
        REFERENCES Customers(customer_id) ON DELETE NO ACTION ON UPDATE CASCADE,
    CONSTRAINT FK_Orders_Employee FOREIGN KEY (employee_id) 
        REFERENCES Employees(employee_id) ON DELETE SET NULL ON UPDATE CASCADE,
    CONSTRAINT FK_Orders_Table FOREIGN KEY (table_id) 
        REFERENCES Tables(table_id) ON DELETE SET NULL ON UPDATE CASCADE
);
GO

-- Indexes for Orders
CREATE INDEX IX_Orders_Customer ON Orders(customer_id);
CREATE INDEX IX_Orders_Employee ON Orders(employee_id);
CREATE INDEX IX_Orders_Status ON Orders(status);
CREATE INDEX IX_Orders_Date ON Orders(order_date);
GO

-- ───────────────────────────────────────────────────────────────────────────
-- Table: OrderItems
-- Description: Line items for orders - Junction table (M:N)
-- ───────────────────────────────────────────────────────────────────────────
CREATE TABLE OrderItems (
    order_item_id INT IDENTITY(1,1) PRIMARY KEY,
    order_id INT NOT NULL,
    item_id INT NOT NULL,
    quantity INT NOT NULL CHECK (quantity > 0),
    unit_price DECIMAL(10,2) NOT NULL, -- Snapshot of price at time of order
    subtotal DECIMAL(10,2) NOT NULL, -- quantity × unit_price
    special_requests NVARCHAR(255) NULL,
    CONSTRAINT FK_OrderItems_Order FOREIGN KEY (order_id) 
        REFERENCES Orders(order_id) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT FK_OrderItems_MenuItem FOREIGN KEY (item_id) 
    REFERENCES MenuItems(item_id) ON DELETE NO ACTION ON UPDATE NO ACTION
);
GO

-- Indexes for OrderItems
CREATE INDEX IX_OrderItems_Order ON OrderItems(order_id);
CREATE INDEX IX_OrderItems_MenuItem ON OrderItems(item_id);
GO

-- ═══════════════════════════════════════════════════════════════════════════
-- DOMAIN: BILLING
-- ═══════════════════════════════════════════════════════════════════════════

-- ───────────────────────────────────────────────────────────────────────────
-- Table: Invoices
-- Description: Invoices for orders (1:1 relationship)
-- ───────────────────────────────────────────────────────────────────────────
CREATE TABLE Invoices (
    invoice_id INT IDENTITY(1,1) PRIMARY KEY,
    order_id INT NOT NULL UNIQUE,
    subtotal DECIMAL(10,2) NOT NULL,
    tax_rate DECIMAL(5,4) NOT NULL DEFAULT 0.1400, -- 14% VAT
    tax_amount DECIMAL(10,2) NOT NULL,
    discount_amount DECIMAL(10,2) NOT NULL DEFAULT 0.00,
    total_amount DECIMAL(10,2) NOT NULL,
    status NVARCHAR(20) NOT NULL DEFAULT 'draft' 
        CHECK (status IN ('draft', 'issued', 'paid', 'void')),
    issued_at DATETIME2 NULL,
    CONSTRAINT FK_Invoices_Order FOREIGN KEY (order_id) 
        REFERENCES Orders(order_id) ON DELETE NO ACTION ON UPDATE CASCADE
);
GO

-- Indexes for Invoices
CREATE INDEX IX_Invoices_Order ON Invoices(order_id);
CREATE INDEX IX_Invoices_Status ON Invoices(status);
GO

-- ───────────────────────────────────────────────────────────────────────────
-- Table: PaymentMethods
-- Description: Reference table for payment methods
-- ───────────────────────────────────────────────────────────────────────────
CREATE TABLE PaymentMethods (
    method_id INT IDENTITY(1,1) PRIMARY KEY,
    name NVARCHAR(60) NOT NULL UNIQUE,
    is_active BIT NOT NULL DEFAULT 1
);
GO

-- ───────────────────────────────────────────────────────────────────────────
-- Table: Payments
-- Description: Payment records (supports split payments)
-- ───────────────────────────────────────────────────────────────────────────
CREATE TABLE Payments (
    payment_id INT IDENTITY(1,1) PRIMARY KEY,
    invoice_id INT NOT NULL,
    method_id INT NOT NULL,
    amount DECIMAL(10,2) NOT NULL CHECK (amount > 0),
    paid_at DATETIME2 NOT NULL DEFAULT GETDATE(),
    reference_number NVARCHAR(100) NULL, -- Card/wallet transaction reference
    status NVARCHAR(20) NOT NULL DEFAULT 'pending' 
        CHECK (status IN ('pending', 'completed', 'failed', 'refunded')),
    CONSTRAINT FK_Payments_Invoice FOREIGN KEY (invoice_id) 
        REFERENCES Invoices(invoice_id) ON DELETE NO ACTION ON UPDATE CASCADE,
    CONSTRAINT FK_Payments_Method FOREIGN KEY (method_id) 
        REFERENCES PaymentMethods(method_id) ON DELETE NO ACTION ON UPDATE CASCADE
);
GO

-- Indexes for Payments
CREATE INDEX IX_Payments_Invoice ON Payments(invoice_id);
CREATE INDEX IX_Payments_Date ON Payments(paid_at);
GO

-- ═══════════════════════════════════════════════════════════════════════════
-- DOMAIN: OPERATIONS
-- ═══════════════════════════════════════════════════════════════════════════

-- ───────────────────────────────────────────────────────────────────────────
-- Table: Suppliers
-- Description: Ingredient and supply vendors
-- ───────────────────────────────────────────────────────────────────────────
CREATE TABLE Suppliers (
    supplier_id INT IDENTITY(1,1) PRIMARY KEY,
    name NVARCHAR(150) NOT NULL,
    contact_name NVARCHAR(100) NULL,
    email NVARCHAR(150) NULL,
    phone NVARCHAR(25) NULL,
    address NVARCHAR(255) NULL,
    is_active BIT NOT NULL DEFAULT 1
);
GO

-- Indexes for Suppliers
CREATE INDEX IX_Suppliers_Name ON Suppliers(name);
GO

-- ───────────────────────────────────────────────────────────────────────────
-- Table: StockLogs
-- Description: Audit trail for inventory movements
-- ───────────────────────────────────────────────────────────────────────────
CREATE TABLE StockLogs (
    log_id INT IDENTITY(1,1) PRIMARY KEY,
    ingredient_id INT NOT NULL,
    supplier_id INT NULL,
    employee_id INT NULL, -- Who recorded this
    change_type NVARCHAR(20) NOT NULL 
        CHECK (change_type IN ('purchase', 'usage', 'waste', 'adjustment')),
    quantity_change DECIMAL(10,3) NOT NULL, -- Positive=in, Negative=out
    unit_cost DECIMAL(10,2) NULL,
    notes NVARCHAR(MAX) NULL,
    logged_at DATETIME2 NOT NULL DEFAULT GETDATE(),
    CONSTRAINT FK_StockLogs_Ingredient FOREIGN KEY (ingredient_id) 
        REFERENCES Ingredients(ingredient_id) ON DELETE NO ACTION ON UPDATE CASCADE,
    CONSTRAINT FK_StockLogs_Supplier FOREIGN KEY (supplier_id) 
        REFERENCES Suppliers(supplier_id) ON DELETE SET NULL ON UPDATE CASCADE,
    CONSTRAINT FK_StockLogs_Employee FOREIGN KEY (employee_id) 
        REFERENCES Employees(employee_id) ON DELETE SET NULL ON UPDATE CASCADE
);
GO

-- Indexes for StockLogs
CREATE INDEX IX_StockLogs_Ingredient_Date ON StockLogs(ingredient_id, logged_at);
CREATE INDEX IX_StockLogs_Date ON StockLogs(logged_at);
GO

-- ───────────────────────────────────────────────────────────────────────────
-- Table: Shifts
-- Description: Work shift definitions
-- ───────────────────────────────────────────────────────────────────────────
CREATE TABLE Shifts (
    shift_id INT IDENTITY(1,1) PRIMARY KEY,
    name NVARCHAR(60) NOT NULL, -- Morning, Afternoon, Night
    start_time TIME NOT NULL,
    end_time TIME NOT NULL
);
GO

-- ───────────────────────────────────────────────────────────────────────────
-- Table: Attendance
-- Description: Employee attendance and shift tracking
-- ───────────────────────────────────────────────────────────────────────────
CREATE TABLE Attendance (
    attendance_id INT IDENTITY(1,1) PRIMARY KEY,
    employee_id INT NOT NULL,
    shift_id INT NOT NULL,
    work_date DATE NOT NULL,
    check_in DATETIME2 NULL,
    check_out DATETIME2 NULL,
    status NVARCHAR(20) NOT NULL DEFAULT 'present' 
        CHECK (status IN ('present', 'absent', 'late', 'half_day', 'holiday')),
    notes NVARCHAR(MAX) NULL,
    CONSTRAINT FK_Attendance_Employee FOREIGN KEY (employee_id) 
        REFERENCES Employees(employee_id) ON DELETE NO ACTION ON UPDATE CASCADE,
    CONSTRAINT FK_Attendance_Shift FOREIGN KEY (shift_id) 
        REFERENCES Shifts(shift_id) ON DELETE NO ACTION ON UPDATE CASCADE
);
GO

-- Indexes for Attendance
CREATE INDEX IX_Attendance_Employee_Date ON Attendance(employee_id, work_date);
CREATE INDEX IX_Attendance_Date ON Attendance(work_date);
GO

-- ═══════════════════════════════════════════════════════════════════════════
-- DOMAIN: SYSTEM
-- ═══════════════════════════════════════════════════════════════════════════

-- ───────────────────────────────────────────────────────────────────────────
-- Table: Users
-- Description: System user accounts (1:1 with Employees)
-- ───────────────────────────────────────────────────────────────────────────
CREATE TABLE Users (
    user_id INT IDENTITY(1,1) PRIMARY KEY,
    employee_id INT NOT NULL UNIQUE,
    username NVARCHAR(60) NOT NULL UNIQUE,
    password_hash NVARCHAR(255) NOT NULL, -- Store bcrypt hash, never plain text
    last_login DATETIME2 NULL,
    is_active BIT NOT NULL DEFAULT 1,
    CONSTRAINT FK_Users_Employee FOREIGN KEY (employee_id) 
        REFERENCES Employees(employee_id) ON DELETE CASCADE ON UPDATE CASCADE
);
GO

-- Indexes for Users
CREATE INDEX IX_Users_Username ON Users(username);
CREATE INDEX IX_Users_Employee ON Users(employee_id);
GO

-- ───────────────────────────────────────────────────────────────────────────
-- Table: AuditLogs
-- Description: System audit trail for security and compliance
-- ───────────────────────────────────────────────────────────────────────────
CREATE TABLE AuditLogs (
    log_id BIGINT IDENTITY(1,1) PRIMARY KEY,
    user_id INT NULL, -- NULL = system action
    action NVARCHAR(100) NOT NULL,
    table_name NVARCHAR(80) NOT NULL,
    record_id INT NULL,
    old_values NVARCHAR(MAX) NULL, -- JSON
    new_values NVARCHAR(MAX) NULL, -- JSON
    ip_address NVARCHAR(45) NULL, -- Supports IPv6
    logged_at DATETIME2 NOT NULL DEFAULT GETDATE(),
    CONSTRAINT FK_AuditLogs_User FOREIGN KEY (user_id) 
        REFERENCES Users(user_id) ON DELETE SET NULL ON UPDATE CASCADE
);
GO

-- Indexes for AuditLogs
CREATE INDEX IX_AuditLogs_User_Date ON AuditLogs(user_id, logged_at);
CREATE INDEX IX_AuditLogs_Table_Record ON AuditLogs(table_name, record_id);
CREATE INDEX IX_AuditLogs_Date ON AuditLogs(logged_at);
GO

-- ═══════════════════════════════════════════════════════════════════════════
-- SAMPLE DATA INSERTION
-- ═══════════════════════════════════════════════════════════════════════════

PRINT 'Inserting sample data...';
GO

-- Insert Departments
INSERT INTO Departments (name, description) VALUES
('Kitchen', 'Food preparation and cooking'),
('Service', 'Customer service and waitstaff'),
('Management', 'Restaurant management and administration'),
('Finance', 'Accounting and financial operations');
GO

-- Insert Roles
INSERT INTO Roles (role_name, description) VALUES
('Manager', 'Restaurant manager with full authority'),
('Head Chef', 'Chief of kitchen operations'),
('Chef', 'Cooking staff'),
('Waiter', 'Front-of-house service staff'),
('Cashier', 'Payment processing and billing'),
('Supervisor', 'Shift supervisor');
GO

-- Insert Sample Employees
INSERT INTO Employees (department_id, role_id, reports_to_employee_id, first_name, last_name, email, phone, address_street, address_city, date_of_birth, hire_date, salary, is_active)
VALUES
(3, 1, NULL, 'John', 'Smith', 'john.smith@restaurant.com', '555-0101', '123 Main St', 'New York', '1980-05-15', '2020-01-01', 75000.00, 1),
(1, 2, 1, 'Maria', 'Garcia', 'maria.garcia@restaurant.com', '555-0102', '456 Oak Ave', 'New York', '1985-08-22', '2020-02-01', 55000.00, 1),
(1, 3, 2, 'James', 'Wilson', 'james.wilson@restaurant.com', '555-0103', '789 Pine Rd', 'New York', '1990-03-10', '2021-06-15', 38000.00, 1),
(2, 4, 1, 'Emily', 'Davis', 'emily.davis@restaurant.com', '555-0104', '321 Elm St', 'New York', '1995-11-30', '2022-01-10', 32000.00, 1);
GO

-- Insert Menu Categories
INSERT INTO MenuCategories (name, description, display_order, is_active) VALUES
('Burgers', 'Gourmet burgers and sandwiches', 1, 1),
('Pizza', 'Wood-fired pizzas', 2, 1),
('Pasta', 'Italian pasta dishes', 3, 1),
('Salads', 'Fresh salads and healthy options', 4, 1),
('Beverages', 'Soft drinks, juices, and specialty drinks', 5, 1),
('Desserts', 'Sweet treats and desserts', 6, 1);
GO

-- Insert Menu Items
INSERT INTO MenuItems (category_id, managed_by_employee_id, name, description, price, is_available, preparation_time_min) VALUES
(1, 2, 'Classic Burger', 'Beef patty with lettuce, tomato, onion, and special sauce', 12.99, 1, 15),
(1, 2, 'Cheese Burger', 'Classic burger with aged cheddar cheese', 14.99, 1, 15),
(1, 2, 'Bacon Burger', 'Classic burger with crispy bacon strips', 15.99, 1, 18),
(2, 2, 'Margherita Pizza', 'Fresh mozzarella, tomato sauce, and basil', 13.99, 1, 20),
(2, 2, 'Pepperoni Pizza', 'Classic pepperoni with mozzarella', 15.99, 1, 20),
(3, 2, 'Spaghetti Carbonara', 'Creamy carbonara with pancetta', 14.99, 1, 25),
(3, 2, 'Fettuccine Alfredo', 'Rich alfredo sauce with parmesan', 13.99, 1, 22),
(4, 2, 'Caesar Salad', 'Romaine lettuce, croutons, parmesan, Caesar dressing', 9.99, 1, 10),
(4, 2, 'Greek Salad', 'Mixed greens, feta, olives, cucumber, tomato', 10.99, 1, 10),
(5, 2, 'Coca Cola', 'Classic Coca Cola', 2.99, 1, 2),
(5, 2, 'Fresh Orange Juice', 'Freshly squeezed orange juice', 4.99, 1, 5),
(6, 2, 'Chocolate Cake', 'Rich chocolate layer cake', 6.99, 1, 5),
(6, 2, 'Tiramisu', 'Classic Italian tiramisu', 7.99, 1, 5);
GO

-- Insert Ingredients
INSERT INTO Ingredients (name, unit, stock_quantity, reorder_level) VALUES
('Beef Patty', 'piece', 500.000, 100.000),
('Burger Buns', 'piece', 300.000, 50.000),
('Lettuce', 'kg', 25.000, 5.000),
('Tomatoes', 'kg', 30.000, 8.000),
('Onions', 'kg', 20.000, 5.000),
('Cheddar Cheese', 'kg', 15.000, 3.000),
('Bacon', 'kg', 12.000, 3.000),
('Pizza Dough', 'piece', 200.000, 40.000),
('Mozzarella', 'kg', 25.000, 5.000),
('Tomato Sauce', 'litre', 15.000, 3.000),
('Pepperoni', 'kg', 10.000, 2.000),
('Pasta', 'kg', 40.000, 10.000),
('Cream', 'litre', 20.000, 5.000),
('Parmesan', 'kg', 8.000, 2.000),
('Eggs', 'piece', 200.000, 50.000);
GO

-- Insert Tables
INSERT INTO Tables (table_number, capacity, location, status) VALUES
('T01', 2, 'indoor', 'available'),
('T02', 2, 'indoor', 'available'),
('T03', 4, 'indoor', 'available'),
('T04', 4, 'indoor', 'available'),
('T05', 6, 'indoor', 'available'),
('T06', 4, 'outdoor', 'available'),
('T07', 4, 'outdoor', 'available'),
('T08', 8, 'private room', 'available');
GO

-- Insert Customers
INSERT INTO Customers (first_name, last_name, email, address_street, address_city, address_postal) VALUES
('Alice', 'Johnson', 'alice.johnson@email.com', '111 Broadway', 'New York', '10001'),
('Bob', 'Brown', 'bob.brown@email.com', '222 Park Ave', 'New York', '10002'),
('Carol', 'White', 'carol.white@email.com', '333 5th Ave', 'New York', '10003'),
('David', 'Miller', 'david.miller@email.com', '444 Madison Ave', 'New York', '10004'),
('Emma', 'Taylor', 'emma.taylor@email.com', '555 Lexington Ave', 'New York', '10005');
GO

-- Insert Customer Phones
INSERT INTO CustomerPhones (customer_id, phone_number, phone_type, is_primary) VALUES
(1, '555-1001', 'mobile', 1),
(1, '555-1002', 'home', 0),
(2, '555-2001', 'mobile', 1),
(3, '555-3001', 'mobile', 1),
(4, '555-4001', 'mobile', 1),
(5, '555-5001', 'mobile', 1);
GO

-- Insert Payment Methods
INSERT INTO PaymentMethods (name, is_active) VALUES
('Cash', 1),
('Credit Card', 1),
('Debit Card', 1),
('Mobile Wallet', 1),
('Gift Card', 1);
GO

-- Insert Shifts
INSERT INTO Shifts (name, start_time, end_time) VALUES
('Morning', '06:00:00', '14:00:00'),
('Afternoon', '14:00:00', '22:00:00'),
('Night', '22:00:00', '06:00:00');
GO

-- Insert Suppliers
INSERT INTO Suppliers (name, contact_name, email, phone, address, is_active) VALUES
('Fresh Foods Inc', 'Michael Green', 'orders@freshfoods.com', '555-7001', '100 Supplier Lane, New York', 1),
('Quality Meats Co', 'Sarah Black', 'contact@qualitymeats.com', '555-7002', '200 Butcher St, New York', 1),
('Dairy Delights', 'Tom Anderson', 'info@dairydelights.com', '555-7003', '300 Milk Road, New York', 1);
GO

PRINT 'Database creation completed successfully!';
PRINT 'Total tables created: 25';
PRINT 'Sample data inserted for testing and demonstration.';
GO

-- ═══════════════════════════════════════════════════════════════════════════
-- USEFUL QUERIES FOR VERIFICATION
-- ═══════════════════════════════════════════════════════════════════════════

-- List all tables
SELECT TABLE_NAME, TABLE_TYPE 
FROM INFORMATION_SCHEMA.TABLES 
WHERE TABLE_TYPE = 'BASE TABLE'
ORDER BY TABLE_NAME;
GO

-- Count records in each table
PRINT '--- Record Counts ---';
SELECT 'Customers' AS TableName, COUNT(*) AS RecordCount FROM Customers
UNION ALL SELECT 'Employees', COUNT(*) FROM Employees
UNION ALL SELECT 'MenuCategories', COUNT(*) FROM MenuCategories
UNION ALL SELECT 'MenuItems', COUNT(*) FROM MenuItems
UNION ALL SELECT 'Ingredients', COUNT(*) FROM Ingredients
UNION ALL SELECT 'Tables', COUNT(*) FROM Tables
UNION ALL SELECT 'Departments', COUNT(*) FROM Departments
UNION ALL SELECT 'Roles', COUNT(*) FROM Roles
UNION ALL SELECT 'PaymentMethods', COUNT(*) FROM PaymentMethods
UNION ALL SELECT 'Shifts', COUNT(*) FROM Shifts
UNION ALL SELECT 'Suppliers', COUNT(*) FROM Suppliers;
GO
