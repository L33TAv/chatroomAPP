import socket
import threading 
import ssl
from config import CERT_FILE,HOST_NAME,PORT,HOST,BUFFER_SIZE
from tkinter import messagebox
import chat_gui

stop_thread = False
authenticated = False
client = None

def connect(login_type,username,password):
    try:
        global stop_thread
        global client
        global receive_thread

        stop_thread = False

        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_REQUIRED
        context.load_verify_locations(CERT_FILE)  # Path to the pinned certificate

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        ssl_client = context.wrap_socket(sock, server_hostname=HOST_NAME)
        ssl_client.connect((HOST, PORT))
        ssl_client.settimeout(1.0)  
        client = ssl_client 
    except (ConnectionRefusedError,TimeoutError):
        messagebox.showerror("Server Error","Server is unavailable.")
        return False
    except Exception as e:
        print(e)
        messagebox.showwarning("Invalid Input","Something went wrong, please try again.")
        return False
        
    if not auth(client,login_type,username,password):
        client.close()
        return False
    
    receive_thread = threading.Thread(target=receive,args=(client,))
    receive_thread.start()

    return True


def close_chat():
    global stop_thread
    global client
    global receive_thread

    stop_thread = True
    
    if receive_thread and receive_thread.is_alive():
        receive_thread.join(timeout=1.0)

    if client:
        try:
            client.shutdown(socket.SHUT_RDWR)
            client.close()
        except:
            pass
        finally:
            client = None




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


def receive(client):
    global stop_thread
    global authenticated 
    
    while not stop_thread and client:
        try:
            message = client.recv(BUFFER_SIZE).decode('utf-8')

            if not message: 
                print("Connection has stopped.") 
                stop_thread = True
                break

            else:
                chat_gui.message_queue.put((message,False))

        except socket.timeout:
            continue 
        except Exception as e:
            stop_thread = True
            print(f"An error occurred! - {e}")
            break
            


def write(nickname, message):
    global stop_thread,authenticated
    
    if stop_thread or not authenticated or client is None:
        return
    try:
        new_message = f"{nickname}: {message}"
        client.send(f"{nickname}: {message}".encode('utf-8'))
        chat_gui.message_queue.put((new_message, True))

    except BrokenPipeError:
        messagebox.showerror("Server Error","the connection was already closed by the server.")
        chat_gui.close_chat()
    except Exception as e:
        messagebox.showerror("Error",f"There was an error with sending the message, {e}")
        chat_gui.close_chat()

        
        
            
            

