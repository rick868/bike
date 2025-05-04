import mysql.connector

# Database connection details
db_config = {
    'user': 'root',
    'password': 'Access+23#',
    'host': 'localhost',
    'database': 'voyager_db',
    'auth_plugin': 'mysql_native_password'  # Explicitly set the authentication plugin

}

# Read SQL commands from the file
with open('voyager.session.sql', 'r') as file:
    sql_commands = file.read()

# Connect to the database and execute the commands
cursor = None  # Initialize cursor variable
try:
    connection = mysql.connector.connect(**db_config)
    if connection.is_connected():
        cursor = connection.cursor()  # Ensure cursor is defined
        for command in sql_commands.split(';'):
            if command.strip():  # Avoid executing empty commands
                cursor.execute(command)  # Execute each command

        connection.commit()
        print("SQL commands executed successfully.")
    else:
        print("Failed to connect to the database.")
except mysql.connector.Error as err:
    print(f"Error: {err}")
finally:
    if cursor is not None:  # Close cursor if it was created
        cursor.close()
    if 'connection' in locals():  # Close connection if it was established
        connection.close()
