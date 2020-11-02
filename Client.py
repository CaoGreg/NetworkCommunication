import socket
import json
import threading

# Server Addresses
serverAAddressPort = ("127.0.0.1", 1000)
serverBAddressPort = ("127.0.0.1", 1001)
bufferSize = 1024
currentServerAddressPort = serverAAddressPort

# Client info
client_name = "Khendek"
ip_address = "127.0.0.1"
socket_number = "22"
subjects_of_interest = []

# Create a UDP socket at client side
UDPClientSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)


def listen_for_messages():
    global currentServerAddressPort

    # Wait for messages
    server_message = UDPClientSocket.recvfrom(bufferSize)
    print(server_message[0])

    if "CHANGE-SERVER" in str(server_message[0]):
        server_info = str(server_message).split(',')
        if server_info[0] == serverAAddressPort[0] and server_info[1] == serverAAddressPort[1]:
            currentServerAddressPort = serverAAddressPort
            print("Setting current server to server A")
        else:
            currentServerAddressPort = serverBAddressPort
            print("Setting current server to server B")


if __name__ == "__main__":
    # Send register request to both servers
    registerMessage = {"request_type": "REGISTER", "rq_number": 1, "name": client_name, "ip": ip_address,
                       "socket": socket_number}
    registerMessageJson = json.dumps(registerMessage)
    registerMessageBytes = str.encode(registerMessageJson)

    UDPClientSocket.sendto(registerMessageBytes, serverAAddressPort)
    UDPClientSocket.sendto(registerMessageBytes, serverBAddressPort)

    msgFromServer = UDPClientSocket.recvfrom(bufferSize)
    registration_msg = "Message from Server {}".format(msgFromServer[0])
    print(registration_msg)

    t_message = threading.Thread(target=listen_for_messages, args=())
    t_message.start()

    # TODO: 1) change how rq numbers are generated

    if "REGISTERED" in registration_msg:
        print("Client successfully registered")
        while True:
            # Get user input
            print("What would you like to do today?")
            print("1: De-register from server\n2: Update ip/socket\n3: Update subjects of interest"
                  "\n4: Publish subjects of interest")
            user_action = input()

            if user_action == '1':
                print("Starting De-registering")

                # Create de-register message
                de_register_message = {"request_type": "DE-REGISTER", "rq_number": 1, "name": client_name}
                de_register_message_json = json.dumps(de_register_message)
                de_register_message_bytes = str.encode(de_register_message_json)

                # Send message to current active server
                UDPClientSocket.sendto(de_register_message_bytes, currentServerAddressPort)
                print("Client was de-registered, exiting.")
                break

            elif user_action == '2':
                # TODO: add client socket/ip update
                print("Starting ip/socket update")
            elif user_action == '3':
                # TODO: add client subject of interest update
                print("Starting subjects of interest update")
            elif user_action == '4':
                # TODO: add client subject of interest publish
                print("Starting subjects of interest publish")
            else:
                print("Invalid input. Please try again")
