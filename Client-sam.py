import socket

MSG_ENCODING = "utf-8"

class Client:

    HOSTNAME = "127.0.0.1"

    def __init__(self):
        self.connected_tcp = False
        self.connected_chat = False
        self.chat_name = ""
        self.chat_room = ""
        self.client_main()

    def client_main(self):
        print("starting")
        while True:

            if self.connected_tcp == False:

                if self.connected_chat == False: 
                    command = input("Not Connected, Please enter your command: ")
                    command = command.split(" ")

                    if command[0] == "connect":
                        self.get_socket_tcp()
                        self.connect_to_server("127.0.0.1", 50000)

                    '''
                    ========================================================================================================================================================================================================
                    elif command[0] == "chat":

                        #logic to connect to the chatroom multicast (you may need to prompt the server for the address) 

                    elif command[0] == "name":

                        #logic to change name for the chatroom 
                else:
                
                    #logic for the chat multicast messages
                    ========================================================================================================================================================================================================
                    '''

            elif self.connected_tcp == True:
                command = input("Connected to server, please enter your command: ")
                command_split = command.split(" ")
                
                if command_split[0] == "getdir" or command_split[0] == "makeroom" or command_split[0] == "deleteroom":
                    pkt = command.encode(MSG_ENCODING)
                    self.socket.sendall(pkt)

                    #print the recieved message from the server
                    data = self.socket.recv(1024)
                    if not data:
                        break
                    print(data.decode(errors='ignore'), end='')

                elif command_split[0] == "bye":
                    self.disconnect_from_server()

                



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
        self.socket.close()
        self.connected_tcp = False

def main():
    Client()
main()
        
