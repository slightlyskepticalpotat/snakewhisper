import logging
import os
import socket
import sys
import threading
import time
from urllib import request

from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives.serialization import (Encoding,
                                                          PublicFormat,
                                                          load_pem_public_key)

aliases = {}
connected = ""
fernet = ""
private_key = ""
peer_public_key = ""
shared_key = ""

COMMANDS = ["/alias", "/clear", "/help", "/ip", "/quit", "/remote", "/time"]
LOCAL_ALT_PORT = 4096
LOCAL_PORT = 2048
REMOTE_ALT_PORT = 4096
REMOTE_PORT = 2048


class Server(threading.Thread):
    def accept_connection(self):
        """Accepts a connection and does key exchange."""
        try:
            self.incoming.sendall(private_key.public_key().public_bytes(
                Encoding.PEM, PublicFormat.SubjectPublicKeyInfo))
            peer_public_key = self.incoming.recv(4096)
            peer_public_key = load_pem_public_key(self.incoming.recv(4096))
            shared_key = private_key.exchange(ec.ECDH(), peer_public_key)
            print(len(shared_key))
        except Exception as e:
            logging.error(str(e))

    def run(self):
        """Handles all of the incoming messages."""
        global connected, private_key
        while True:
            # generate a private key
            logging.info("Generating private key")
            private_key = ec.generate_private_key(ec.SECP521R1())
            print(private_key.public_key().public_bytes(
                Encoding.PEM, PublicFormat.SubjectPublicKeyInfo))

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

            # connect to peer automatically
            self.incoming.listen(1)
            peer, address = self.incoming.accept()
            logging.info(f"New connection {address[0]}")
            self.accept_connection()
            logging.info(f"Press enter to continue")

            # listen for messages forever
            while True:
                try:
                    message = f"{aliases.get(address[0], address[0])}: {fernet.decrypt(peer.recv(1024)).decode()}"
                    print(message)
                    logging.debug(message)
                except Exception as e:
                    if not str(e):
                        # almost restart the thread
                        logging.info(
                            f"{aliases.get(address[0], address[0])} disconnected")
                        self.incoming.close()
                        connected = ""
                        break
                    logging.error(str(e))
                    logging.info(
                        f"Error from {aliases.get(address[0], address[0])}")


class Client(threading.Thread):
    def alias(self, args):
        """Aliases an IP to a name"""
        aliases[args[1]] = args[2]
        logging.info(f"Aliased {args[1]} to {args[2]}")

    def clear(self, args):
        """Clears the console"""
        if os.name == "posix":
            os.system("clear")
        else:
            os.system("cls")
        logging.info("Console cleared")

    def help(self, args):
        """Shows all commands or info"""
        if len(args) > 1 and "/" + args[1] in COMMANDS:
            logging.info(getattr(self, args[1]).__doc__)
        else:
            logging.info(" ".join(COMMANDS))

    def ip(self, args):
        """Shows local IP address"""
        logging.info(request.urlopen(
            "http://ipv4.icanhazip.com").read().decode("utf8").strip())

    def quit(self, args):
        """Quits the program"""
        client.outgoing.close()
        logging.info("Quit successfully")
        raise SystemExit

    def remote(self, args):
        """Shows connected IP address"""
        if connected:
            logging.info(f"Connected to {connected}")
        else:
            logging.info("Currently not connected")

    def time(self, args):
        """Shows current local time"""
        logging.info(time.ctime())

    def initate_connection(self, target_host):
        """Tries the primary and alternate ports."""
        global connected, peer_public_key
        # establish initial connection
        try:
            self.outgoing.connect((target_host, REMOTE_PORT))
        except Exception as e:
            logging.error(str(e))
            logging.info("Trying alternate remote")
            try:
                self.outgoing.connect((target_host, REMOTE_ALT_PORT))
            except Exception as e:
                logging.error(str(e))
                return

        # exchange the ec public key
        try:
            self.outgoing.sendall(private_key.public_key().public_bytes(
                Encoding.PEM, PublicFormat.SubjectPublicKeyInfo))
            peer_public_key = self.outgoing.recv(4096)
            peer_public_key = load_pem_public_key(self.outgoing.recv(4096))
            shared_key = private_key.exchange(ec.ECDH(), peer_public_key)
            print(len(shared_key))
        except Exception as e:
            logging.error(str(e))
            return
        connected = target_host

    def run(self):
        """Handles all of the outgoing messages."""
        global connected
        # Connect to a specified peer
        logging.info(f"/help to list commands")
        while True:
            self.outgoing = socket.socket(
                socket.AF_INET, socket.SOCK_STREAM)
            while not connected:
                target_host = input("HOST: ")
                if target_host:
                    logging.info(f"Connecting to {target_host}")
                    self.initate_connection(target_host)
            logging.info(f"Connected to {connected}")

            try:
                # Either send message or run command
                while True:
                    message = input("")
                    if message:
                        logging.debug(message)
                        check_command = message.split()
                        if check_command[0] in COMMANDS:
                            # hack to call function with name
                            try:
                                getattr(
                                    self, check_command[0][1:])(
                                    check_command)
                            except Exception as e:
                                logging.error(str(e))
                        else:
                            self.outgoing.sendall(
                                fernet.encrypt(message.encode()))
            except Exception as e:
                logging.error(str(e))
                connected = ""


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
