import socket
import signal
import sys
import random
import urllib.parse

# Default server port
port = 8080
if len(sys.argv) > 1:
    port = int(sys.argv[1])
else:
    print("Using default port 8080")

hostname = socket.gethostname()

# Start a listening server socket on the port
sock = socket.socket()
sock.bind(('', port))
sock.listen(2)

# Contents of pages to be served
login_form = """
   <form action = "http://%s" method = "post">
   Name: <input type = "text" name = "username">  <br/>
   Password: <input type = "text" name = "password" /> <br/>
   <input type = "submit" value = "Submit" />
   </form>
"""
login_page = "<h1>Please login</h1>" + login_form
bad_creds_page = "<h1>Bad user/pass! Try again</h1>" + login_form
logout_page = "<h1>Logged out successfully</h1>" + login_form
success_page = """
   <h1>Welcome!</h1>
   <form action="http://%s" method = "post">
   <input type = "hidden" name = "action" value = "logout" />
   <input type = "submit" value = "Click here to logout" />
   </form>
   <br/><br/>
   <h1>Your secret data is here:</h1>
"""

# Helper functions
def print_value(tag, value):
    print(f"Here is the {tag}")
    print('"""')
    print(value)
    print('"""')
    print()

def sigint_handler(sig, frame):
    print('Finishing up by closing listening socket...')
    sock.close()
    sys.exit(0)

# Register the signal handler for graceful exit
signal.signal(signal.SIGINT, sigint_handler)

# Load user credentials and secrets
user_credentials = {}
user_secrets = {}

def load_file_data():
    try:
        with open('passwords.txt', 'r') as f:
            for line in f:
                parts = line.strip().split(' ', 1)
                if len(parts) == 2:
                    username, password = parts
                    user_credentials[username] = password
    except FileNotFoundError:
        print("Warning: passwords.txt file not found!")

    try:
        with open('secrets.txt', 'r') as f:
            for line in f:
                parts = line.strip().split(' ', 1)
                if len(parts) == 2:
                    username, secret = parts
                    user_secrets[username] = secret
    except FileNotFoundError:
        print("Warning: secrets.txt file not found!")

load_file_data()

# Store active user cookies
cookie_to_username = {}

def parse_form_data(data):
    result = {}
    if not data:
        return result
    
    pairs = data.split('&')
    for pair in pairs:
        if '=' in pair:
            key, value = pair.split('=', 1)
            key = urllib.parse.unquote_plus(key)
            value = urllib.parse.unquote_plus(value)
            result[key] = value
    return result

def extract_cookie_value(headers):
    header_lines = headers.split('\r\n')
    for line in header_lines:
        if line.startswith('Cookie:'):
            cookie_str = line[len('Cookie:'):].strip()
            cookie_pairs = cookie_str.split('; ')
            for pair in cookie_pairs:
                if pair.startswith('token='):
                    return pair[len('token='):]
    return None

# Start the server loop to accept incoming HTTP connections
while True:
    client, addr = sock.accept()
    req = client.recv(1024)

    # Parse the headers and body from the request
    header_body = req.decode().split('\r\n\r\n')
    headers = header_body[0]
    body = '' if len(header_body) == 1 else header_body[1]
    
    # Log headers and body for debugging
    print_value('headers', headers)
    print_value('entity body', body)

    form_data = parse_form_data(body)
    cookie_value = extract_cookie_value(headers)

    # Initialize response variables
    html_content_to_send = ''
    headers_to_send = ''

    # Set up the port/hostname for the form's submit URL
    submit_hostport = f"{hostname}:{port}"
    for line in headers.split('\r\n'):
        if line.startswith('Host:'):
            submit_hostport = line[len('Host:'):].strip()
            break

    # Process different actions based on the request
    if 'action' in form_data and form_data['action'] == 'logout':
        # Case E: Logout request
        headers_to_send = 'Set-Cookie: token=; expires=Thu, 01 Jan 1970 00:00:00 GMT\r\n'
        html_content_to_send = logout_page % submit_hostport
    
    elif cookie_value and cookie_value in cookie_to_username:
        # Case C: Valid cookie present
        username = cookie_to_username[cookie_value]
        secret = user_secrets.get(username, 'No secret available')
        html_content_to_send = (success_page % submit_hostport) + secret
    
    elif cookie_value and cookie_value not in cookie_to_username:
        # Case D: Invalid cookie present
        html_content_to_send = bad_creds_page % submit_hostport
    
    elif 'username' in form_data and 'password' in form_data:
        # Case A & B: Username/password authentication
        username = form_data['username']
        password = form_data['password']
        
        if username in user_credentials and user_credentials[username] == password:
            # Case A: Valid credentials
            rand_val = random.getrandbits(64)
            cookie_value = str(rand_val)
            cookie_to_username[cookie_value] = username
            headers_to_send = f'Set-Cookie: token={cookie_value}\r\n'
            secret = user_secrets.get(username, 'No secret available')
            html_content_to_send = (success_page % submit_hostport) + secret
        else:
            # Case B: Invalid credentials
            html_content_to_send = bad_creds_page % submit_hostport
    
    else:
        # Default case: Show login page
        html_content_to_send = login_page % submit_hostport

    # Construct and send the final HTTP response
    response = 'HTTP/1.1 200 OK\r\n'
    response += headers_to_send
    response += 'Content-Type: text/html\r\n\r\n'
    response += html_content_to_send
    
    # Send response to the client
    print_value('response', response)    
    client.send(response.encode())
    client.close()

    print("Served one request/connection!")
    print()

# This code will never actually be reached since we have an infinite loop.
# Close the listening socket when exiting
sock.close()
