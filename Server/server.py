#Server

#imports

from ast import literal_eval
from queue import Queue
from Client.restartablethread import RestartableThread
import socket

class Server:
    def __init__(self, log):
        self.connectionDict = dict()
        self.threadDict = dict()
        self.userDict = dict()
        self.packet_size = 1024
        self.max_connections = 4
        self.log = log
        self.off = False
        self.server_address = ""
        self.sock = None
        # init threads
        self.connQ = Queue()
        self.msgQ = Queue()
        self.clients = RestartableThread(target=self.connections)
        self.distribute = RestartableThread(target=self.reply)

    # conn thread accepts new connections and sends them to messages thread

    def is_spam(self, client):
        if len(self.threadDict) > 0:
            for x in self.threadDict:
                if client[1][0] == x[0]:
                    return True
        return False

    def connections(self):
        current_connections = 0
        while current_connections < self.max_connections:
            if self.off:
                break
            print("Waiting for a connection...")
            self.log.put("Waiting for a connection...")
            client = self.sock.accept()
            if self.off:
                break
            print("Client connected from:", client[1])
            self.log.put("Client connected from: " + str(client[1]))
            if self.is_spam(client):
                print("Client kicked due to being a spam connection")
                self.log.put("Client kicked due to being a spam connection")
                client[0].sendall(bytearray(str.encode("Booted for spam.")))
                client[0].close()
                continue
            self.connQ.put(client)
        else:
            client = self.sock.accept()
            print("Kicking client from:", client[1], "(Max capacity)")
            self.log.put("Kicking client from: " + str(client[1]) + "(Max capacity)")
            client[0].sendall(bytearray(str.encode("Disconnecting due to server capacity full.\nType anything to continue...")))

    # receives from clients
    def listen(self, client):
        connection, client_address = client
        while True:
            if self.off:
                break
            info = ""
            try:
                data = connection.recv(self.packet_size)
                info = data.decode("utf-8")
            except:
                # a client must have left...
                pass
            if len(info) == 0:
                # end this thread
                print("No length message received.")
                info = "close:" + str(client_address)
                self.msgQ.put(info)
                break
            if info[0] == "/":
                # whatever they typed will now be read as a command
                command = data.decode("utf-8").replace("/", "").split(" ")
                # command holds all the parts of a command in this order:
                # command arg arg arg arg arg arg ... arg
                if command[0] == "user":
                    if len(command) > 1:
                        if client_address in self.userDict:
                            if self.userDict[client_address] != command[1]:
                                info = "[Server] " + self.userDict[client_address] + " has changed his name to " + command[1]
                                self.userDict[client_address] = command[1]
                        else:
                            info = "[Server] " + command[1] + " has joined the server!"
                            self.userDict[client_address] = command[1]
                        if not info == "":
                            self.msgQ.put(info)
                elif command[0] == "leave":
                    info = "[Server] " + self.userDict[client_address] + " has left the server."
                    self.msgQ.put(info)
                elif command[0] == "users":
                    # list all users
                    info = "users:" + str(client_address) + ":[Server] Current users: " + str(self.userDict.values())
                    # to send to a single client, message format as /client_address
                    self.msgQ.put(info)
            else:
                # a normal message
                if not info == "":
                    info = self.userDict[client_address] + ": " + data.decode("utf-8")
                    self.msgQ.put(info)

    # replies to all clients
    def reply(self):
        while True:
            if self.off:
                break
            info = b""
            try:
                # initialize new threads for newly made connections
                if not self.connQ.empty():
                    item = self.connQ.get()
                    self.connectionDict[item[1]] = item # add to connectionDict
                    ct = RestartableThread(target=self.listen, args=(item,))
                    ct.start()
                    self.threadDict[item[1]] = ct # add to threadDict
                else:
                    # queue empty
                    pass
            except:
                print("[ERR] Adding more clients to the threadDict")
            try:
                if not self.msgQ.empty():
                    info = self.msgQ.get()
                    print("info gotten: %s" % info)
                if not info == b"":
                    # if the server has received a closing message (0 length message, end that thread)
                    if info.split(":")[0] == "close":
                        client_address = info.split(":")[1]
                        address = literal_eval(client_address)
                        self.threadDict[address].join()
                        del self.threadDict[address]
                        del self.connectionDict[address]
                        continue
                    if info.split(":")[0] == "users":
                        # [0] --> users
                        # [1] --> client address
                        # [2] --> current users are:
                        # [3+] -> actual users list
                        pass
                    print(info)
                    self.log.put(info)
                    for conn in self.connectionDict.values():
                        connection, client_address = conn
                        name = info.split(":")[0]
                        # if the server has received a closing message (0 length message, end that thread)
                        if not name == self.userDict.get(client_address):
                            # if not the person who sent the message
                            # send back to all other clients
                            try:
                                connection.sendall(bytearray(str.encode(info)))
                            except:
                                # a client must have left...
                                print("Send messages error.")
                                pass
            finally:
                pass

    def start(self, server_address):
        self.off = False
        self.server_address = server_address
        # init server socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # set up address
        print("Starting on %s:%s" % self.server_address)
        self.log.put("Starting on %s:%s" % self.server_address)
        self.sock.bind(self.server_address)
        # set to server mode to accept other sockets
        self.sock.listen(1)
        # start the server
        try:
            self.clients.start()
            self.distribute.start()
            print("Threads started.")
            self.log.put("Threads started.")
        except (EOFError, NameError):
            # if any errors, end all threads
            print("Error")
            self.clients.join()
            self.distribute.join()
            for ct in self.threadDict:
                ct.join()

    def destroy(self):
        if not self.off:
            self.off = True
        if self.clients.is_alive():
            self.create_fake_client()
            self.clients.join()
            self.clients = self.clients.clone()
            self.clients.clone().start()
        if self.distribute.is_alive():
            self.distribute.join()
        self.distribute = self.distribute.clone()
        if len(self.threadDict.values()) > 0:
            for ct in self.threadDict.values():
                ct.join()
                del ct
        self.sock.close()
        self.log.put("Shutdown procedure complete.")

    def create_fake_client(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            s.connect(self.server_address)
            s.shutdown(socket.SHUT_RDWR)
            s.close()
        except:
            print("Couldn't connect.")