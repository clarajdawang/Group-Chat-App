import os
import socket
import threading


MSG_ENCODING = "utf-8"

class Server:

    HOSTNAME = "127.0.0.1"

    PORT = 50000
    RECV_SIZE = 1024
    BACKLOG = 5

    def __init__(self):
        self.server_main()

    def create_listen_socket(self):
        try:
            # Create the TCP server listen socket in the usual way.
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.socket.bind((Server.HOSTNAME, Server.PORT))
            self.socket.listen(Server.BACKLOG)
            print("Listening on port {} ...".format(Server.PORT))
        except Exception as msg:
            print(msg)
            exit()

    def process_connections_forever(self):
        try:
            while True:
                thread = threading.Thread(target=self.handle_client(self.socket.accept()), daemon=True)
                thread.start()

        except KeyboardInterrupt:
            print()
        finally:
            self.socket.close()
    
    def handle_client(self, client):
        connection,address = client
        print("-" * 72)
        print("Connection received from {}.".format(address))

        while True: #keep listening for commands
            try:
                data = connection.recv(1024)
                if not data:
                    break

                command = data.decode(MSG_ENCODING)
                command = command.split(" ")
                print(command)
                return_message = ""

                if command[0] == "getdir":
                    print("recieved getdir command")
                    return_message = Server.get_directory()
                    pkt = return_message.encode(MSG_ENCODING)
                    connection.sendall(pkt)

                elif command[0] == "makeroom":
                    if len(command) == 4:
                        print("got command to make room: " + command[1] + " with addr: " + command[2] + " at port: " + command[3])
                        return_message = Server.add_room(command[1],command[2],command[3])
                    else: 
                        return_message = "wrong number of parameters for makeroom\n"
                    pkt = return_message.encode(MSG_ENCODING)
                    connection.sendall(pkt)

                elif command[0] == "deleteroom":
                    if len(command) == 2:
                        print("got command to delete room: " + command[1])
                        return_message = Server.delete_room(command[1])
                    else:
                        return_message = "wrong number of parameters for delete room\n"
                    pkt = return_message.encode(MSG_ENCODING)
                    connection.sendall(pkt)

                else:
                    print("invalid command recieved: " + command)

            except Exception as e:
                print("Error:", e)
                break


    def load_from_file():
        filename = "server_data.txt"
        file_data = []

        with open(filename, 'r') as file:
            if os.path.getsize(filename) > 0:
                for line in file:
                        line_data = line.split()
                        file_data.append([line_data[0],line_data[1],line_data[2]])

        return file_data
    
    def get_directory():
        file_data = Server.load_from_file()
        message = "Directory List \n------------------- \n"

        for line in file_data:
            message = message + "Room name: " + line[0] + ", Address: " + line[1] + ", Port: " + line[2] + "\n"

        return message + "\n"
    
    def add_room(name, address, port):

        #check if multicast address is valid
        if not Server.addr_check(address):
            return "Address not a valid multicast address\n"
        
        data = Server.load_from_file()

        #check if name or addr/port combo already in use
        for item in data:
            if item[0] == name:
                return "Chatroom of that name already exists\n"
            elif item[1] == address:
                if item[2] == port:
                    return "Address/Port combination is already in use\n"
        
        #append data to list
        data.append([name,address,port])
        Server.write_to_file(data)
        return "Chatroom successfully created\n"

    def addr_check(address):
        addr_check = address.split('.')

        if len(addr_check) != 4:
            return False
        elif addr_check[0] != "239":
            return False
        else:
            if 0 <= int(addr_check[1]) <=255 and 0 <= int(addr_check[2]) <=255 and 0 <= int(addr_check[3]) <=255:
                return True
    
    def delete_room(room_name):
        message = "Room Not Found\n"
        data = Server.load_from_file()
        for i in range(len(data)):
            if data[i][0] == room_name:
                data.pop(i)
                message = "room deleted\n"
                break
        Server.write_to_file(data)
        return message

    def write_to_file(data):
        filename = "server_data.txt"

        with open(filename, 'w') as file:
            for line in data:
                file.write(line[0] + " " + line[1] + " " + line[2] + "\n")
                    
    def server_main(self):
        self.create_listen_socket()
        self.process_connections_forever()



def main():
    Server()

main()
