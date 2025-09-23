from ServerChat import ServerChat
import logging


def main():
    
    server = ServerChat()
    try:
        server.receive()
    except KeyboardInterrupt:
        server.shutdown() 
        logging.info("Server was shutdown successfully.")


if __name__ == "__main__":
    main()