import logging
import socket
import sys
import threading
import time
from urllib import request

from cryptography.fernet import Fernet, InvalidToken

aliases = {}
connected = ""

COMMANDS = ["/alias", "/help", "/ip", "/quit", "/time"]
LOCAL_PORT = 2048
REMOTE_PORT = 2048
LOCAL_ALT_PORT = 4096
REMOTE_ALT_PORT = 4096


class Server(threading.Thread):
    def run(self):
        """Handles all of the incoming messages."""
        global connected
        # listen for ipv4 connections on all hosts
        self.incoming = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.incoming.bind(("", LOCAL_PORT))
            logging.info(f"Listening on port {LOCAL_PORT}")
        except Exception as e:
            logging.error(str(e))
            logging.info("Trying alternate local")
            self.incoming.bind(("", LOCAL_ALT_PORT))
            logging.info(f"Listening on port {LOCAL_ALT_PORT}")
        self.incoming.listen(1)

        # connect to peer automatically
        peer, address = self.incoming.accept()
        logging.info(f"New connection {address[0]}")
        if not connected:
            client.connect(address[0])

        # listen for messages forever
        while True:
            try:
                message = f"{aliases.get(address[0], address[0])}: {fernet.decrypt(peer.recv(1024)).decode()}"
                print(message)
                logging.debug(message)
            except Exception as e:
                logging.error(str(e))
                logging.info(
                    f"Error from {aliases.get(address[0], address[0])}")


class Client(threading.Thread):
    def alias(self, args):
        """Alias args[1] (an IP) to args[2] (any string)."""
        aliases[args[1]] = args[2]
        logging.info(f"Aliased {args[1]} to {args[2]}")

    def help(self, args):
        """Displays all of the available commands."""
        logging.info(" ".join(COMMANDS))

    def ip(self, args):
        """Return the IP address of the computer."""
        logging.info(request.urlopen(
            "http://ipv4.icanhazip.com").read().decode("utf8").strip())

    def quit(self, args):
        """Quits the program and properly closes sockets."""
        client.outgoing.close()
        logging.info("Quit successfully")
        raise SystemExit

    def time(self, args):
        """Displays the current local time."""
        logging.info(time.ctime())

    def connect(self, target_host):
        """Tries the primary and alternate ports."""
        global connected
        try:
            self.outgoing.connect((target_host, REMOTE_PORT))
        except Exception as e:
            logging.error(str(e))
            logging.info("Trying alternate remote")
            try:
                self.outgoing.connect((target_host, REMOTE_ALT_PORT))
            except Exception as e:
                logging.error(str(e))
            else:
                connected = target_host
        else:
            connected = target_host

    def run(self):
        """Handles all of the outgoing messages."""
        global connected
        # Connect to a specified peer
        logging.info(f"/help to list commands")
        self.outgoing = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        while not connected:
            target_host = input("HOST: ")
            self.connect(target_host)
        logging.info(f"Connected to {connected}")

        # Either send message or run command
        while True:
            message = input("")
            if message:
                logging.debug(message)
                check_command = message.split()
                if check_command[0] in COMMANDS:
                    # hack to call function with name
                    try:
                        getattr(self, check_command[0][1:])(check_command)
                    except Exception as e:
                        logging.error(str(e))
                else:
                    self.outgoing.sendall(fernet.encrypt(message.encode()))


if __name__ == "__main__":
    # setup message output and logging
    handlers = [logging.StreamHandler(sys.stdout)]
    handlers[0].setLevel(logging.INFO)
    if input("Log? (y/n): ").lower() == "y":
        handlers.append(logging.FileHandler(filename='snakewhisper.log'))
        handlers[1].setFormatter(logging.Formatter(
            "%(asctime)s - %(levelname)s: %(message)s"))
    logging.basicConfig(level=logging.DEBUG,
                        format="%(levelname)s: %(message)s", handlers=handlers)

    # get and validate the key
    while True:
        try:
            key = input("KEY: ")
            fernet = Fernet(key)
        except Exception as e:
            logging.error(str(e))
        else:
            break

    # start the combined server and client
    server = Server()
    server.daemon = True
    server.start()
    time.sleep(1)
    client = Client()
    client.start()
