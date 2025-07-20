-- Users Table
CREATE TABLE Users (
    UserID INT IDENTITY(1,1) PRIMARY KEY,
    Username NVARCHAR(50) NOT NULL UNIQUE,
    PasswordHash NVARCHAR(255) NOT NULL,
    Role NVARCHAR(20) NOT NULL, -- 'staff', 'manager', 'admin'
    CreatedAt DATETIME DEFAULT GETDATE()
);

-- Reservations Table
CREATE TABLE Reservations (
    ReservationID INT IDENTITY(1,1) PRIMARY KEY,
    RoomNumber NVARCHAR(10) NOT NULL,
    Floor INT,
    LastName NVARCHAR(50),
    FirstName NVARCHAR(50),
    CheckInDate DATE,
    CheckOutDate DATE,
    Status NVARCHAR(20) DEFAULT 'Active', -- 'Active', 'CheckedOut', etc.
    CreatedAt DATETIME DEFAULT GETDATE()
);

-- Items Table (Inventory)
CREATE TABLE Items (
    ItemID INT IDENTITY(1,1) PRIMARY KEY,
    ItemName NVARCHAR(100) NOT NULL,
    Quantity INT NOT NULL,
    Price DECIMAL(10,2) NOT NULL,
    Description NVARCHAR(255),
    CreatedAt DATETIME DEFAULT GETDATE()
);
-- Discounts Table
CREATE TABLE Discounts (
    Code VARCHAR(50) PRIMARY KEY,
    DiscountPercentage DECIMAL(5,2) NOT NULL,
    CreatedAt DATETIME DEFAULT GETDATE()
);
CREATE TABLE ValetVehicles (
    ValetID INT IDENTITY(1,1) PRIMARY KEY,
    LicensePlate NVARCHAR(20) NOT NULL,
    OwnerName NVARCHAR(100) NOT NULL,
    ParkingSpot NVARCHAR(20),
    Status NVARCHAR(20) DEFAULT 'Checked-In', -- 'Checked-In', 'Checked-Out'
    CheckInTime DATETIME DEFAULT GETDATE(),
    CheckOutTime DATETIME NULL,
    CreatedAt DATETIME DEFAULT GETDATE()
);
