import socket
import ssl
import threading
import getpass
from database import *

host = '127.0.0.1' 
port = 55555
MAX_ATTEMPTS = 3

# creating regular socket 
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((host,port))
server.listen()

clients = []
nicknames = []

create_users_table() #if already exists - doesnt create, just connects and then closes from func.
create_messages_table()

# generating SSL Context
context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)  # פרוטוקול TLS

for attempt in range(MAX_ATTEMPTS):
    try:
        password = getpass.getpass("Enter password for private key: ")
        context.load_cert_chain(certfile="cert.pem", keyfile="key.pem", password=password)  # with the password i generated with
        print("Certificate and key loaded successfully.")
        break  # יוצאים מהלולאה אם הצליח
    except ssl.SSLError as e:
        print(f"Incorrect password ({attempt + 1}/{MAX_ATTEMPTS})")
        print("Try again...\n")
else:
    print("Too many failed attempts. Exiting.")
    exit(1)


def broadcast(message,sender,nickname):
    israel_tz = pytz.timezone("Asia/Jerusalem")
    timestamp = datetime.now(israel_tz).strftime("%d.%m.%Y %H:%M")
    save_message(nickname, message.decode('utf-8'))

    message = message.decode('utf-8')
    message = timestamp + " " + message

    for client in clients:
        if client is not sender:
            print(f"sent the message:{message}")
            try:
                client.send(message.encode('utf-8'))
            except:
                # if an error comes up
                clients.remove(client)
                client.close()

def handle(client):
    while True:
        try:            
            message = client.recv(1024)
            msg = message
            name = nicknames[clients.index(client)]

            if msg.decode('utf-8').startswith('KICK'):
                if nicknames[clients.index(client)] == 'admin':
                    name_to_kick = msg.decode('utf-8')[5:]
                    print(name_to_kick)
                    kick_user(name_to_kick, client)
                    print(f'{name_to_kick} was kicked!')
                else:
                    client.send('Command was refused!'.encode('utf-8'))
            elif msg.decode('utf-8').startswith('BAN'):
                if nicknames[clients.index(client)] == 'admin':
                    name_to_ban = msg.decode('utf-8')[4:]
                    kick_user(name_to_ban, client)
                    if client in clients:
                        with open('bans.txt', 'a') as f:
                            f.write(f'{name_to_ban}\n')
                    print(f'{name_to_ban} was banned!')
                else:
                    client.send('Command was refused!'.encode('utf-8'))
            else:
                broadcast(message,client,name)
        except Exception as e:
            print(f"Server Error: {e}, {clients},{client}")
            if client in clients:
                index = clients.index(client)
                nickname  = nicknames[index]
                clients.remove(client)
                nicknames.remove(nickname)
                client.close()
                broadcast(f'{nickname} left the chat.'.encode('utf-8'),client,name)
                break
            else:
                break

def receive():
    while True:
        client_socket, address = server.accept()
        print(f"Connected with {str(address)}")

        #getting the connection with ssl
        try:
            client = context.wrap_socket(client_socket, server_side=True)
        except ssl.SSLError as e:
            print(f"SSL error: {e}")
            client_socket.close()
            continue

        # gets username
        client.send('USERNAME'.encode('utf-8'))
        username = client.recv(1024).decode('utf-8')

        # client.send('NICK'.encode('utf-8'))
        # nickname = client.recv(1024).decode('utf-8')

        with open('bans.txt','r') as f:
            bans = f.readlines() 
        if username+'\n' in bans:
            print(f"banned user {username} tried to log in")
            client.send('BAN'.encode('utf-8'))
            client.close()
            continue

        #checks for pass
        client.send('PASSWORD'.encode('utf-8'))
        password = client.recv(1024).decode('utf-8')

        #auth of the user
        auth = authenticate_user(username, password)
        if auth is True:
            client.send('AUTH_SUCCESS'.encode('utf-8'))
        elif auth is None:
            #new user
            if register_user(username,password):
                client.send('REGISTERED'.encode('utf-8'))
            else:
                client.send('REFUSE'.encode('utf-8'))
                client.close()
                continue
        else:
            client.send('REFUSE'.encode('utf-8'))
            client.close()
            continue

        # if username == 'admin':
        #     client.send('PASS'.encode('utf-8'))
        #     password = client.recv(1024).decode('utf-8')

        #     if password != 'adminpass':
        #         client.send('REFUSE'.encode('utf-8'))
        #         client.close()
        #         continue

        last_messages = get_last_messages()
        if last_messages:      
            for sender, content, timestamp in last_messages:
                try:
                    client.send(f"[{timestamp}] - {content}".encode('utf-8'))
                except:
                    pass

        nicknames.append(username)
        clients.append(client)

        print(f"nickname of the client is {username}!")
        broadcast(f'{username} has just entered the chat!'.encode('utf-8'),client,username)

        thread = threading.Thread(target=handle, args=(client,))
        thread.start()

def kick_user(name, client):
    if name in nicknames:
        name_index = nicknames.index(name)
        client_to_kick  = clients[name_index]

        client_to_kick.send('You were kicked by an admin!'.encode('utf-8'))

        clients.remove(client_to_kick)
        nicknames.remove(name)       
        client_to_kick.close()

        broadcast(f'{name} was kicked'.encode('utf-8'),client,name)
    else:
        print("{name} doesnt exits.")
        client.send(f'{name} doesnt exists!'.encode('utf-8'))


print("server is running...")
receive()