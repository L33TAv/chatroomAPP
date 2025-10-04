import logging
import socket
import ssl
import pytz
import threading
import getpass
from datetime import datetime

import database.database as database 
from config.config import HOST,PORT,MAX_ATTEMPTS,CERT_FILE,KEY_FILE,BUFFER_SIZE,TIMEZONE,BANS_FILE, TIME_FORMAT, LAST_MESSAGES_SENT

logging.basicConfig(level=logging.INFO,format="%(asctime)s [%(levelname)s] %(message)s")

class ServerChat():
    def __init__(self):
        self.clients = {}  # client:nickname
    
        #Time zone
        self.tz = pytz.timezone(TIMEZONE)

        # DB connection
        database.create_users_table()
        database.create_messages_table()

        # Create Socket
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((HOST,PORT))
        self.server.listen()

        #Wrapping the Socket with SSL  
        self.context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        self.load_certificates()
    
    def load_certificates(self):
        #loads the certificate if the user knows the password
        for attempt in range(MAX_ATTEMPTS):
            try:
                password = getpass.getpass("Enter password for private key: ")
                self.context.load_cert_chain(certfile=CERT_FILE, keyfile=KEY_FILE, password=password)
                logging.info("Certificate and key loaded successfully.")
                return
            except ssl.SSLError as e:
                logging.warning(f"Incorrect password ({attempt + 1}/{MAX_ATTEMPTS}). Try again... \n")
        logging.critical("Too many failed attempts. Exiting.")
        exit(1)

    def broadcast(self, message: bytes, sender=None, nickname="Unknown"):
        #sends to other users
        timestamp = datetime.now(self.tz).strftime(TIME_FORMAT)
        
        message = message.decode('utf-8')
        database.save_message(nickname, message) #loads texts only into database
        full_message = f"{timestamp} {message}"


        for client,nickname in self.clients.items():
            if client is not sender:
                try:
                    client.send(full_message.encode('utf-8'))
                except Exception as e:
                    logging.error(f"Failed to send to {nickname}: {e}")
                    self.remove_client(client)

    def remove_client(self,client):
        nickname = self.clients.pop(client, None)

        if nickname:
            client.close()
            self.broadcast(f"{nickname} left the chat.".encode('utf-8'),client," SERVER_MESSAGE ")
            logging.info(f"{nickname} disconnected.")

    def is_message_ok(self,message: bytes): 
        return bool(message)

    def handle_client(self, client):
        while True:
            try:
                message = client.recv(BUFFER_SIZE)

                if not self.is_message_ok(message):
                    break

                client_nickname = self.clients.get(client)

                self.broadcast(message, client, client_nickname)

            except ConnectionResetError:
                logging.warning("Client disconnected unexpectedly.")
                break
            except Exception as e:
                logging.error(f"Server Error: {e}")
                break
        self.remove_client(client)


    def send_last_messages(self,client,username):
        messages = database.get_last_messages(LAST_MESSAGES_SENT)
        for message in messages:
            try:
                if message[0] != " SERVER_MESSAGE ":
                    client.send(f"{message[-1]} {message[-2]}".encode('utf-8'))
            except Exception as e:
                logging.error(f"Error sending message:{message} for: {client}, {e},")
                break


    def authenticate_client(self, client):
        try:
            login_type =  client.recv(BUFFER_SIZE).decode('utf-8')
            username = client.recv(BUFFER_SIZE).decode('utf-8')
            password = client.recv(BUFFER_SIZE).decode('utf-8')

            with open(BANS_FILE, 'r') as f:
                if username + '\n' in f.readlines():
                    client.send('BAN'.encode('utf-8'))
                    client.close()
                    return None, None
                
            if database.check_user(username) and login_type=="register":
                client.send('EXISTS'.encode('utf-8'))
                client.close()
                return None, None
            
            elif not database.check_user(username) and login_type=="login":
                client.send('NOT_EXISTS'.encode('utf-8'))
                client.close()
                return None, None

            auth = database.authenticate_user(username, password)
            if auth is True:
                client.send('AUTH_SUCCESS'.encode('utf-8'))
            elif auth is None and database.register_user(username, password):
                client.send('REGISTERED'.encode('utf-8'))
            else:
                client.send('REFUSE'.encode('utf-8'))
                client.close()
                return None, None

            if login_type=="login":
                self.send_last_messages(client,username)

            return client, username
        
        except Exception as e:
            logging.error(f"Authentication error: {e}")
            client.close()
            return None, None


    def receive(self):
        logging.info("Server is listening...")

        while True:
            try:
                client_socket, addr = self.server.accept()
                logging.info(f"Connected with: {addr}")

                try:
                    client = self.context.wrap_socket(client_socket, server_side=True)
                except ssl.SSLError as e:
                    logging.error(f"SSL error: {e}")
                    client_socket.close()
                    continue

                client, username = self.authenticate_client(client)
                if not client:
                    continue

                self.clients[client] = username

                self.broadcast(f'{username} has just entered the chat!'.encode('utf-8'), client, " SERVER_MESSAGE ")

                threading.Thread(target=self.handle_client, args=(client,), daemon=True).start()
            except Exception as e:
                 logging.warning(f"Connected failed with: {addr} - {e}")


    def shutdown(self):
        logging.info("Shutting down server...")
        for client in self.clients:
            try:
                client.send("Server is shutting down!".encode('utf-8'))
                client.close()
            except:
                pass
        self.clients.clear()
        self.server.close()
            

    
