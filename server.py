import csv
import socket
from cryptography.fernet import Fernet

from client_thread import ClientThread


class Server():
    def __init__(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_address = (socket.gethostname(), 2121) 
        self.queue_max = 5
        self.buffer_size = 1024
        self.allowed_users = self.__load_users()

    def run_server(self):
        self.server_socket.bind(self.server_address)
        self.server_socket.listen(self.queue_max)
        ip, port = self.server_socket.getsockname()
        created_threads = []
        print("Server has started listening... ip: {}, port: {}".format(ip, port))

        while True:
            # wait for connections
            client_socket, (client_ip, port) = self.server_socket.accept()
            print("Connection from {}".format(client_ip))

            # want to verify client user, password before spawing thread
            while True:
                auth_data = client_socket.recv(self.buffer_size)
                print("Recieved: {}".format(auth_data))
                recv_data = auth_data.decode('utf-8').strip().split(",")
                print(recv_data)

                if len(recv_data) != 3:
                    print("The data recieved from client {} is wrong.".format(client_ip))
                    error = "Expected,'CONNECT','user:user','passwd:passwd'"
                    client_socket.sendall(error.encode('utf-8'))
                    client_socket.shutdown(socket.SHUT_RDWR)
                    client_socket.close()
                    break
                else:
                    user_info = recv_data[1].split(":")
                    pass_info = recv_data[2].split(":")
                    print(pass_info)
                    if self.__authenticate_user(user_info[1], pass_info[1]):
                        message = "Success"
                        client_socket.sendall(message.encode('utf-8'))

                        thread = ClientThread(client_socket, client_ip, port)
                        thread.start()
                        created_threads.append(thread)
                        break
                    else:
                        message = "Unknown"
                        client_socket.sendall(message.encode('utf-8'))
                        client_socket.shutdown(socket.SHUT_RDWR)
                        client_socket.close()
                        break

        for t in created_threads:
            t.join()

    def load_key():
        return open("secret.key", "rb").read()

    def decrypt_message(self, message):
        key = load_key()
        f = Fernet(key)
        decrypted_message = f.decrypt(message)
        return decrypted_message.decode()
        print(decrypted_message.decode())

    def __authenticate_user(self, user_name, passwd):
        for user in self.allowed_users:
            if user_name == user["name"]:
                print(user_name)
                return decrypt_message(user["passwd"]) == passwd
            
        return False

    def __load_users(self):
        users = []
        with open("allowed_users.txt", "r") as user_file:
            user_csv = csv.DictReader(user_file)
            for user in user_csv:
                users.append(user)

        return users