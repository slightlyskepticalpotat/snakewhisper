import socket
import sys
import threading
import time

from cryptography.fernet import Fernet, InvalidToken

aliases = {}
connected = set()

COMMANDS = {"/alias", "/help", "/quit"}
LOCAL_PORT = 2048
REMOTE_PORT = 2048
LOCAL_ALT_PORT = 4096
REMOTE_ALT_PORT = 4096


class Server(threading.Thread):
    def run(self):
        """Handles all of the incoming messages."""
        # listen for ipv4 connections on all hosts
        self.peer = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.peer.bind(("", LOCAL_PORT))
            print(f"INFO: Listening on port {LOCAL_PORT}")
        except Exception as e:
            print(f"ERROR: {str(e)}")
            print(f"INFO: Trying alternate local")
            self.peer.bind(("", LOCAL_ALT_PORT))
            print(f"INFO: Listening on port {LOCAL_ALT_PORT}")
        self.peer.listen(1)

        # listen for messages forever
        peer, address = self.peer.accept()
        print(f"INFO: New connection {address[0]}")
        while True:
            message = peer.recv(1024)
            try:
                print(f"{aliases.get(address[0], address[0])}: {fernet.decrypt(message).decode()}")
            except InvalidToken:
                print(f"ERROR: {aliases.get(address[0], address[0])} using wrong key")


class Client(threading.Thread):
    def alias(self, args):
        """Alias args[1] (an IP) to args[2] (any string)."""
        aliases[args[1]] = args[2]

    def help(self, args):
        """Displays all of the available commands."""
        print(" ".join(COMMANDS))

    def quit(self, args):
        """Quits the program and properly closes sockets."""
        server.peer.shutdown(1)
        server.peer.close()
        raise SystemExit

    def run(self):
        """Handles all of the outgoing messages."""
        # Connect to a specified peer
        self.peer = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        while True:
            target_host = input("HOST: ")
            try:
                self.peer.connect((target_host, REMOTE_PORT))
            except Exception as e:
                print(f"ERROR: {str(e)}")
                print(f"INFO: Trying alternate remote")
                try:
                    self.peer.connect((target_host, REMOTE_ALT_PORT))
                except Exception as e:
                    print(f"ERROR: {str(e)}")
                else:
                    break
            else:
                break
        print(f"INFO: Connected to {target_host}")

        # Either send message or run command
        while True:
            message = input("")
            if message:
                check_command = message.lower().split()
                if check_command[0] in COMMANDS:
                    # hack to call function with name
                    getattr(self, check_command[0][1:])(check_command)
                else:
                    self.peer.send(fernet.encrypt(message.encode()))

if __name__ == "__main__":
    # get and validate the key
    while True:
        try:
            key = input("KEY: ")
            fernet = Fernet(key)
        except Exception as e:
            print(f"ERROR: {str(e)}")
        else:
            break

    # start the combined server and client
    server = Server()
    server.daemon = True
    server.start()
    time.sleep(1)
    client = Client()
    client.start()
