import socket
import threading
import sys
import struct

MSG_ENCODING = "utf-8"

class Client:

    HOSTNAME = "127.0.0.1"
    room_array = list()

    def __init__(self):
        self.connected_tcp = False
        self.connected_chat = False
        self.chat_name = "Unknown"
        self.client_main()
        #self.room_array = list()

    def client_main(self):
        print("starting")
        while True:

            if self.connected_tcp == False:

                if self.connected_chat == False: 
                    command = input("Not Connected, Please enter your command: ")
                    command = command.split(" ")

                    if command[0] == "connect":
                        self.get_socket_tcp()
                        self.connect_to_server("192.168.0.124", 50000)

                    elif command[0] == "name":
                        if len(command) > 1:
                            self.chat_name = command[1]
                            print("Name = ", self.chat_name)
                    
                    elif command[0] == "chat":
                        print("Recognized chat command")
                        if len(command) > 1:
                            print("about to run multicast command")
                            #room = command_split[1]
                            for room in Client.room_array:
                                if room[0] == command[1]:
                                    self.multicast_chat(room[0],room[1],int(room[2]))
                            '''
                            if room in self.chat_room:
                                ip, port = self.chat_room[room]
                                self.multicast_chat(room, ip, int(port))
                            else:
                                print("Not in Room, Please Join it First")'''

                    

            elif self.connected_tcp == True:
                command = input("Connected to server, please enter your command: ")
                command_split = command.split(" ")

                if command_split[0] == "makeroom" or command_split[0] == "deleteroom":
                    pkt = command.encode(MSG_ENCODING)
                    self.socket.sendall(pkt)

                    #print the recieved message from the server
                    data = self.socket.recv(1024)
                    if not data:
                        self.disconnect_from_server()
                        break
                    
                    print(data.decode(errors='ignore'), end='')
                
                if command_split[0] == "getdir":
                    pkt = command.encode(MSG_ENCODING)
                    self.socket.sendall(pkt)

                    #print the recieved message from the server
                    data = self.socket.recv(1024)
                    if not data:
                        self.disconnect_from_server()
                        break
                    print(data.decode(errors='ignore'), end='')
                    directory_data = data.decode(errors='ignore')
                    directory_array = directory_data.strip().split("\n")
                    for item in directory_array:
                        Client.room_array.append(item.split(" "))
                    print(Client.room_array)

                elif command_split[0] == "bye":
                    self.disconnect_from_server()

                elif command_split[0] == "name":
                    if len(command_split) > 1:
                        self.chat_name = command_split[1]
                        print("Change Name = ", self.chat_name)

        

    def multicast_chat(self, room, multicast_ip, port):
        print("Entering multicast chat room:", room)
        print("Type messages, 'exit' to leave")

        self.connected_chat = True

        try:
            self.chat_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
            self.chat_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.chat_socket.bind(('', port))

            mreq = struct.pack(
                "4s4s",
                socket.inet_aton(multicast_ip),
                socket.inet_aton("0.0.0.0"),
            )

            self.chat_socket.setsockopt(
                socket.IPPROTO_IP,
                socket.IP_ADD_MEMBERSHIP,
                mreq
            )
            self.chat_socket.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)

        except Exception as msg:
            print("Multicast chat error:", msg)
            exit()

        recv_thread = threading.Thread(target=self.message_recieve)
        recv_thread.daemon = True
        recv_thread.start()

        while self.connected_chat:
            message = input()

            if message.lower() == "exit" or message == '\x1d':
                self.connected_chat = False
                break

            full_message = self.chat_name + ": " + message
            self.chat_socket.sendto(full_message.encode(MSG_ENCODING), (multicast_ip, port))

        self.chat_socket.close()
        print("Exited chat mode")


    def message_recieve(self):
        while self.connected_chat:
            try:
                data, addr = self.chat_socket.recvfrom(1024)
                print("\n" + data.decode())
            except:
                break

    def get_socket_tcp(self):
        print("getting socket")
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            print("got that socket")
        except Exception as msg:
            print(msg)
            exit()
    
    def connect_to_server(self,hostname,port):
        print("Entering Connect to server")
        try:
            self.socket.connect((hostname, port))
            print("connected to server")
            self.connected_tcp = True
        except Exception as msg:
            print(msg)
            exit()

    def disconnect_from_server(self):
        print("Disconnecting from server")
        self.connected_tcp = False
        self.socket.close()

def main():
    Client()
main()
        
