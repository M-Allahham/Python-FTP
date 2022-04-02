import os
import socket
from threading import Thread


class ClientThread(Thread):
    def __init__(self, client_socket, client_ip, client_port):
        Thread.__init__(self)
        self.socket = client_socket
        self.ip = client_ip
        self.port = client_port
        self.buffer_size = 1024
        print("Server started thread for client {} on port {}".format(self.ip, self.port))

    def run(self):
        while True:
            recv_data = self.socket.recv(self.buffer_size)
            print("Server received data: {}".format(recv_data))
            packet_info = recv_data.decode('utf-8').strip().split(",")
            print(packet_info[0])
            if packet_info[0] == "UPLOAD" and len(packet_info[1:]) == 2:
                self.__read_file(*packet_info[1:])
            elif packet_info[0] == "DOWNLOAD" and len(packet_info[1:]) == 1:
                self.__send_file(*packet_info[1:])
            elif packet_info[0] == "DIR":
                self.__list_file()
            elif packet_info[0] == "DELETE":
                self.__del_file(*packet_info[1:])
            else:
                if packet_info[0] != '':
                    print("Server does not support that check sent command")
                    self.socket.sendall("Invalid".encode('utf-8'))

            if not recv_data:
                print("Disconnecting from client {}:{}".format(self.ip, self.port))
                self.socket.shutdown(socket.SHUT_RDWR)
                self.socket.close()
                break

    def __del_file(self, file_name):
        
        try:
            os.remove(os.getcwd() + "\\server_files\\" + file_name)
            
            self.socket.sendto("deleted".encode('utf-8'), (self.ip, self.port))
            
        except:
            print("Unable to delete {}".format(file_name))
            self.socket.sendto("stink".encode('utf-8'), (self.ip, self.port))

    def __list_file(self):
        print("Listing files...")
        directory = os.getcwd() + "\server_files"
        print(directory)
        listing = os.listdir(directory)
        self.socket.sendto(str(len(listing)).encode('utf-8'), (self.ip, self.port))
        
        print(len(listing))
        for i in listing:
            
            self.socket.sendto(i.encode('utf-8'), (self.ip, self.port))
            
        
        self.socket.sendto("pinter".encode('utf-8'), (self.ip, self.port))
        print("Successfully sent file listing")

    def __read_file(self, file_name, length):
        self.socket.sendall("Ready".encode("utf-8"))
        print("Server ready to accept file: {} from client: {}:{}".format(file_name, self.ip, self.port))

        save_file = open("server_files/{}".format(file_name), "wb")

        amount_recieved_data = 0
        while amount_recieved_data < int(length):
            recv_data = self.socket.recv(self.buffer_size)
            amount_recieved_data += len(recv_data)
            save_file.write(recv_data)

        save_file.close()

        self.socket.sendall("Received,{}".format(amount_recieved_data).encode('utf-8'))
        print("Server done receiving from client {}:{}. File Saved.".format(self.ip, self.port))
    
    def __send_file(self, file_name):
        file_location = "server_files/{}".format(file_name)
        try:
            file_size = os.path.getsize(file_location)
            self.socket.sendall("Exists,{}".format(file_size).encode('utf-8'))

            while True:
                recv_data = self.socket.recv(self.buffer_size)
                packet_info = recv_data.decode('utf-8').strip().split(",")

                if packet_info[0] == "Ready":
                    print("Sending file {} to client {}".format(file_name, self.ip))

                    with open(file_location, "rb") as file:
                        self.socket.sendfile(file)
                elif packet_info[0] == "Received":
                    if int(packet_info[1]) == file_size:
                        self.socket.sendall("Success".encode('utf-8'))
                        print("{} successfully downloaded to client {}:{}".format(file_name, self.ip, self.port))
                        break
                    else:
                        print("Something went wrong trying to download to client {}:{}. Try again".format(self.ip, self.port))
                        break
                else:
                    print("Something went wrong trying to download to client {}:{}. Try again".format(self.ip, self.port))
                    break
        except IOError:
            print("File {} does not exist on server".format(file_name))
            self.socket.sendall("Failed".encode('utf-8'))