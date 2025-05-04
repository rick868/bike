import pymysql
import bcrypt

# Database connection details
connection = pymysql.connect(
    host='localhost',
    user='root',
    password='Access+23#',
    database='voyager_db'
)

def update_password(username, new_password):
    if len(new_password) < 7:
        print("Error: Password must be at least 7 characters long.")
        return

    try:
        cursor = connection.cursor()
        # Rehash the password
        new_hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        # Update the user's password
        cursor.execute('UPDATE users SET hashed_password = %s WHERE username = %s', (new_hashed_password, username))
        connection.commit()
        print("Password updated successfully.")
    except Exception as e:
        print(f"Error updating password: {str(e)}")
    finally:
        connection.close()

# Example usage
if __name__ == "__main__":
    username = input("Enter your username: ")
    new_password = input("Enter your new password: ")
    update_password(username, new_password)
