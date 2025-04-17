import socket
import signal
import sys
import random
import re
from datetime import date, datetime, timezone, timedelta
from email.utils import format_datetime
# Read a command line argument for the port where the server must run.
port = 8000
if len(sys.argv) > 1:
    port = int(sys.argv[1])
else:
    print("Using default port 8000")
hostname = socket.gethostname()
# Start a listening server socket on the port
sock = socket.socket()
sock.bind(('', port))
sock.listen(2)
### Contents of pages we will serve.
# Login form
login_form = """
   <form action = "http://%s" method = "post">
   Name: <input type = "text" name = "username">  <br/>
   Password: <input type = "text" name = "password" /> <br/>
   <input type = "submit" value = "Submit"/>
   </form>
"""
# Default: Login page.
login_page = "<h1>Please login</h1>" + login_form
# Error page for bad credentials
bad_creds_page = "<h1>Bad user/pass! Try again</h1>" + login_form
# Successful logout
logout_page = "<h1>Logged out successfully</h1>" + login_form
# A part of the page that will be displayed after successful
# login or the presentation of a valid cookie
success_page = """
   <h1>Welcome!</h1>
   <form action="http://%s" method = "post">
   <input type = "hidden" name = "action" value = "logout" />
   <input type = "submit" value = "Click here to logout" />
   </form>
   <br/><br/>
   <h1>Your secret data is here:</h1>
"""
#### Helper functions
# Printing.
def print_value(tag, value):
    print("Here is the", tag)
    print("\"\"\"")
    print(value)
    print("\"\"\"")
    print()
# Signal handler for graceful exit
def sigint_handler(sig, frame):
    print('Finishing up by closing listening socket...')
    sock.close()
    sys.exit(0)
# Register the signal handler
signal.signal(signal.SIGINT, sigint_handler)
#cookie maker
cookieDict = {}
def assignCookie(username):
    cookieValue = str(random.getrandbits(64))
    cookieDict[cookieValue] = username
    return cookieValue
# page templates 
def sucessPageCookieTemplate(username):
    submit_hostport = "%s:%d" % (hostname, port)
    html_content_to_send = success_page % submit_hostport
    expires = datetime.now(timezone.utc).replace(microsecond=0) + timedelta(days=1)
    cookie_expire = format_datetime(expires)
    headers_to_send = 'Set-Cookie: token=' + str(assignCookie(username)) +'; expires='+ cookie_expire +'\r\n'
    response  = 'HTTP/1.1 200 OK\r\n'
    response += headers_to_send
    response += 'Content-Type: text/html\r\n\r\n'
    response += html_content_to_send
    response += '<h1>%s</h1>' % secretsDict[username]
    return response
def sucessPageTemplate(username):
    submit_hostport = "%s:%d" % (hostname, port)
    html_content_to_send = success_page % submit_hostport
    headers_to_send = ''
    response  = 'HTTP/1.1 200 OK\r\n'
    response += headers_to_send
    response += 'Content-Type: text/html\r\n\r\n'
    response += html_content_to_send
    response += '<h1>%s</h1>' % secretsDict[username]
    return response
def loginPageTemplate():
    submit_hostport = "%s:%d" % (hostname, port)
    html_content_to_send = login_page % submit_hostport
    headers_to_send = ''
    response  = 'HTTP/1.1 200 OK\r\n'
    response += headers_to_send
    response += 'Content-Type: text/html\r\n\r\n'
    response += html_content_to_send
    return response 
def badCredPageTemplate():
    submit_hostport = "%s:%d" % (hostname, port)
    html_content_to_send = bad_creds_page % submit_hostport
    headers_to_send = ''
    response  = 'HTTP/1.1 200 OK\r\n'
    response += headers_to_send
    response += 'Content-Type: text/html\r\n\r\n'
    response += html_content_to_send
    return response 
def logoutPageTemplate():
    submit_hostport = "%s:%d" % (hostname, port)
    html_content_to_send = logout_page % submit_hostport
    headers_to_send = 'Set-Cookie: token=; expires=Thu, 01 Jan 1970 00:00:00 GMT\r\n'
    response  = 'HTTP/1.1 200 OK\r\n'
    response += headers_to_send
    response += 'Content-Type: text/html\r\n\r\n'
    response += html_content_to_send
    return response 
# set up 
credentialsDict = {}
secretsDict = {}
with open("passwords.txt",'r') as file:
    for line in file:
        username, password = line.strip().split(" ")
        credentialsDict[username] = password
print("Credentials")
print(credentialsDict)
# Read secret data of all the users
with open("secrets.txt",'r') as file:
    for line in file:
        username, secret = line.split(" ")
        secretsDict[username] = secret
print("Secrets")
print(secretsDict)
print('-' * 100)
# Loop to accept incoming HTTP connections and respond.
while True:
    cookie = None
    client, addr = sock.accept()
    req = client.recv(1024)
    header_body = req.decode().split('\r\n\r\n')
    headers = header_body[0]
    body = '' if len(header_body) == 1 else header_body[1]
    print_value('headers', headers)
    print_value('entity body', body)

    try: # grab username password
        username, password = re.search(r'username=([^&]*)&password=([^&]*)',body).groups()
        print("Username:" + str(username) + "\nPassword: " + str(password))
    except Exception as e:
        print("Credential Error:" + str(e))
        username = None
        password = None
    try: # grab cookie
        cookieMatch = re.search(r'Cookie: token=(.*+)',headers)
        if cookieMatch:
            cookie = str(cookieMatch.group(1).strip())
        print("Cookie: '" + cookie + "'")
    except Exception as e:
        print("Cookie Error " + str(e))
        cookie = None

    if body == 'action=logout':
        print("Logout")
        response = logoutPageTemplate()
    elif username == None and password == None and cookie == None:
        print("Base login")
        response = loginPageTemplate()
    elif username in credentialsDict.keys() and password == credentialsDict[username]:
        print("Valid credentials")
        if cookie == None or cookie in cookieDict.keys():
            response = sucessPageCookieTemplate(username)
        else:
            response = badCredPageTemplate()
            print("Bad cookie")
    elif cookie in cookieDict.keys():
        print("Found cookie")
        response = sucessPageCookieTemplate(cookieDict[cookie])
    elif cookie != None and cookie not in cookieDict.keys():
        print("Given cookie not in our db")
        response = badCredPageTemplate()
    elif (username != "" and password != "") or (username != "" or password != ""):
        print("Bad credentials")
        response = badCredPageTemplate()
    else:
        print("Base login")
        response = loginPageTemplate()

    print(cookieDict.keys())
    print("Response")
    print(response)
    client.send(response.encode())
    client.close()
    print("Served one request/connection!")
    print('-' * 100)
# We will never actually get here. Close the listening socket
sock.close()