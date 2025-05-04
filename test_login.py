import requests

# Test login function
def test_login(username, password):
    response = requests.post("http://localhost:8501/login", json={"username": username, "password": password})
    return response.json()

# Test with valid credentials
valid_user = test_login("admin", "admin")  # Replace with actual valid credentials
print("Valid login response:", valid_user)

# Test with invalid credentials
invalid_user = test_login("invalid_user", "wrong_password")
print("Invalid login response:", invalid_user)
