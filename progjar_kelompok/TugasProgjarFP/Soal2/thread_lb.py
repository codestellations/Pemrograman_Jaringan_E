from socket import *
import socket
import threading
import time
import sys
import logging

class BackendList:
    def __init__(self):
        self.servers=[]
        self.servers.append(('127.0.0.1', 9001))
        self.servers.append(('127.0.0.1', 9002))
        self.servers.append(('127.0.0.1', 9003))
        self.servers.append(('127.0.0.1', 9004))
        self.servers.append(('127.0.0.1', 9005))
        self.current=0
    def getserver(self):
        s = self.servers[self.current]
        self.current=self.current+1
        if (self.current>=len(self.servers)):
            self.current=0
        return s

class ProcessTheClient(threading.Thread):
    def __init__(self, connection, address):
        self.connection = connection
        self.address = address
        threading.Thread.__init__(self)

    def run(self):
        rcv=""
        while True:
            try:
                data = self.connection.recv(8192)
                self.destination_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                if data:
                    server = bserver.getserver()
                    print(f"forwarded to server {server}")
                    self.destination_sock.connect(server)
                    self.destination_sock.sendall(data)
                    data_balasan = self.destination_sock.recv(8192)
                    self.connection.sendall(data_balasan)
                    # logging.warning(data)
                    # logging.warning(data_balasan)
                    break
                else:
                    break
            except OSError as e:
                pass
        self.connection.close()



class Server(threading.Thread):
    def __init__(self, portnumber):
        self.my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        self.my_socket.bind(('0.0.0.0', portnumber))
        self.my_socket.listen(5)

        logging.warning("load balancer running on port {}".format(portnumber))

        threading.Thread.__init__(self)

    def run(self):
        # self.my_socket.bind(('0.0.0.0', 18000))
        # self.my_socket.listen(5)
        while True:
            self.connection, self.client_address = self.my_socket.accept()
            logging.warning("connection from {}".format(self.client_address))

            clt = ProcessTheClient(self.connection, self.client_address)
            clt.start()



def main():
    portnumber = 18000
    try:
        portnumber = int(sys.argv[1])
    except:
        pass
    svr = Server(portnumber)
    # svr = Server()
    svr.start()

if __name__=="__main__":
    bserver = BackendList()
    main()
