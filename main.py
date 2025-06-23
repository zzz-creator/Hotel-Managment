from decimal import Decimal
import logging
import os
import sys
import time
import pyodbc
import random
import string
import getpass
from datetime import datetime, timedelta
import configparser

# Database connection settings
config = configparser.ConfigParser()
config_path = os.path.join(os.path.dirname(__file__), 'config.ini')
config.read(config_path)

server = config.get('database', 'server', fallback='' )
database = config.get('database', 'database', fallback='')
username = config.get('database', 'username', fallback='')
password = config.get('database', 'password', fallback='')
HOTEL_NAME = config.get('hotel', 'name', fallback='')
TAX_RATE = config.getfloat('hotel', 'tax', fallback=0)
LOCKOUT_THRESHOLD = config.getint('hotel', 'lockout_threshold', fallback=3)
LOCKOUT_DURATION = config.getint('hotel', 'lockout_duration', fallback=5)
# Set up logging
#logging.basicConfig(filename='hotel_management.log', level=logging.DEBUG, format='%(asctime)s:%(levelname)s:%(message)s')
class CustomFormatter(logging.Formatter):
    def format(self, record):
        if record.levelno == logging.INFO:
            return record.getMessage()
        return f"{record.levelname}: {record.getMessage()}"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

# Apply the custom formatter to all handlers
for handler in logger.handlers:
    handler.setFormatter(CustomFormatter())
#Lockout settings: control the lockout mechanism for failed login attempts


def create_connection():
    try:
        connection_string = (
            'DRIVER={ODBC Driver 17 for SQL Server};'
            'SERVER=' + server + ';'
            'DATABASE=' + database + ';'
            'UID=' + username + ';'
            'PWD=' + password
        )
        connection = pyodbc.connect(connection_string)
        logging.debug("Connection successful!")
        return connection
    except Exception as e:
        logging.info("Connection Failed.")
        logging.error(f"{e}")
        logging.info("Exiting program.")
        sys.exit(1)

def generate_code():
    """Generate a random 5-character alphanumeric code."""
    return ''.join(random.choices(string.ascii_letters + string.digits, k=5))

def display_items():
    conn = create_connection()
    if conn is None:
        return
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT ItemID, Name FROM Items")  # Select only needed columns
        rows = cursor.fetchall()
        logging.info("Service/Item Price")
        for row in rows:
            item_id = row[0]  # Assuming ItemID is the first column
            name = row[1]    # Assuming Name is the second column
            price = get_dynamic_price(item_id)  # Get the price dynamically
            if price is not None:
                logging.info(f"{item_id}. {name} ${price:.2f}")  # Format price to 2 decimal places
            else:
                SystemExit("Item not found or price could not be retrieved.")
    except Exception as e:
        logging.error(f"Error displaying items: {e}")
    finally:
        conn.close()
'''def get_item_choice():
    while True:
        try:
            display_items()
            choice = int(input("Which service/item do you want? "))
            conn = create_connection()
            if conn is None:
                return None
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM Items WHERE ItemID = ?", (choice,))
            item = cursor.fetchone()
            ()
            if item:
                return choice
            else:
                logging.info("Invalid choice. Please try again.")
        except ValueError:
            logging.info("Invalid input. Please enter a number.")
        except Exception as e:
            logging.error(f"Error getting item choice: {e}")'''

def get_quantity():
    while True:
        try:
            quantity = int(input("How many? "))
            if quantity > 0:
                return quantity
            else:
                logging.info("Quantity must be a positive number. Please try again.")
        except ValueError:
            logging.info("Invalid input. Please enter a number.")
        except Exception as e:
            logging.error(f"Error getting quantity: {e}")

def get_another_item():
    while True:
        again = input("Would you like to order another service/item? (Yes/No) ").strip().lower()
        if again in ['yes', 'no']:
            return again == 'yes'
        else:
            logging.info("Invalid input. Please enter 'Yes' or 'No'.")

def validate_room():
    while True:
        try:
            last_name = input("Please enter your last name: ").strip()
            room_number = input("Please enter your room number (floor + 3-digit code): ").strip()

            conn = create_connection()
            if conn is None:
                return None, None
            cursor = conn.cursor()
            cursor.execute("SELECT RoomNumber, FirstName FROM Reservations WHERE LastName = ?", (last_name,))
            reservations = cursor.fetchall()
            ()

            if reservations:
                logging.info("Available reservations with the same last name:")
                for idx, reservation in enumerate(reservations, 1):
                    logging.info(f"{idx}. Room Number: {reservation.RoomNumber}, First Name: {reservation.FirstName}")

                try:
                    choice = int(input("Please select the reservation number: "))
                    if 1 <= choice <= len(reservations):
                        selected_reservation = reservations[choice - 1]
                        if selected_reservation.RoomNumber == room_number:
                            logging.info("Please wait while we validate your room number and last name.")
                            time.sleep(2)  # Simulate a delay for validation
                            return room_number, selected_reservation.FirstName
                        else:
                            logging.info("Room number does not match the selected reservation. Please try again.")
                    else:
                        logging.info("Invalid selection. Please try again.")
                except ValueError:
                    logging.info("Invalid input. Please enter a number.")
            else:
                logging.info("No reservations found with that last name. Please try again.")
        except Exception as e:
            logging.error(f"Error validating room: {e}")
        finally:
            conn.close()


def add_reservation():
    try:
        room_number = input("Enter room number (floor + 3-digit code): ").strip()
        floor = int(room_number[:-3])  # Extract the floor from the first digit
        last_name = input("Enter last name: ").strip()
        first_name = input("Enter first name: ").strip()
        conn = create_connection()
        if conn is None:
            return
        cursor = conn.cursor()
        cursor.execute("IF NOT EXISTS (SELECT * FROM Reservations WHERE RoomNumber = ?) "
                       "INSERT INTO Reservations (RoomNumber, Floor, LastName, FirstName) VALUES (?, ?, ?, ?)",
                       (room_number, room_number, floor, last_name, first_name))
        conn.commit()
        logging.info(f"Reservation for room {room_number} on floor {floor} added successfully.")
    except Exception as e:
        logging.error(f"Error adding reservation: {e}")
    finally:
        conn.close()


def delete_reservation():
    try:
        room_number = input("Enter room number (floor + 3-digit code) to delete: ").strip()
        conn = create_connection()
        if conn is None:
            return
        cursor = conn.cursor()
        cursor.execute("DELETE FROM Reservations WHERE RoomNumber = ?", (room_number,))
        conn.commit()
        logging.info(f"Reservation for room {room_number} deleted successfully.")
    except Exception as e:
        logging.error(f"Error deleting reservation: {e}")
    finally:
        conn.close()

def edit_reservation():
    """Edit an existing reservation, including the room number and floor."""
    conn = create_connection()
    if conn is None:
        return

    try:
        cursor = conn.cursor()
        old_room_number = input("Enter the current room number (floor + 3-digit code) of the reservation to edit: ").strip()

        cursor.execute("SELECT * FROM Reservations WHERE RoomNumber = ?", (old_room_number,))
        reservation = cursor.fetchone()

        if reservation:
            logging.info(f"Current reservation details: Room Number: {reservation.RoomNumber}, Floor: {reservation.Floor}, Last Name: {reservation.LastName}, First Name: {reservation.FirstName}")

            new_room_number = input("Enter new room number (floor + 3-digit code) (leave blank to keep current): ").strip()
            new_last_name = input("Enter new last name (leave blank to keep current): ").strip()
            new_first_name = input("Enter new first name (leave blank to keep current): ").strip()

            if new_room_number == "":
                new_room_number = old_room_number
            if new_last_name == "":
                new_last_name = reservation.LastName
            if new_first_name == "":
                new_first_name = reservation.FirstName

            # Calculate new floor from new room number
            if len(new_room_number) > 3:
                new_floor = new_room_number[:-3] 
            else:
                logging.info("Invalid room number format. Using old floor.")
                new_floor = old_room_number[:-3]
            

            # Check if the new room number is already in use
            if new_room_number != old_room_number:
                cursor.execute("SELECT * FROM Reservations WHERE RoomNumber = ?", (new_room_number,))
                existing_reservation = cursor.fetchone()
                if existing_reservation:
                    logging.info(f"Room number {new_room_number} is already occupied.")
                    return

            # Update the reservation
            cursor.execute("""
                UPDATE Reservations
                SET RoomNumber = ?, LastName = ?, FirstName = ?, Floor = ?
                WHERE RoomNumber = ?""",
                (new_room_number, new_last_name, new_first_name, new_floor, old_room_number))
            conn.commit()
            logging.info(f"Reservation for room {old_room_number} updated successfully. \n New details: Room Number: {new_room_number}, Floor: {new_floor}, Last Name: {new_last_name}, First Name: {new_first_name}")
        else:
            logging.info("No reservation found with that room number.")
    except Exception as e:
        logging.error(f"Error editing reservation: {e}")
    finally:
        conn.close()

def edit_user():
    """Edit an existing user."""
    try:
        username = input("Enter the username of the user to edit: ").strip()

        conn = create_connection()
        if conn is None:
            return

        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Users WHERE Username = ?", (username,))
        user = cursor.fetchone()

        if user:
            logging.info(f"Current user details: Username: {user.Username}")

            new_username = input("Enter new username (leave blank to keep current): ").strip()
            new_password = input("Enter new password (leave blank to keep current): ").strip()

            if new_username == "":
                new_username = user.Username
            if new_password == "":
                new_password = user.Password

            cursor.execute("""
                UPDATE Users
                SET Username = ?, Password = ?
                WHERE Username = ?""",
                (new_username, new_password, username))
            conn.commit()
            logging.info(f"User '{username}' updated successfully.")
        else:
            logging.info("No user found with that username.")
    except Exception as e:
        logging.error(f"Error editing user: {e}")
    finally:
        conn.close()


def add_item():
    try:
        item_id = int(input("Enter item ID: ").strip())
        item_name = input("Enter item name: ").strip()
        item_price = float(input("Enter item price: ").strip())
        conn = create_connection()
        if conn is None:
            return
        cursor = conn.cursor()
        cursor.execute("INSERT INTO Items (ItemID, Name, Price) VALUES (?, ?, ?)", (item_id, item_name, item_price))
        conn.commit()
        logging.info(f"Item '{item_name}' added successfully with ID {item_id}.")
    except Exception as e:
        logging.error(f"Error adding item: {e}")
    finally:
        conn.close()

def delete_item():
    try:
        item_id = int(input("Enter item ID to delete: ").strip())
        conn = create_connection()
        if conn is None:
            return
        cursor = conn.cursor()
        cursor.execute("DELETE FROM Items WHERE ItemID = ?", (item_id,))
        conn.commit()
        logging.info(f"Item with ID {item_id} deleted successfully.")
    except Exception as e:
        logging.error(f"Error deleting item: {e}")
    finally:
        conn.close()

def record_transaction(item_id, quantity):
    try:
        conn = create_connection()
        if conn is None:
            return
        cursor = conn.cursor()
        cursor.execute("INSERT INTO Transactions (ItemID, Quantity) VALUES (?, ?)", (item_id, quantity))
        conn.commit()
        logging.info(f"Recorded transaction for Item ID {item_id} with Quantity {quantity}.")
    except Exception as e:
        logging.error(f"Error recording transaction: {e}")
    finally:
        conn.close()

def security_alert():
    """Display a security alert message to deter unauthorized access."""
    logging.info("\n[SECURITY ALERT]")
    logging.info("WARNING: Unauthorized access detected!")
    logging.info("Our security system has detected multiple failed login attempts.")
    logging.info("The authorities have been notified, and your IP address has been logged.")
    logging.info("Further attempts to breach this system may result in legal action.")
    logging.info("You are being monitored. Cease all unauthorized activities immediately.")
    logging.info("Do not attempt to access this system again.")
    logging.info("Lockout period will be enforced. Thank you for your cooperation.")

def simulate_authority_conversation():
    """Simulate a realistic text-based conversation with a fictional authority representative."""
    conversation = [
        "Cybersecurity Response Unit: Hello, this is the Cybersecurity Response Unit. We have detected unauthorized access attempts from your IP address.",
        "User: [Type your response here]",
        "Cybersecurity Response Unit: Our monitoring systems have recorded several failed login attempts. Can you please explain what you are doing?",
        "User: [Type your response here]",
        "Cybersecurity Response Unit: It is important that you cease all unauthorized activities immediately. Further attempts could result in legal consequences.",
        "Cybersecurity Response Unit: For verification, please provide your credentials or any information that can prove your authorization to access this system.",
        "User: [Type your response here]",
        "Cybersecurity Response Unit: We are reviewing your credentials. Please hold on while we verify the information.",
        "Cybersecurity Response Unit: Unauthorized access is a serious matter. Our systems will log your IP address and report this incident to relevant authorities.",
        "User: [Type your response here]",
        "Cybersecurity Response Unit: Please note that continued unauthorized access attempts may lead to a formal complaint to Canadian Centre for Cyber Security and potential legal action.",
        "User: [Type your response here]",
        "Cybersecurity Response Unit: If you believe this is an error, please contact our concierge team immediately."
    ]

    for line in conversation:
        time.sleep(4)
        if not "User: [Type your response here]" in line:
                 time.sleep(2)
                 logging.info(line)
          # Simulate time between messages for realism

        # Simulate user input
        elif "User: [Type your response here]" in line:
            user_input = input("You: ").strip()
            if user_input.lower() in ['exit', 'quit', 'close']:
                logging.info("Cybersecurity Response Unit: Exiting the conversation. Please cease all unauthorized activities.")
                break
def admin_login():
    """Handle admin login with a grace period for lockout, displaying a warning before the final lockout."""
    while True:
        try:
            username = input("Enter admin username: ").strip()
            if username == "master":
                 logging.info("Username not found.")
                 continue
            password = getpass.getpass("Enter admin password: ").strip()

            conn = create_connection()
            if conn is None:
                return False, None

            cursor = conn.cursor()
            cursor.execute("SELECT Password, FailedAttempts, LockoutTime, Role FROM Users WHERE Username = ?", (username,))
            user = cursor.fetchone()

            if not user:
                logging.info("Username not found.")
                continue

            db_password, failed_attempts, lockout_time, role = user

            # Check if the user is currently locked out
            if lockout_time and lockout_time > datetime.now():
                logging.info(f"Account is locked until {lockout_time}. Please try again later.")
                continue

            # Validate the entered password
            if password == db_password:
                logging.info("Login successful!")
                # Reset failed attempts and lockout time
                cursor.execute("UPDATE Users SET FailedAttempts = 0, LockoutTime = NULL WHERE Username = ?", (username,))
                conn.commit()
                return True, role, False  # Return role and reauthentication status
            else:
                failed_attempts += 1
                logging.info(f"Invalid credentials. Attempt {failed_attempts}/{LOCKOUT_THRESHOLD}.")

                # Display a warning message after the second failed attempt
                if failed_attempts == LOCKOUT_THRESHOLD - 1:
                    logging.info("Warning: One more failed attempt will lock you out.")

                # Lock out the user after exceeding the threshold
                if failed_attempts >= LOCKOUT_THRESHOLD:
                    lockout_time = datetime.now() + timedelta(minutes=LOCKOUT_DURATION)
                    cursor.execute("UPDATE Users SET FailedAttempts = ?, LockoutTime = ? WHERE Username = ?", (failed_attempts, lockout_time, username))
                    conn.commit()
                    logging.info("Maximum login attempts exceeded. Account locked.")
                    unlockpassword = input("Please call the manager to come over. Would you like to unlock this account? (Y/N) ")
                    if unlockpassword.upper()=="Y":
                        check=input("Please enter the master password: ")
                        cursor.execute("SELECT Password FROM Users WHERE Username = ?", ('master'))
                        masterpwd_tuple = cursor.fetchone()
                        masterpwd=masterpwd_tuple[0]
                        if masterpwd == check:
                            cursor.execute("UPDATE Users SET FailedAttempts = 0, LockoutTime = NULL WHERE Username = ?", (username))
                            conn.commit()
                            logging.info("Account unlocked successfully!")
                            return False, role, True  # Return role and reauthentication status
                        else:
                            simulate_authority_conversation()
                    else:
                        simulate_authority_conversation()
                    return False, None
                else:
                    cursor.execute("UPDATE Users SET FailedAttempts = ? WHERE Username = ?", (failed_attempts, username))
                    conn.commit()

        except Exception as e:
            logging.error(f"Error during login: {e}")
            return False, None
        finally:
            conn.close()

def add_user():
    try:
        new_username = input("Enter new username: ").strip()
        new_password = input("Enter new password: ").strip()
        while True:
            role = input("Enter the role (a)dmin/(s)taff/(m)anager: ").strip().lower()
            if role == 'a':
                role = 'admin'
                break
            elif role == 's':
                role = 'staff'
                break
            elif role == 'm':
                role = 'manager'
                break
            else:
                role = ''
                logging.info("Invalid role. Please try again.")
        conn = create_connection()
        if conn is None:
            return
        cursor = conn.cursor()
        cursor.execute("IF NOT EXISTS (SELECT * FROM Users WHERE Username = ?) INSERT INTO Users (Username, Password, Role) VALUES (?, ?, ?)", (new_username, new_username, new_password, role))
        conn.commit()
        logging.info(f"User '{new_username}' added successfully.")
    except Exception as e:
        logging.error(f"Error adding user: {e}")
    finally:
        conn.close()

def delete_user():
    try:
        del_username = input("Enter username to delete: ").strip()
        conn = create_connection()
        if conn is None:
            return
        cursor = conn.cursor()
        cursor.execute("DELETE FROM Users WHERE Username = ?", (del_username,))
        conn.commit()
        logging.info(f"User '{del_username}' deleted successfully.")
    except Exception as e:
        logging.error(f"Error deleting user: {e}")
    finally:
        conn.close()

def get_dynamic_price(item_id):
    try:
        conn = create_connection()
        if conn is None:
            return None
        cursor = conn.cursor()
        cursor.execute("SELECT Price, PricingRule FROM Items WHERE ItemID = ?", (item_id,))
        result = cursor.fetchone()

        if result:
            base_price, pricing_rule = result
            base_price = float(base_price)  # Convert Decimal to float
            if pricing_rule == 'Peak':
                return base_price * 1.20
            elif pricing_rule == 'OffPeak':
                return base_price * 0.90
            else:
                return base_price
        else:
            logging.info("Item not found.")
            return None
    except Exception as e:
        logging.error(f"Error retrieving dynamic price: {e}")
        return None
    finally:
        conn.close()

def get_item_choice():
    while True:
        try:
            display_items()
            choice = int(input("Which service/item do you want? "))
            price = get_dynamic_price(choice)
            if price is not None:
                return choice, price
            else:
                logging.info("Invalid choice. Please try again.")
        except ValueError:
            logging.info("Invalid input. Please enter a number.")
        except Exception as e:
            logging.error(f"Error getting item choice: {e}")

def view_reservations():
    """Display all reservations including the floor."""
    conn = create_connection()
    if conn is None:
        return
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT RoomNumber, Floor, LastName, FirstName FROM Reservations")
        rows = cursor.fetchall()
        logging.info("Reservations")
        for row in rows:
            logging.info(f"Room Number: {row.RoomNumber}, Floor: {row.Floor}, Last Name: {row.LastName}, First Name: {row.FirstName}")
    except Exception as e:
        logging.error(f"Error displaying reservations: {e}")
    finally:
        conn.close()

def update_item():
    try:
        item_id = int(input("Enter the item ID to update: ").strip())
        new_name = input("Enter the new item name: ").strip()
        new_price = float(input("Enter the new item price: ").strip())

        conn = create_connection()
        if conn is None:
            return

        cursor = conn.cursor()
        cursor.execute("UPDATE Items SET Name = ?, Price = ? WHERE ItemID = ?", (new_name, new_price, item_id))
        conn.commit()
        logging.info(f"Item with ID {item_id} updated successfully.")
    except Exception as e:
        logging.error(f"Error updating item: {e}")
    finally:
        conn.close()

def search_reservations():
    try:
        conn = create_connection()
        if conn is None:
            return
        search_type = input("Search by room number (RN)/last name(LN): ").strip().lower()
        cursor = conn.cursor()
        if search_type == 'rn':
            search_value = input(f"Enter the room number: ").strip()
            cursor.execute("SELECT * FROM Reservations WHERE RoomNumber = ?", (search_value,))
        elif search_type == 'ln':
            search_value = input(f"Enter the last name: ").strip()
            cursor.execute("SELECT * FROM Reservations WHERE LastName = ?", (search_value,))
        else:
            logging.info("Invalid search type.")
            return

        reservations = cursor.fetchall()
        if reservations:
            logging.info("Search Results:")
            for reservation in reservations:
                logging.info(f"Room Number: {reservation.RoomNumber}, Last Name: {reservation.LastName}, First Name: {reservation.FirstName}")
        else:
            logging.info("No reservations found.")
    except Exception as e:
        logging.error(f"Error searching reservations: {e}")
    finally:
        conn.close()

def view_users():
    try:
        
        conn = create_connection()
        cursor = conn.cursor()
        if conn is None:
            return
        passwords = input("Would you like to see the passwords? (Y/N): ").strip().upper()
        if passwords == 'Y':
            mpwd= getpass.getpass("Please enter the master password: ").strip()
            conn = create_connection()
            if conn is None:
                logging.info("Database connection failed.")
                return
            cursor.execute("SELECT Password FROM Users WHERE Username = ?", ('master'))
            rows = cursor.fetchone()
            if mpwd == rows[0]:
                logging.info("Master password is correct. Displaying passwords.")
                cursor = conn.cursor()
                cursor.execute("SELECT Username, Password, Role FROM Users")
                rows = cursor.fetchall()
                logging.info("Users and Roles")
                for row in rows:
                    if row.Username.lower() == 'master':
                        logging.info("An account was skipped for security reasons.")
                        continue
                    logging.info(f"Username: {row.Username}, Password: {row.Password}, Role: {row.Role}")
                return
            else:
                logging.info("Incorrect master password. Cannot display passwords.")
        
        cursor = conn.cursor()
        cursor.execute("SELECT Username, Password, Role FROM Users")
        rows = cursor.fetchall()
        logging.info("Users and Roles")
        for row in rows:
            if row.Username.lower() == 'master':
                logging.info("An account was skipped for security reasons.")
                continue
            logging.info(f"Username: {row.Username}, Role: {row.Role}")

    except Exception as e:
        logging.error(f"Error displaying users: {e}")
    finally:
        conn.close()

def apply_discount(total_amount):
    try:
        discount_code = input("Enter discount code: ").strip()

        conn = create_connection()
        if conn is None:
            return

        cursor = conn.cursor()
        cursor.execute("SELECT DiscountPercentage FROM Discounts WHERE Code = ?", (discount_code,))
        result = cursor.fetchone()

        if result:
            discount_percentage = result[0]
            discount_amount = (total_amount * float(discount_percentage)) / 100
            total_with_discount = total_amount - discount_amount
            logging.info(f"Discount applied! New total amount: ${total_with_discount:.2f}")
            return total_with_discount
        else:
            logging.info("Invalid discount code.")
            return total_amount
    except Exception as e:
        logging.error(f"Error applying discount: {e}")
    finally:
        conn.close()

def view_items():
    """Display all items."""
    conn = create_connection()
    if conn is None:
        return
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT ItemID, Name, Price, PricingRule FROM Items")
        rows = cursor.fetchall()
        logging.info("Items")
        for row in rows:
            logging.info(f"Item ID: {row.ItemID}, Name: {row.Name}, Price: ${row.Price:.2f}, Pricing Rule: {row.PricingRule}")
    except Exception as e:
        logging.error(f"Error displaying items: {e}")
    finally:
        conn.close()

def admin_panel():
    login_successful, role, reauth = admin_login()

    if not login_successful and not reauth:
        logging.info("Unauthorized access. Returning to main menu.")
        return
    elif reauth:
        logging.info("Reauthentication required. Please log in again.")
        admin_panel()
    role = str(role).lower()
    while True:
        logging.info("\nAdmin Panel")

        if role == 'staff':
            logging.info("---- Reservations ----")
            logging.info("1. Add Reservation")
            logging.info("2. View Reservations")
            logging.info("3. Edit Reservation")
            logging.info("4. Delete Reservation")
            logging.info("5. Search Reservations")
            logging.info("6. Exit Admin Panel")

        elif role == 'manager':
            logging.info("---- Reservations ----")
            logging.info("1. Add Reservation")
            logging.info("2. Delete Reservation")
            logging.info("3. Edit Reservation")
            logging.info("4. View Reservations")
            logging.info("5. Search Reservations")

            logging.info("---- Items ----")
            logging.info("6. Add Item")
            logging.info("7. Delete Item")
            logging.info("8. Update Item")
            logging.info("9. View Items")

            logging.info("---- Users ----")
            logging.info("10. View Users")  # Managers can view users

            logging.info("---- Discounts ----")
            logging.info("11. View Discount Codes")

            logging.info("---- Other ----")
            logging.info("12. Exit Admin Panel")

        elif role == 'admin':
            logging.info("---- Reservations ----")
            logging.info("1. Add Reservation")
            logging.info("2. Delete Reservation")
            logging.info("3. Edit Reservation")
            logging.info("4. View Reservations")
            logging.info("5. Search Reservations")

            logging.info("---- Items ----")
            logging.info("6. Add Item")
            logging.info("7. Delete Item")
            logging.info("8. Update Item")
            logging.info("9. View Items")

            logging.info("---- Users ----")
            logging.info("10. Add User")
            logging.info("11. Delete User")
            logging.info("12. Edit User")
            logging.info("13. View Users")
            logging.info("14. Reset User Password")

            logging.info("---- Discounts ----")
            logging.info("15. Manage Discount Codes")

            logging.info("---- Other ----")
            logging.info("16. Exit Admin Panel")
        else:
            logging.error("A role has not been assigned. Please contact the system administrator.")
            break
        choice = input("Enter your choice: ").strip()

        if role == 'staff':
            if choice == '1':
                add_reservation()
            elif choice == '2':
                view_reservations()
            elif choice == '3':
                edit_reservation()
            elif choice == '4':
                delete_reservation()
            elif choice == '5':
                search_reservations()
            elif choice == '6':
                break
            else:
                logging.info("Invalid choice. Please try again.")

        elif role == 'manager':
            if choice == '1':
                add_reservation()
            elif choice == '2':
                delete_reservation()
            elif choice == '3':
                edit_reservation()
            elif choice == '4':
                view_reservations()
            elif choice == '5':
                search_reservations()
            elif choice == '6':
                add_item()
            elif choice == '7':
                delete_item()
            elif choice == '8':
                update_item()
            elif choice == '9':
                view_items()
            elif choice == '10':
                view_users()
            elif choice == '11':
                try:
                    conn = create_connection()
                    if conn is None:
                        logging.info("Database connection failed.")
                        continue
                    cursor = conn.cursor()
                    cursor.execute("SELECT Code, DiscountPercentage FROM Discounts")
                    discounts = cursor.fetchall()
                    if discounts:
                        logging.info("Current Discount Codes:")
                        for discount in discounts:
                            logging.info(f"Code: {discount.Code}, Percentage: {discount.DiscountPercentage}%")
                    else:
                        logging.info("No discount codes found.")
                    
                except Exception as e:
                    logging.error(f"Error viewing discount codes: {e}")
                finally:
                    conn.close()
            elif choice == '12':
                break
            else:
                logging.info("Invalid choice. Please try again.")

        elif role == 'admin':
            if choice == '1':
                add_reservation()
            elif choice == '2':
                delete_reservation()
            elif choice == '3':
                edit_reservation()
            elif choice == '4':
                view_reservations()
            elif choice == '5':
                search_reservations()
            elif choice == '6':
                add_item()
            elif choice == '7':
                delete_item()
            elif choice == '8':
                update_item()
            elif choice == '9':
                view_items()
            elif choice == '10':
                add_user()
            elif choice == '11':
                delete_user()
            elif choice == '12':
                edit_user()
            elif choice == '13':
                view_users()
            elif choice == '14':
                reset_user_password()
            elif choice == '15':
                manage_discount_codes()
            elif choice == '16':
                break
            else:
                logging.info("Invalid choice. Please try again.")
        os.system('pause')
def manage_discount_codes():
    """Provides a sub-menu for discount code management."""
    conn = create_connection()
    if conn is None:
        logging.info("Database connection failed.")
        return
    try:
        cursor = conn.cursor()
        while True:
            logging.info("\nDiscount Code Management:")
            logging.info("1. Add Discount Code")
            logging.info("2. Update Discount Code")
            logging.info("3. Delete Discount Code")
            logging.info("4. View Discount Codes")
            logging.info("5. Exit Discount Management")
            choice = input("Enter your choice: ").strip()
            if choice == "1":
                cursor.execute("SELECT Code FROM Discounts")
                last_code = cursor.fetchall()
                logging.info(f"Last discount code: {(last_code[-1])[0] if last_code else 'None'}")
                code = input("Enter new discount code: ").strip()
                try:
                    discount_percentage = float(input("Enter discount percentage: ").strip())
                except ValueError:
                    logging.info("Invalid discount percentage.")
                    continue
                cursor.execute(
                    "INSERT INTO Discounts (Code, DiscountPercentage) VALUES (?, ?)",
                    (code, discount_percentage)
                )
                conn.commit()
                logging.info(f"Discount code '{code}' added successfully.")
            elif choice == "2":
                cursor.execute("SELECT Code, DiscountPercentage FROM Discounts")
                discounts = cursor.fetchall()
                if discounts:
                    logging.info("Current Discount Codes:")
                    for discount in discounts:
                        logging.info(f"Code: {discount.Code}, Percentage: {discount.DiscountPercentage}%")
                else:
                    logging.info("No discount codes found.")
                code = input("Enter discount code to update: ").strip()
                cursor.execute("SELECT * FROM Discounts WHERE Code = ?", (code,))
                if cursor.fetchone():
                    try:
                        new_percentage = float(input("Enter new discount percentage: ").strip())
                    except ValueError:
                        logging.info("Invalid percentage.")
                        continue
                    cursor.execute(
                        "UPDATE Discounts SET DiscountPercentage = ? WHERE Code = ?",
                        (new_percentage, code)
                    )
                    conn.commit()
                    logging.info(f"Discount code '{code}' updated successfully.")
                else:
                    logging.info("Discount code not found.")
            elif choice == "3":
                cursor.execute("SELECT Code, DiscountPercentage FROM Discounts")
                discounts = cursor.fetchall()
                if discounts:
                    logging.info("Current Discount Codes:")
                    for discount in discounts:
                        logging.info(f"Code: {discount.Code}, Percentage: {discount.DiscountPercentage}%")
                else:
                    logging.info("No discount codes found.")
                code = input("Enter discount code to delete: ").strip()
                cursor.execute("DELETE FROM Discounts WHERE Code = ?", (code,))
                conn.commit()
                logging.info(f"Discount code '{code}' deleted successfully.")
            elif choice == "4":
                cursor.execute("SELECT Code, DiscountPercentage FROM Discounts")
                discounts = cursor.fetchall()
                if discounts:
                    logging.info("Current Discount Codes:")
                    for discount in discounts:
                        logging.info(f"Code: {discount.Code}, Percentage: {discount.DiscountPercentage}%")
                else:
                    logging.info("No discount codes found.")
            elif choice == "5":
                break
            else:
                logging.info("Invalid choice. Please try again.")
    except Exception as e:
        logging.error(f"Error managing discount codes: {e}")
    finally:
        conn.close()
def reset_user_password():
    logging.info("List of Users:")
    view_users()
    """Allow an admin to reset a user's password."""
    conn = create_connection()
    if conn is None:
        logging.info("Database connection failed.")
        return
    try:
        cursor = conn.cursor()
        username = input("Enter the username to reset password: ").strip()
        cursor.execute("SELECT Username FROM Users WHERE Username = ?", (username,))
        if cursor.fetchone():
            new_password = input("Enter new password: ").strip()
            cursor.execute("UPDATE Users SET Password = ? WHERE Username = ?", (new_password, username))
            conn.commit()
            logging.info(f"Password for user '{username}' has been reset successfully.")
        else:
            logging.info("User not found.")
    except Exception as e:
        logging.error(f"Error resetting user password: {e}")
    finally:
        conn.close()

def luhn_check(card_number):
    """Validate credit card number using Luhn's algorithm."""
    def digits_of(n):
        return [int(d) for d in str(n)]

    digits = digits_of(card_number)
    odd_digits = digits[-1::-2]
    even_digits = digits[-2::-2]

    checksum = sum(odd_digits)

    for d in even_digits:
        checksum += sum(digits_of(d * 2))

    return checksum % 10 == 0

def process_credit_card(total_amount):
    """Simulate credit card processing with tax."""
    total_amount = float(total_amount)
    # Calculate the tax amount
    tax_amount = total_amount * TAX_RATE
    total_with_tax = total_amount + tax_amount

    logging.info(f"Processing credit card payment of ${total_with_tax:.2f}...")

    # Get credit card details
    card_number = input("Enter your credit card number: ")

    # Validate credit card number using Luhn's algorithm
    if not luhn_check(card_number) or card_number == "":
        logging.info("Invalid credit card number. Payment Cancelled.")
        return False

    expiration_date = input("Enter your credit card expiration date (MM/YYYY): ")

    # Validate expiration date
    if not validate_expiration_date(expiration_date):
        logging.info("Invalid or expired credit card expiration date. Payment Cancelled.")
        return False

    cvv = input("Enter your credit card CVV: ")

    # Validate CVV length
    if len(cvv) != 3:
        logging.info("Invalid CVV. Payment Cancelled.")
        return False
    return True

def validate_expiration_date(expiration_date):
    """Validate if the credit card expiration date is valid and not expired."""
    try:
        # Parse expiration date
        exp_month, exp_year = expiration_date.split('/')
        exp_month = int(exp_month)
        exp_year = int(exp_year)

        # Get current date
        current_date = datetime.now()
        current_year = current_date.year
        current_month = current_date.month

        # Check if the expiration date is in the future
        if (exp_year > current_year or (exp_year == current_year and exp_month >= current_month)) and exp_month <= 12:
            return True
        else:
            return False
    except (ValueError, IndexError):
        # Return False if the date format is invalid
        return False
    


def check_in():
    """Handle customer check-in using validate_room and display amenities."""
    room_number, first_name = validate_room()  # Assume validate_room returns (room_number, first_name)
    if room_number and first_name:
        logging.info("Checking in...")
        time.sleep(2)
        logging.info("Verifying Identity...")
        time.sleep(2)
        logging.info("Finalizing check-in...")
        time.sleep(1)
        logging.info("Room number and key card are being prepared...")
        time.sleep(2)
        logging.info(f"Your room number is {room_number}.")
        logging.info("Your key card is ready for use.")
        logging.info(f"Check-in successful! Welcome to {HOTEL_NAME}, {first_name.capitalize()}!")
        logging.info("Please enjoy your stay!")
        logging.info(f"If you need assistance, please call the front desk at {room_number}-56.\n")
        logging.info("Amenities:")
        logging.info("- Complimentary high-speed Wi‑Fi throughout the premises")
        logging.info("- Fully equipped fitness center")
        logging.info("- Sparkling swimming pool")
        logging.info("- 24/7 room service")
        logging.info("- Gourmet restaurant")
        logging.info("- Business center with meeting rooms")
        logging.info("- 24-hour front desk assistance")
        logging.info("- Complimentary breakfast for premium guests")
    else:
        logging.info("Check-in failed. Contacting the front desk for assistance.")
        logging.info("Please take your ID and credit card with you.")
        logging.info("Error:  0x0201 Invalid room number or last name.")
        logging.info("Please wait while we redirect you to the front desk.")
        logging.info("Redirecting...")
        time.sleep(2)  # Simulate a delay for redirection
        logging.info("You have been redirected to the front desk.")
        logging.info("Please provide your ID and credit card for verification.")
        id = input("Please enter your ID: ").strip()
        credit_card = input("Please enter your credit card number: ").strip()
        logging.info(f"ID: {id}, Credit Card: {credit_card}")
        logging.info("Verifying ID and credit card...")
        time.sleep(2)  # Simulate a delay for verification
        logging.info("Thank you for your patience.")
        logging.info("Your room number is being verified.")
        logging.info("Please wait...")
        time.sleep(2)  # Simulate a delay for verification
        logging.info("Verification unsuccessful!")
        logging.info("You reservation is not in our system. Possible fraud and/or spam detected. Please ask the front desk for assistance.")
        check=input("Please enter the master password: ")
        try:
            conn = create_connection()
            cursor=conn.cursor()
            cursor.execute("SELECT Password FROM Users WHERE Username = ?", ('master'))
            masterpwd_tuple = cursor.fetchone()
            masterpwd=masterpwd_tuple[0]
            if masterpwd == check:
                logging.info("Account unlocked successfully!")
                logging.info("Please try again.")
                cutomer_panel()
        except Exception as e:
            logging.error(f"Error during check-in: {e}")
        finally:
            conn.close()
def billing_creator():
    logging.info("\n--- Billing Creator ---")
    logging.info("Enter your charges. Type 'done' for description to finish.")
    items = []
    total = 0.0
    while True:
        description = input("Enter charge description (or 'done' to finish): ").strip()
        if description.lower() == 'done' or description == '':
            break
        try:
            amount = float(input("Enter amount for this charge: ").strip())
        except ValueError:
            logging.info("Invalid amount. Please try again.")
            continue
        items.append((description, amount))
        total += amount
    receipt = "\n----- Receipt -----\n"
    for desc, amt in items:
        receipt += f"{desc}: ${amt:.2f}\n"
    receipt += f"Subtotal: ${total:.2f}\n"
    tax = total * TAX_RATE
    final_total = total + tax
    receipt += f"Tax (Tax Rate: {TAX_RATE*100:.0f}%): ${tax:.2f}\n"
    receipt += f"Total Amount: ${final_total:.2f}\n"
    receipt += "-------------------\n"
    logging.info(receipt)
def check_out():
    """Handle customer check-out without deleting the reservation."""
    try:
        last_name = input("Please enter your last name: ").strip()
        room_number = input("Please enter your room number (floor + 3-digit code): ").strip()
        conn = create_connection()
        if conn is None:
            return
        cursor = conn.cursor()
        cursor.execute("SELECT RoomNumber, FirstName FROM Reservations WHERE LastName = ?", (last_name,))
        reservations = cursor.fetchall()
        matched = False
        first_name = ""
        if reservations:
            for reservation in reservations:
                if reservation.RoomNumber == room_number:
                    matched = True
                    first_name = reservation.FirstName
                    break
        if matched:
            logging.info(f"Check-out successful for room {room_number}. Thanks for visting {HOTEL_NAME}, {first_name.capitalize()}! We hope to see you again soon!")
            bill_choice = input("Would you like to generate your bill? (Y/N): ").strip().lower()
            if bill_choice == 'y':
                billing_creator()
        else:
            logging.info("No matching reservation found for check-out.")
    except Exception as e:
        logging.error(f"Error during check-out: {e}")
    finally:
        conn.close()
def order_item():
    logging.info("Welcome to the ordering system!")
# Existing ordering code starts here
    total = 0.0  # Initialize total as a float
    redemption_codes = []

    room_number, first_name = validate_room()
    if room_number is None or first_name is None:
        logging.info("Invalid room number or last name. Please try again.")
        return  # Return to main menu if validation fails

    logging.info(f"Welcome, {first_name.capitalize()}! Room {room_number} validated successfully.")

    while True:
        item_choice = get_item_choice()
        if item_choice is None:
            continue  # Return to item choice if error occurs

        quantity = get_quantity()
        conn = create_connection()
        if conn is None:
            logging.info("Connection failed. Returning to main menu.")
            return

        try:
            item_id_str, price = item_choice
            logging.debug(f"Item Choice: {item_choice}")
            item_id = int(item_id_str)  # Convert item ID to integer

           
            price = get_dynamic_price(item_id)

            if price:
                if isinstance(price, Decimal):
                    price = float(price)
                total += price * quantity
                code = generate_code()
                redemption_codes.append((item_id, code))
                logging.info(f"Total so far: ${total:.2f}")
                logging.info(f"Redemption code for item {item_id}: {code}")
            else:
                logging.info("Item not found. Please try again.")
        except Exception as e:
            logging.error(f"Error during item processing: {e}")
        finally:
            conn.close()

        if not get_another_item():
            break  # Exit the item ordering loop
    discount = input("Do you have a discount code? (Y/N): ").strip().lower()
    if discount == 'y':
        total = apply_discount(total)  # Apply discount if applicable
    logging.info("End of transaction")
    logging.info(f"Your total is ${total:.2f} and will be delivered to room {room_number}")
    logging.info("Your redemption codes are:")
    for item, code in redemption_codes:
        logging.info(f"Item ID {item}: {code}")
    while True:
        if process_credit_card(total):
            logging.info("Thank you for your order!")
            logging.info("Your order will be delivered shortly.")
            break
        else:
            logging.info("Payment failed. Please try again.")
def view_amenities():
    """Display a full list of hotel amenities for customers."""
    logging.info("\nHotel Amenities:")
    logging.info("- Complimentary high‑speed Wi‑Fi throughout the premises")
    logging.info("- Fully equipped fitness center")
    logging.info("- Sparkling swimming pool")
    logging.info("- 24/7 room service")
    logging.info("- Gourmet restaurant")
    logging.info("- Business center with logging.infoing and meeting rooms")
    logging.info("- 24-hour front desk assistance")
    logging.info("- Complimentary breakfast for premium guests")

def provide_feedback():
    """Allow customers to provide feedback about their stay."""
    logging.info("\nWe value your feedback!")
    try:
        rating = input("Please rate our service on a scale of 1-5: ").strip()
        if not rating.isdigit() or int(rating) not in [1, 2, 3, 4, 5]:
            logging.info("Invalid rating. Please enter a number between 1 and 5.")
            return
        comment = input("Please provide any additional comments: ").strip()
        logging.info("Thank you for your feedback!")
        logging.info(f"Rating: {rating}, Comments: {comment}")
    except Exception as e:
        logging.error(f"Error capturing feedback: {e}")
def view_promotions():
    """Display current hotel promotions and discount offers."""
    logging.info("\nCurrent Promotions:")
    logging.info("- Enjoy 15% off on all room service orders above $50!")
    logging.info("- Summer Special: Book a spa session and get a free fitness class!")
    logging.info("- Loyalty Bonus: Earn extra points for every dine-in meal!")

def track_order_status():
    """Simulate tracking an order's status."""
    logging.info("\nTrack Order Status")
    order_id = input("Enter your order ID: ").strip()
    logging.info(f"Checking status for Order ID {order_id}...")
    time.sleep(3)
    delivery_array=["Preparing", "Ready for pickup", "Out for delivery", "Delivered", "Cancelled", 
         "Awaiting confirmation", "In transit", "Failed delivery", "Completed"]
    delivery_status = random.choice(delivery_array)  # Randomly select a status from the list
    status= delivery_status  # Get the first element from the list
    logging.info(f"Order ID {order_id} status: {status}")
    if status == "Preparing":
        logging.info("Your order is currently being prepared. Please wait patiently.")
    elif status == "Ready for pickup":
        logging.info("Your order is ready for pickup. Please collect it at your convenience.")
    elif status == "Out for delivery":
        delivery_time = random.randint(5, 15)
        logging.info(f"Your order is out for delivery! Expected delivery time: {delivery_time} minutes.")
    elif status == "Delivered":
        logging.info("Your order has been delivered. Enjoy your meal!")
    elif status == "Cancelled":
        logging.info("Your order has been cancelled. Please contact concierge for further assistance.")
    elif status == "Awaiting confirmation":
        logging.info("Your order is awaiting confirmation. Please check back later.")
    elif status == "In transit":
        logging.info("Your order is in transit. It will arrive soon.")
    elif status == "Failed delivery":
        logging.info("Delivery attempt failed. Please contact concierge to reschedule.")
    elif status == "Completed":
        logging.info("Your order has been successfully completed. Thank you!")
    delivery_status = ""

def contact_concierge():
    """Simulate contacting the concierge for assistance."""
    logging.info("\nContact Concierge")
    message = input("Enter your message for our concierge: ").strip()
    logging.info("Sending your message...")
    time.sleep(2)
    logging.info("Your message has been sent. A concierge will get back to you shortly.")
    logging.info("For immediate assistance, please call the front desk at 123-456-7890.")
    logging.info("Your message: " + message)
def cutomer_panel():
    while True:
        logging.info("\nCustomer Menu:")
        logging.info("1. Check In")
        logging.info("2. Place Order")
        logging.info("3. Check Out")
        logging.info("4. View Amenities")
        logging.info("5. Provide Feedback")
        logging.info("6. View Promotions")
        logging.info("7. Join Loyalty Program")
        logging.info("8. Track Order Status")
        logging.info("9. Contact Concierge")
        logging.info("10. Exit Customer Menu")
        cust_choice = input("Enter your choice: ").strip()

        if cust_choice == '1':
            check_in()
        elif cust_choice == '2':
            order_item()
        elif cust_choice == '3':
            check_out()
        elif cust_choice == '4':
            view_amenities()
        elif cust_choice == '5':
            provide_feedback()
        elif cust_choice == '6':
            view_promotions()
        elif cust_choice == '7':
            logging.info("Loyalty Program is currently unavailable.")
        elif cust_choice == '8':
            track_order_status()
        elif cust_choice == '9':
            contact_concierge()
        elif cust_choice == '10':
            break  # Exit the customer menu and return to the main menu
        os.system('pause')
def main():
    while True:
        os.system('cls')
        logging.info(f"Welcome to {HOTEL_NAME}!")
        logging.info("Please select an option:")
        logging.info("\n1. Customer")
        logging.info("2. Admin")
        logging.info("3. Exit")
        choice = input("Enter your choice: ").strip()
        if choice == '1':
            cutomer_panel()
        elif choice == '2':
            admin_panel()
        elif choice == '3':
            logging.info("Exiting Program")
            time.sleep(2)
            sys.exit(1)
        else:
            logging.info("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()