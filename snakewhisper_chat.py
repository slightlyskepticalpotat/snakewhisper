import socket
import threading
import time

COMMANDS = {"/alias", "/help", "/quit")
PORT = 2048

aliases = {}
connected = set()


class Server(threading.Thread):
    def run(self):
        # listen for ipv4 connections on all hosts
        self.peer = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.peer.bind(("", PORT))
        self.peer.listen(1)
        print(f"INFO: Listening on port {PORT}")

        # listen for messages forever
        peer, address = self.peer.accept()
        print(f"INFO: New connection {address[0]}")
        while True:
            message = peer.recv(1024)
            print(f"{aliases.get(address[0], address[0])}: {message.decode()}")


class Client(threading.Thread):
    def alias(self, args):
        aliases[args[1]] = args[2]

    def help(self, args):
        print(" ".join(COMMANDS))

    def quit(self, args):
        server.peer.shutdown(1)
        server.peer.close()
        raise SystemExit

    def run(self):
        # Connect to a specified peer
        self.peer = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        while True:
            target_host = input("HOST: ")
            try:
                self.peer.connect((target_host, PORT))
                break
            except Exception as e:
                print(f"ERROR: {str(e)}")
        print(f"INFO: Connected to {target_host}")

        # Either send message or command
        while True:
            message = input("> ")
            if message:
                check_command = message.lower().split()
                if check_command[0] in COMMANDS:
                    # hack to call command with name
                    getattr(self, check_command[0][1:])(check_command)
                else:
                    self.peer.send(message.encode())
            time.sleep(1)


if __name__ == "__main__":
    server = Server()
    server.daemon = True
    server.start()
    time.sleep(1)
    client = Client()
    client.start()
    print("INFO: Successful start")
