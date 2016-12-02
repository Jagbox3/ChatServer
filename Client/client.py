#!/usr/bin/env python
#Client

#imports
import sys
import socket
from threading import Thread
from queue import Queue

class Client:
    def __init__(self, log, message_queue):
        self.message_queue = message_queue
        self.log = log
        self.packet_size = 1024
        self.info = ""
        self.sock = None
        self.off = False
        self.send = None
        self.get = None
        self.username = ""

    #threads
    def get_messages(self):
        try:
            while True:
                if self.off:
                    break
                data = self.sock.recv(self.packet_size)
                if not data == b"":
                    self.log.put(data.decode("utf-8"))
                    print(data.decode("utf-8"))
        except:
            pass
    def send_messages(self):
        try:
            self.sock.sendall(bytearray(str.encode("/user " + self.username)))
            while True:
                info = ""
                if self.off:
                    print("breaking send")
                    break
                if not self.message_queue.empty():
                    print("getting msgs")
                    info = self.message_queue.get()
                try:
                    if not info == "":
                        self.sock.sendall(bytearray(str.encode(info)))
                        self.log.put(self.username + ": " + info)
                        if info == "/leave":
                            self.leave()
                except:
                    pass
        except:
            pass

    def start(self, address, username):
        self.off = False
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.username = username

        #begin connection
        print("Connecting to server at ip %s:%s" % address)
        self.log.put("Connecting to server at ip %s:%s" % address)
        try:
            self.sock.connect(address)
        except ConnectionRefusedError as cre:
            print("Error: Could not connect to ip %s:%s" % address)
            self.log.put("Error: Could not connect to ip %s:%s" % address)
            return
        except socket.gaierror as e:
            print("Error: Could not gather address info")
            self.log.put("Error: Could not gather address info")
            return

        print("Connected...")
        self.log.put("Connected")
        self.send = Thread(target=self.send_messages)
        self.get = Thread(target=self.get_messages)

        try:
            self.send.start()
            self.get.start()
        finally:
            pass

    def leave(self):
        if self.sock is not None:
            try:
                self.sock.sendall(bytearray(str.encode("/leave")))
            except:
                print("Server wasn't on.")
            self.off = True
            print("Closing connection.")
            self.log.put("Disconnected")
            if self.send.is_alive():
                self.send.join()
            if self.get.is_alive():
                self.get.join()
            try:
                self.sock.shutdown(socket.SHUT_RDWR)
                self.sock.close()
                self.sock = None
            except:
                print("Wasn't connected in the first place")