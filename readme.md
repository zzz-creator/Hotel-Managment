# Hotel Management System

A comprehensive hotel management system built with Python, featuring:

- **User Roles:** Staff, Manager, Admin
- **Reservation Management:** Add, edit, delete, and search reservations
- **Inventory Management:** Manage items and view item lists
- **User Management:** View and manage users (admin/manager)
- **Discounts:** Apply and manage discount codes
- **Database Integration:** Uses SQL Server (configurable via `config.ini`)
- **Security:** Admin panel with password and user restrictions
- **Configurable Settings:** Hotel name, tax rate, lockout policy, and more via `config.ini`

## Getting Started

### Prerequisites

- Python 3.8+
- [pyodbc](https://pypi.org/project/pyodbc/)
- SQL Server (or compatible database)
    -  ODBC Driver 17 for SQL Server

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/zzz-creator/Hotel-Managment.git
   cd Hotel-Managment
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure the database:**
   - Edit `config.ini` with your database credentials and hotel settings.

4. **Set up the database schema:**
   - Run the provided SQL scripts to create necessary tables (Users, Reservations, Discounts, etc.).

### Running the Application

```bash
python main.py
```

## Configuration

Edit `config.ini` to set:

- Database connection (`server`, `database`, `username`, `password`)
- Hotel name, tax rate, lockout policy, etc.

## Features

- **Reservations:** Add, edit, delete, and search for reservations.
- **Inventory:** Manage hotel items.
- **User Management:** View and manage users.
- **Discounts:** Apply and manage discount codes.
- **Event & Banquet Management:** Book and manage events, seating, equipment, and catering.
- **Admin Panel:** Secure access for sensitive operations.

**Developed by [zzz-creator](https://github.com/zzz-creator)