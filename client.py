import socket
import threading 
import ssl
from config import CERT_FILE,HOST_NAME,PORT,HOST,BUFFER_SIZE
from tkinter import messagebox

stop_thread = False
authenticated = False


def connect(login_type,username,password):
    try:
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_REQUIRED
        context.load_verify_locations(CERT_FILE)  # Path to the pinned certificate

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        ssl_client = context.wrap_socket(sock, server_hostname=HOST_NAME)
        ssl_client.connect((HOST, PORT))
        client = ssl_client 
    except Exception as e:
        print(e)
        messagebox.showwarning("Invalid Input","Something went wrong, please try again.")
        return False
        
    if not auth(client,login_type,username,password):
        return False
    
    connect_thread = threading.Thread(target=receive,args=(client, username))
    connect_thread.start()

    write_thread = threading.Thread(target=write,args=(client, username))
    write_thread.start()

    return True


def auth(client,login_type,username, password):
    global authenticated

    try:
        client.send(login_type.encode('utf-8'))
        client.send(username.encode('utf-8'))
        client.send(password.encode('utf-8'))

        response = client.recv(BUFFER_SIZE).decode('utf-8')
        
        if response  == 'BAN':
            messagebox.showerror("Invalid Input","You are banned!")
            return False
        
        elif response == "EXISTS":
            messagebox.showwarning("Invalid Input",f"Username '{username}' already exists!")
            return False
        
        elif response == "NOT_EXISTS":
            messagebox.showwarning("Invalid Input",f"No Username called '{username}'")
            return False

        elif response == 'AUTH_SUCCESS':
            authenticated = True
            return True

        elif response == 'REGISTERED':
            messagebox.showwarning("Invalid Input",f"Welcome to the chat {username}!")
            authenticated = True
            return True

        elif response == 'REFUSE':
            messagebox.showwarning("Invalid Input","Username or password are incorrect.")
            return False
        
        else:
            messagebox.showerror("Failed","Something went wrong with the login, please try again.")
            return False

    except:
        messagebox.showerror("Error","Something went wrong, please try again.")
        return False


def receive(client,nickname):
    '''Config this func after auth'''
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

            else:
                print(f"{message}\n>",end="")

        except Exception as e:
            print(f"An error occurred! - {e}")
            client.close()
            break


def write(client,nickname):
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

