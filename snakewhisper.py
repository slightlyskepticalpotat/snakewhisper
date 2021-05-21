import base64
import logging
import os
import socket
import sys
import threading
import time
from urllib import request

from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import x25519
from cryptography.hazmat.primitives.kdf.hkdf import HKDFExpand
from cryptography.hazmat.primitives.serialization import (Encoding,
                                                          NoEncryption,
                                                          PrivateFormat,
                                                          PublicFormat,
                                                          load_pem_public_key)

aliases = {}
connected = None
fernet = None
private_key = None

COMMANDS = ["/alias", "/clear", "/help", "/ip",
            "/privkey", "/quit", "/remote", "/time"]
LOCAL_ALT_PORT = 4096
LOCAL_PORT = 2048
REMOTE_ALT_PORT = 4096
REMOTE_PORT = 2048


class Server(threading.Thread):
    def accept_connection(self):
        """Accepts connection and derives a shared key."""
        global connected, fernet
        try:
            # exchange the ec public key
            peer_public_key = load_pem_public_key(self.peer.recv(1024))
            self.peer.sendall(private_key.public_key().public_bytes(
                Encoding.PEM, PublicFormat.SubjectPublicKeyInfo))
            shared_key = private_key.exchange(peer_public_key)
            derived_key = HKDFExpand(algorithm=hashes.SHA256(),
                                     length=32, info=None).derive(shared_key)
            fernet = Fernet(base64.urlsafe_b64encode(derived_key))
        except Exception as e:
            logging.error(str(e))

    def run(self):
        """Handles all of the incoming messages."""
        global connected, fernet, private_key
        while True:
            # generate a private key
            logging.info("Generating private key")
            private_key = x25519.X25519PrivateKey.generate()

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
            self.peer, self.address = self.incoming.accept()
            if not connected:
                self.accept_connection()
                client.initate_connection(self.address[0], True)
                logging.info(f"New connection {self.address[0]}")
                logging.info(f"Press enter to continue")

            # listen for messages forever
            while True:
                try:
                    message = f"{aliases.get(self.address[0], self.address[0])}: {fernet.decrypt(self.peer.recv(1024)).decode()}"
                    print(message)
                    logging.debug(message)
                except Exception as e:
                    if not str(e):
                        # empty string means peer disconnected
                        logging.info(
                            f"{aliases.get(self.address[0], self.address[0])} disconnected")
                        self.incoming.close()
                        connected = None
                        break
                    logging.error(str(e))
                    logging.info(
                        f"Error from {aliases.get(self.address[0], self.address[0])}")


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

    def privkey(self, args):
        """Shows the local private key"""
        logging.info("Do not disclose this key")
        logging.info(private_key.private_bytes(
            Encoding.PEM, PrivateFormat.Raw, NoEncryption()).decode())

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

    def initate_connection(self, target_host, no_exchange=False):
        """Tries the primary and alternate ports."""
        global connected, fernet
        # establish an initial connection
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

        # setup connection from server thread
        connected = target_host
        if no_exchange:
            return

        # exchange the ec public key
        try:
            self.outgoing.sendall(private_key.public_key().public_bytes(
                Encoding.PEM, PublicFormat.SubjectPublicKeyInfo))
            peer_public_key = load_pem_public_key(self.outgoing.recv(1024))
            shared_key = private_key.exchange(peer_public_key)
            derived_key = HKDFExpand(algorithm=hashes.SHA256(),
                                     length=32, info=None).derive(shared_key)
            fernet = Fernet(base64.urlsafe_b64encode(derived_key))
        except Exception as e:
            logging.error(str(e))
            connected = None

    def run(self):
        """Handles all of the outgoing messages."""
        global connected, fernet
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
                                    self, check_command[0][1:])(check_command)
                            except Exception as e:
                                logging.error(str(e))
                        else:
                            self.outgoing.sendall(
                                fernet.encrypt(message.encode()))
            except Exception as e:
                logging.error(str(e))
                connected = None


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

    # start the combined server and client
    server = Server()
    server.daemon = True
    server.start()
    time.sleep(1)
    client = Client()
    client.start()
