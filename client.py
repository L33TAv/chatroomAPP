import socket
import threading 
import ssl
from config import CERT_FILE,HOST_NAME,PORT,HOST,BUFFER_SIZE

nickname = input("choose a nickname:")
'''if nickname == 'admin':
    password = input('Enter the password for admin:')'''

context = ssl.create_default_context()
context.check_hostname = False
context.verify_mode = ssl.CERT_REQUIRED
context.load_verify_locations(CERT_FILE)  # Path to the pinned certificate

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
ssl_client = context.wrap_socket(sock, server_hostname=HOST_NAME)
ssl_client.connect((HOST, PORT))

client = ssl_client  # נשתמש בזה בהמשך כרגיל

stop_thread = False
authenticated = False


def receive():
    global stop_thread
    global authenticated 
    while True:
        if stop_thread:
            break
        try:
            message = client.recv(BUFFER_SIZE).decode('utf-8')

            if not message:
                print("Connection has stopped.")
                stop_thread = True
                break

            if message == 'USERNAME':
                client.send(nickname.encode('utf-8'))

            elif message == 'PASSWORD':
                password = input("Enter your password: ")
                client.send(password.encode('utf-8'))

            elif message == 'AUTH_SUCCESS':
                print("Welcome back!")
                authenticated = True

            elif message == 'REGISTERED':
                print(f"Welcome to the chat {nickname}!")
                authenticated = True

            elif message == 'REFUSE':
                print("Username or password are incorrect. Exiting server...")
                stop_thread = True

            elif message == 'BAN':
                print("You are banned!")
                client.close()
                stop_thread = True

            else:
                print(f"{message}\n>",end="")

        except Exception as e:
            print(f"An error occurred! - {e}")
            client.close()
            break

def write():
    while True:
        if stop_thread:
            break
        if not authenticated:
            continue
        try:
            message = input("> ")
            if message.startswith("/kick ") or message.startswith("/ban "):
                client.send(message.replace("/", "").upper().encode('utf-8'))
            else:
                client.send(f"{nickname}: {message}".encode('utf-8'))
        except BrokenPipeError:
            print("the connection was already closed by the server.")
            break
        except Exception as e:
            print(f"There was an error with sending the message, {e}")
            break

if __name__ == "__main__":
    receive_thread = threading.Thread(target=receive)
    receive_thread.start()

    write_thread = threading.Thread(target=write)
    write_thread.start()