import socket
import json
import threading
import select
import sys

# Server Addresses
serverAAddressPort = ("127.0.0.1", 1000)
serverBAddressPort = ("127.0.0.1", 1001)
bufferSize = 1024
currentServerAddressPort = serverAAddressPort

# Client info
client_name = "Khendek"
ip_address = "127.0.0.1"
socket_number = 2000
subjects_of_interest = []

# Create a UDP socket at client side
UDPClientSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
UDPClientSocket.bind((ip_address, socket_number))


def listen_for_messages(stop_event):
    global currentServerAddressPort
    print("starting message")
    # Wait for messages
    while not stop_event.is_set():
        read, write, errors = select.select([UDPClientSocket], [], [], 1)
        for read_socket in read:
            server_message = UDPClientSocket.recvfrom(bufferSize)
            print(str(server_message))

            if "CHANGE-SERVER" in str(server_message[0]):
                server_info = str(server_message).split(',')
                if server_info[0] == serverAAddressPort[0] and server_info[1] == serverAAddressPort[1]:
                    currentServerAddressPort = serverAAddressPort
                    print("Setting current server to server A")
                else:
                    currentServerAddressPort = serverBAddressPort
                    print("Setting current server to server B")


if __name__ == "__main__":
    # TODO: 1) change how rq numbers are generated
    # TODO: 2) client does not get answer from the server if not registered, is this ok?
    while True:
        # Get user input
        print("What would you like to do today?")
        print("0: Register to the server\n1: De-register from server\n2: Update ip/socket"
              "\n3: Update subjects of interest\n4: Publish subjects of interest")
        user_action = input()

        if user_action == '0':
            # Send register request to both servers
            registerMessage = {"request_type": "REGISTER", "rq_number": 1, "name": client_name, "ip": ip_address,
                               "socket": str(socket_number)}
            registerMessageJson = json.dumps(registerMessage)
            registerMessageBytes = str.encode(registerMessageJson)

            UDPClientSocket.sendto(registerMessageBytes, serverAAddressPort)
            UDPClientSocket.sendto(registerMessageBytes, serverBAddressPort)

            msg = UDPClientSocket.recvfrom(bufferSize)
            if "REGISTERED" in str(msg):
                # Start listening to the server
                t_message_event = threading.Event()
                t_message = threading.Thread(target=listen_for_messages, args=(t_message_event,))
                t_message.start()

            print(msg)

        elif user_action == '1':
            print("Starting De-registering")

            # Create de-register message
            de_register_message = {"request_type": "DE-REGISTER", "rq_number": 1, "name": client_name}
            de_register_message_json = json.dumps(de_register_message)
            de_register_message_bytes = str.encode(de_register_message_json)

            # Send message to current active server
            UDPClientSocket.sendto(de_register_message_bytes, currentServerAddressPort)

            # Stop the listening thread
            try:
                t_message_event.set()
                t_message.join()
                t_message_event.clear()
            except NameError:
                print("Client wasn't registered, nothing to de-register")
            else:
                print("Client was de-registered")

        elif user_action == '2':
            print("Starting ip/socket update")

            # Get new ip/socket info
            print("Please enter your new ip")
            new_ip = input()

            print("Please enter your new socket")
            new_socket = input()

            # Update ip/socket info
            ip_address = str(new_ip)
            socket_number = int(new_socket)
            try:
                # Stop the listening thread
                t_message_event.set()
                t_message.join()
                t_message_event.clear()

                # Starting new listening thread with new socket
                UDPClientSocket.close()
                UDPClientSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
                UDPClientSocket.bind((ip_address, socket_number))
                t_message = threading.Thread(target=listen_for_messages, args=(t_message_event,))
                t_message.start()

                # Create update message
                update_message = {"request_type": "UPDATE", "rq_number": 1, "name": client_name,
                                  "ip": ip_address, "socket": socket_number}
                update_message_json = json.dumps(update_message)
                update_message_bytes = str.encode(update_message_json)

                # Send message to current active server
                UDPClientSocket.sendto(update_message_bytes, currentServerAddressPort)
            except NameError:
                print("Client wasn't registered, cannot update ip/socket")
            else:
                print("Client was de-registered")

        elif user_action == '3':
            print("Starting subjects of interest update")
            # TODO: make this user input
            subj = ["AI", "Cloud"]
            # Create subjects message
            subjects_message = {"request_type": "SUBJECTS", "rq_number": 1, "name": client_name, "subjects": subj}
            subjects_message_json = json.dumps(subjects_message)
            subjects_message_bytes = str.encode(subjects_message_json)

            try:
                t_message_event.clear()
                # Send message to current active server
                UDPClientSocket.sendto(subjects_message_bytes, currentServerAddressPort)
            except NameError:
                print("Client wasn't registered, cannot update subjects")

        elif user_action == '4':
            # TODO: add client subject of interest publish
            print("Starting subjects of interest publish")
        else:
            print("Invalid input. Please try again")
