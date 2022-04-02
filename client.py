import os
import socket
import sys
from cmd import Cmd
from socket import error as socket_error

import shutil
from pathlib import Path
import time

class Client(Cmd):
    def __init__(self):
        Cmd.__init__(self)
        Cmd.intro = "Starting client. Type help or ? to list commands.\n"
        Cmd.prompt = ">>> "
        self.socket = None 
        self.ftp_port = 2121
        self.connected = False

    def do_SCENARIO1(self, args):
        starttime = time.time()
            # client requests text file
        self.do_DOWNLOAD("TC2.txt")
        self.do_DOWNLOAD("TC2.txt")
            # if not, server requests client 2 upload
        self.do_UPLOAD("TC2.txt")
            # check until has
            # send to client 1
        self.do_DOWNLOAD("TC2.txt")
            # delete from server after ack
        self.do_DELETE("TC2.txt")
        print(time.time() - starttime)
        
    def do_SCENARIO21(self, args):
        starttime = time.time()
        #client asks for two files
        self.do_DOWNLOAD("TC2.txt")
        self.do_DOWNLOAD("TS.txt")
        #server checks and sends for one file
        #client 2 uploads file
        self.do_UPLOAD("TC2.txt")
        #server sends to client1
        self.do_DOWNLOAD("TC2.txt")
        print(time.time() - starttime)
        
    def do_SCENARIO22(self, args):
        starttime = time.time()
        #client asks for two files
        self.do_DOWNLOAD("TC2.txt")
        self.do_DOWNLOAD("TS.txt")
        #server asks for other file from client 2
        self.do_UPLOAD("TC2.txt")
        
        #server merges files
        firstfile = Path('server_files\TC2.txt')
        secondfile = Path('server_files\TS.txt')
        os.chdir("./server_files")
        newfile = "newfile.txt"
        os.chdir("..")
        print()
        print("The merged content of the 2 files will be in", newfile)
  
        with open(newfile, "wb") as wfd:
  
            for f in [firstfile, secondfile]:
                with open(f, "rb") as fd:
                    shutil.copyfileobj(fd, wfd, 1024 * 1024 * 10)
            
            #server sends merged to client 1
        self.do_DOWNLOAD("newfile.txt")
        print(time.time() - starttime)
        
    def do_SCENARIO23(self, args):
        starttime = time.time()
        #client asks for two files
        self.do_DOWNLOAD("TC2.txt")
        self.do_DOWNLOAD("TS.txt")
        #server asks for other file from client2
        self.do_UPLOAD("TC2.txt")
        #server sends both files to client 1
        self.do_DOWNLOAD("TC2.txt")
        self.do_DOWNLOAD("TS.txt")
        print(time.time() - starttime)

    def do_DELETE(self, args):
        if self.connected:
            vals = args.split()
            if len(vals) == 1:
                file_name = vals[0]
                print("Trying to delete file {} on server.".format(file_name))
                print()

                try:
                    packet = "DELETE,{}".format(file_name)
                    self.socket.sendall(packet.encode('utf-8'))
                    recvdata = self.socket.recv(1024)
                    while recvdata.decode('utf-8') != "deleted":
                        recvdata = self.socket.recv(1024)
                        
                    print("Deleted Successfully")
                    
                except socket_error:
                    message = (
                        "Looks something happened to server {}. "
                        "Check and ensure you have the right address "
                        "and the server is running.".format(self.socket.getpeername())
                    )
                    print(message)
            else:
                print("DELETE requires exactly 1 arguments...")
                print()
        else:
            print("You must use the 'CONNECT' command to first connect to a server before uploading a file.")

    def do_DIR(self, args):
        
        if self.connected:
        
                packet = "DIR,{}"
                self.socket.sendall(packet.encode('utf-8'))
                recv_data = self.socket.recv(1024)
                #print(recv_data.decode("utf-8").strip())
                for i in range(int(recv_data.decode("utf-8").strip())):
                    recv_data = self.socket.recv(1024)
                    packet_info = recv_data.decode('utf-8').strip().split(",")
                    
                    for packet in packet_info:
                        if packet.__contains__("pinter"):
                            break
                        else:
                            print(packet)
                

    def do_CONNECT(self, args):
        vals = args.split()
        if len(vals) == 4:
            if self.connected:
                print("Client already connected to server (ip, port) : {}".format(self.socket.getpeername()))
            else:
                server_ip, server_port, user_name, password = vals
                print("Trying to connect to server {}:{} with user:password -> {}:{}".format(server_ip, server_port, user_name, password))
                print()
                try:
                    self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    self.socket.connect((server_ip, int(server_port))) #self.ftp_port))
                    packet = "CONNECT,user:{},passwd:{}".format(user_name, password)
                    print("Sending message: {}".format(packet))
                    self.socket.sendall(packet.encode('utf-8'))

                    while True:
                        recv_data = self.socket.recv(1024)
                        recv_data = recv_data.decode('utf-8').strip().split(",")

                        if recv_data[0] == 'Success':
                            self.connected = True
                            print("Successfully Authenticated!")
                            break

                        if recv_data[0] == 'Unknown':
                            self.connected = False
                            print("User name and password incorrect, connection refused.")
                            self.socket.shutdown(socket.SHUT_RDWR)
                            self.socket.close()
                            break

                        if recv_data[0] == 'Expected':
                            self.connected = False
                            print("The client did not send the correct information, connection refused.")
                            self.socket.shutdown(socket.SHUT_RDWR)
                            self.socket.close()
                            break
                        
                except socket_error:
                    message = (
                        "Looks something happened to server {}. "
                        "Check and ensure you have the right address "
                        "and the server is running.".format(server_ip)
                    )
                    print(message)
        else:
            print("CONNECT requires exactly 4 arguments...")
            print()

    def do_DOWNLOAD(self, args):
        if self.connected:
            vals = args.split()
            if len(vals) == 1:
                file_name = vals[0]
                print("Trying to download file {} from server to client.".format(file_name))
                print()

                try:
                    packet = "DOWNLOAD,{}".format(file_name)
                    self.socket.sendall(packet.encode('utf-8'))

                    while True:
                        recv_data = self.socket.recv(1024)
                        packet_info = recv_data.decode('utf-8').strip().split(",")

                        if packet_info[0] == "Exists":
                            self.socket.sendall("Ready".encode('utf-8'))
                            print("{} exits on the server, ready to download.".format(file_name))

                            save_file = open(file_name, "wb")

                            amount_recieved_data = 0
                            while amount_recieved_data < int(packet_info[1]):
                                recv_data = self.socket.recv(1024)
                                amount_recieved_data += len(recv_data)
                                save_file.write(recv_data)

                            save_file.close()

                            self.socket.sendall("Received,{}".format(amount_recieved_data).encode('utf-8'))
                        elif packet_info[0] == "Success":
                            print("Client done downloading {} from server. File Saved.".format(file_name))
                            break
                        elif packet_info[0] == "Failed":
                            print("File {} does not exist on server.".format(file_name))
                            break
                        else:
                            print("Something went wrong when downloading {} from server. Try again.".format(file_name))
                            break
                except socket_error:
                    message = (
                        "Looks something happened to server {}. "
                        "Check and ensure you have the right address "
                        "and the server is running.".format(self.socket.getpeername())
                    )
                    print(message)
            else:
                print("DOWNLOAD requires exactly 1 arguments...")
                print()
        else:
            print("You must use the 'CONNECT' command to first connect to a server before uploading a file.")
    
    def do_UPLOAD(self, args):
        if self.connected:
            vals = args.split()
            if len(vals) == 1:
                file_name = vals[0]
                print("Trying to upload file {} from client to server.".format(file_name))
                print()

                try:
                    packet = "UPLOAD,{},{}".format(file_name, os.path.getsize(file_name))
                    self.socket.sendall(packet.encode('utf-8'))
                    
                    while True:
                        recv_data = self.socket.recv(1024)
                        packet_info = recv_data.decode('utf-8').strip().split(",")

                        if packet_info[0] == "Ready":
                            print("Sending file {} to server {}".format(file_name, self.socket.getpeername()))

                            with open(file_name, mode="rb") as file:
                                self.socket.sendfile(file)
                        elif packet_info[0] == "Received":
                            if int(packet_info[1]) == os.path.getsize(file_name):
                                print("{} successfully uploaded to server {}".format(file_name, self.socket.getpeername()))
                                break
                            else:
                                print("Something went wrong trying to upload to server {}. Try again".format(self.socket.getpeername()))
                                break
                        else:
                            print("Something went wrong trying to upload to server {}. Try again.".format(self.socket.getpeername()))
                            break
                except IOError:
                    print("File doesn't exist on the system!")
            else:        
                print("UPLOAD requires exactly 1 arguments...")
                print()
        else:
            print("You must use the 'CONNECT' command to first connect to a server before uploading a file.")

    def do_QUIT(self, args):
        if self.socket is not None:
            if self.socket.fileno() != -1:
                self.socket.close()
        sys.exit("Quitting...")